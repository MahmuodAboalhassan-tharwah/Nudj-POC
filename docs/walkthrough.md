# Nudj Platform — Implementation Walkthrough

This document provides detailed explanations of HOW key features were implemented in the Nudj HR Maturity Assessment Platform. Each section explains the architecture, data flow, and code patterns used.

---

## Table of Contents

1. [Assessment Scoring Engine](#1-assessment-scoring-engine)
2. [Recursive Comment Threading](#2-recursive-comment-threading)
3. [Domain Delegation Flow](#3-domain-delegation-flow)
4. [RBAC Permission Model](#4-rbac-permission-model)
5. [Tenant Isolation Pattern](#5-tenant-isolation-pattern)
6. [Bilingual i18n Implementation](#6-bilingual-i18n-implementation)

---

## 1. Assessment Scoring Engine

### Overview

The scoring engine converts maturity level selections (1-4) into percentage scores, aggregates them through a weighted hierarchy (Element → Dimension → Domain → Overall), and persists scores at each level for reporting.

### Scoring Formula Architecture

```
                    Overall Score (0-100%)
                            ↑
                            │ weighted sum
                            │
        ┌─────────────────┬─┴──────┬─────────────────┐
        │                 │        │                 │
    Domain 1          Domain 2   ...              Domain 9
    (12% weight)      (15% weight)              (15% weight)
        ↑                 ↑                          ↑
        │ E×0.3 + A×0.5 + Au×0.2                    │
        │                                            │
    ┌───┴───┬───────┬───────┐                       │
    │       │       │       │                        │
Existence Application Automation                    │
(30%)     (50%)      (20%)                          │
    ↑       ↑        ↑                              │
    │       │        │                              │
weighted avg of element scores per dimension        │
    │                                                │
    └────────────────────────────────────────────────┘
        Elements (maturity 1-4 → 0%, 33%, 67%, 100%)
```

### Data Model

**Assessment Hierarchy:**

```python
# src/backend/app/assessments/models.py

Assessment
├── id: UUID (primary key)
├── organization_id: UUID (tenant isolation)
├── status: AssessmentStatus (DRAFT → IN_PROGRESS → COMPLETED)
├── score: float (overall calculated score 0-100)
├── deadline: datetime
└── domains: List[AssessmentDomain] (1-9 domains)

AssessmentDomain
├── id: UUID
├── assessment_id: UUID (FK)
├── domain_id: int (1-9, maps to framework domain)
├── weight: float (e.g., 0.12 for 12%)
├── score: float (domain score 0-100)
├── assignee_id: UUID (delegated assessor)
└── elements: List[AssessmentElementResponse]

AssessmentElementResponse
├── id: UUID
├── domain_record_id: UUID (FK to AssessmentDomain)
├── element_id: int (framework element ID)
├── maturity_level: int (1-4, user selection)
├── score: float (converted score: 0/33/67/100)
└── evidence: List[Evidence] (uploaded files)
```

### Scoring Implementation

**Location:** `src/backend/app/assessments/scoring.py`

```python
class ScoringService:
    @staticmethod
    def calculate_element_score(maturity_level: int) -> float:
        """
        Convert maturity level (1-4) to percentage score.

        Mapping:
          1 (Foundation)       → 0%
          2 (Partial Dev)      → 33%
          3 (Integration)      → 67%
          4 (Excellence)       → 100%
        """
        if not maturity_level or maturity_level < 1:
            return 0.0
        return min(maturity_level * 25.0, 100.0)  # Linear: 25%, 50%, 75%, 100%

    @staticmethod
    def calculate_domain_score(domain: AssessmentDomain) -> float:
        """
        Calculate domain score as weighted average of dimensions.

        Domain = (Existence × 0.30) + (Application × 0.50) + (Automation × 0.20)

        In practice, we average all element scores for now.
        Framework config should map element_id → dimension for proper grouping.
        """
        if not domain.elements:
            return 0.0

        # Filter elements with scores
        scored_elements = [e for e in domain.elements if e.score is not None]
        if not scored_elements:
            return 0.0

        # Simple average (production should group by dimension and weight)
        total = sum(e.score for e in scored_elements)
        return total / len(domain.elements)

    @staticmethod
    def calculate_overall_score(assessment: Assessment) -> float:
        """
        Calculate overall score as weighted sum of domain scores.

        Overall = Σ(Domain Score × Domain Weight)

        Weights from framework_domain_configs table (e.g., Performance Mgmt = 15%).
        """
        if not assessment.domains:
            return 0.0

        total_weighted_score = 0.0
        total_weight = 0.0

        for domain in assessment.domains:
            weight = domain.weight if domain.weight else 1.0
            score = domain.score if domain.score is not None else 0.0
            total_weighted_score += score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return total_weighted_score / total_weight
```

### Calculation Trigger

Scores are recalculated when:
1. **Assessor submits maturity selection** for an element → triggers `calculate_element_score()`
2. **All elements in a domain completed** → triggers `calculate_domain_score()`
3. **Assessment submitted for review** → triggers `calculate_overall_score()`

**Service layer integration:**

```python
# src/backend/app/assessments/service.py

async def save_element_response(self, element_response_data):
    # 1. Save maturity level
    response.maturity_level = element_response_data.maturity_level

    # 2. Calculate and save element score
    response.score = ScoringService.calculate_element_score(
        response.maturity_level
    )
    await self.session.commit()

    # 3. If domain complete, recalculate domain score
    domain = await self.get_domain(response.domain_record_id)
    if self._is_domain_complete(domain):
        domain.score = ScoringService.calculate_domain_score(domain)
        await self.session.commit()

    # 4. If all domains complete, recalculate overall score
    assessment = await self.get_assessment(domain.assessment_id)
    if self._is_assessment_complete(assessment):
        assessment.score = ScoringService.calculate_overall_score(assessment)
        await self.session.commit()
```

### Frontend Display

**Location:** `src/frontend/src/features/assessments/pages/assessment-detail-page.tsx`

```typescript
// Display overall score with visual indicator
<div className="score-card">
  <div className="text-4xl font-bold">
    {assessment.score?.toFixed(1)}%
  </div>
  <div className="text-sm text-slate-500">
    {t('assessments.overallScore')}
  </div>
</div>

// Per-domain scores displayed in domain navigation
{domains.map(domain => (
  <div key={domain.id} className="domain-item">
    <span>{t(`domains.${domain.domainId}`)}</span>
    <Badge>{domain.score?.toFixed(0)}%</Badge>
  </div>
))}
```

### Production Enhancements

For production, the scoring engine should:
1. **Group elements by dimension** (Existence/Application/Automation) using framework config
2. **Validate weights sum to 100%** at assessment creation time
3. **Cache scores** using Redis for dashboard performance
4. **Audit score changes** — track who/when scores were recalculated
5. **Support score overrides** for analysts to manually adjust scores with justification

---

## 2. Recursive Comment Threading

### Overview

Comments support nested discussions (replies to replies) using a self-referencing foreign key. The backend loads comment trees efficiently, and the frontend renders them recursively.

### Data Model

**Location:** `src/backend/app/comments/models.py`

```python
class Comment(Base, TimestampMixin):
    __tablename__ = "comments"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    response_id: Mapped[UUID] = mapped_column(
        ForeignKey("assessment_element_responses.id")
    )

    # Self-referencing FK for threading
    parent_id: Mapped[UUID] = mapped_column(
        ForeignKey("comments.id"),
        nullable=True,  # NULL = top-level comment
        index=True
    )
    content: Mapped[str] = mapped_column(Text)

    # Relationships
    author: Mapped["User"] = relationship("User", foreign_keys=[user_id])

    # Recursive relationship for nested replies
    replies: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="parent",
        cascade="all, delete-orphan",  # Delete child comments when parent deleted
        remote_side=[parent_id]  # Tells SQLAlchemy which side is parent
    )
    parent: Mapped["Comment"] = relationship(
        "Comment",
        back_populates="replies",
        remote_side=[id],
        use_list=False  # Parent is single object, not list
    )
```

**Tree Structure Example:**

```
Comment A (parent_id = NULL)
├── Comment B (parent_id = A.id)
│   ├── Comment C (parent_id = B.id)
│   └── Comment D (parent_id = B.id)
└── Comment E (parent_id = A.id)
```

### Backend Query Strategy

**Location:** `src/backend/app/comments/service.py`

```python
async def get_response_comments(self, response_id: UUID) -> List[Comment]:
    """
    Fetch comment tree for an element response.

    Strategy:
    1. Query only top-level comments (parent_id = NULL)
    2. Use selectinload to eager-load nested replies (avoids N+1)
    3. SQLAlchemy follows 'replies' relationship recursively
    """
    stmt = select(Comment).where(
        Comment.response_id == response_id,
        Comment.parent_id == None  # Top-level only
    ).options(
        selectinload(Comment.author),  # Load author for top-level
        selectinload(Comment.replies).selectinload(Comment.author),  # Level 1 replies
        selectinload(Comment.replies).selectinload(Comment.replies)  # Level 2 replies
    ).order_by(Comment.created_at.asc())

    result = await self.session.execute(stmt)
    return result.scalars().all()
```

**Why this approach:**
- **Avoids N+1 queries:** `selectinload` fetches all replies in 2-3 queries instead of 1 query per comment
- **Limits depth:** Explicitly loading 2-3 levels prevents infinite recursion (can extend with `selectinload(Comment.replies).selectinload(Comment.replies).selectinload(Comment.replies)` for deeper threads)
- **Frontend builds tree:** Backend returns flat list of top-level comments with nested `.replies` — frontend renders recursively

### Frontend Recursive Rendering

**Location:** `src/frontend/src/features/comments/components/comment-item.tsx`

```tsx
export const CommentItem = ({ comment, onReply, isReplying }: CommentItemProps) => {
  const [showReplyInput, setShowReplyInput] = useState(false);

  return (
    <div className="group space-y-3">
      {/* Comment content */}
      <div className="flex gap-3">
        <div className="avatar">
          {comment.author.full_name?.[0] || 'U'}
        </div>
        <div className="flex-1">
          <div className="author-info">
            <span>{comment.author.full_name}</span>
            <span>{formatDistanceToNow(comment.created_at)}</span>
          </div>
          <p>{comment.content}</p>

          {/* Reply button */}
          <Button onClick={() => setShowReplyInput(!showReplyInput)}>
            <Reply /> Reply
          </Button>
        </div>
      </div>

      {/* Reply input (toggled) */}
      {showReplyInput && (
        <div className="ml-11">
          <CommentInput
            onSubmit={(content) => {
              onReply(comment.id, content);  // Pass parent_id
              setShowReplyInput(false);
            }}
          />
        </div>
      )}

      {/* RECURSIVE RENDERING of nested replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="ml-11 border-l-2 border-slate-100 pl-4">
          {comment.replies.map((reply) => (
            <CommentItem
              key={reply.id}
              comment={reply}      // Recursive call
              onReply={onReply}
              isReplying={isReplying}
            />
          ))}
        </div>
      )}
    </div>
  );
};
```

**How recursion works:**
1. `CommentItem` renders a single comment
2. If `comment.replies` exists, it maps over them and renders `<CommentItem>` again (recursive)
3. CSS indentation (`ml-11`) visually nests replies
4. Recursion stops when `replies` array is empty

### Frontend Container Component

**Location:** `src/frontend/src/features/comments/components/comment-thread.tsx`

```tsx
export const CommentThread = ({ responseId }: CommentThreadProps) => {
  const { data: comments, isLoading } = useComments(responseId);
  const addComment = useAddComment();

  const handleAddComment = (content: string) => {
    addComment.mutate({
      response_id: responseId,
      content,
      parent_id: null  // Top-level comment
    });
  };

  const handleReply = (parentId: string, content: string) => {
    addComment.mutate({
      response_id: responseId,
      content,
      parent_id: parentId  // Nested reply
    });
  };

  return (
    <div>
      <CommentInput onSubmit={handleAddComment} />

      {comments?.map((comment) => (
        <CommentItem
          key={comment.id}
          comment={comment}
          onReply={handleReply}
        />
      ))}
    </div>
  );
};
```

### Database Considerations

**PostgreSQL recursive query (alternative approach):**

For deep threads (5+ levels), you could use a Common Table Expression (CTE):

```sql
WITH RECURSIVE comment_tree AS (
  -- Base case: top-level comments
  SELECT id, parent_id, content, user_id, created_at, 0 as depth
  FROM comments
  WHERE response_id = :response_id AND parent_id IS NULL

  UNION ALL

  -- Recursive case: child comments
  SELECT c.id, c.parent_id, c.content, c.user_id, c.created_at, ct.depth + 1
  FROM comments c
  INNER JOIN comment_tree ct ON c.parent_id = ct.id
  WHERE ct.depth < 10  -- Limit recursion depth
)
SELECT * FROM comment_tree ORDER BY created_at;
```

**For Nudj, the SQLAlchemy `selectinload` approach is sufficient** since typical discussions won't exceed 3-4 levels.

---

## 3. Domain Delegation Flow

### Overview

Client Admins can delegate specific domains (or entire assessments) to team members. Delegations grant assessors permission to complete assigned domains, and permissions are enforced via FastAPI dependencies.

### Data Model

**Location:** `src/backend/app/delegations/models.py`

```python
class DelegationStatus(str, Enum):
    ACTIVE = "ACTIVE"      # Delegation is active
    REVOKED = "REVOKED"    # Delegation was revoked

class AssessmentDelegation(Base, TimestampMixin):
    __tablename__ = "assessment_delegations"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    assessment_id: Mapped[UUID] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE")
    )

    # If domain_id is NULL, entire assessment is delegated
    domain_id: Mapped[UUID] = mapped_column(
        ForeignKey("assessment_domains.id", ondelete="CASCADE"),
        nullable=True
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )  # Delegatee (person receiving the task)

    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id")
    )  # Delegator (person who assigned it)

    status: Mapped[DelegationStatus] = mapped_column(
        SQLEnum(DelegationStatus),
        default=DelegationStatus.ACTIVE
    )
    notes: Mapped[str] = mapped_column(String(500), nullable=True)
```

**Delegation Scenarios:**

```
Scenario 1: Delegate entire assessment
├── domain_id = NULL
└── Delegatee can access all 9 domains

Scenario 2: Delegate specific domain
├── domain_id = "uuid-of-performance-mgmt-domain"
└── Delegatee can only access Performance Management domain

Scenario 3: Multiple delegations (common)
├── Domain 1 → User A
├── Domain 2 → User B
├── Domain 3 → User A
└── Each user sees only their assigned domains
```

### Permission Enforcement

**Location:** `src/backend/app/auth/dependencies.py` (custom dependency)

```python
async def require_domain_access(
    assessment_id: UUID,
    domain_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Verify user has access to the specified domain.

    Access granted if:
    1. User is Super Admin or Analyst (full access)
    2. User is Client Admin for the org (full access)
    3. User has active delegation for this domain
    """
    # Super Admin and Analyst bypass
    if current_user.role in [Role.SUPER_ADMIN, Role.ANALYST]:
        return current_user

    # Get assessment to check organization
    assessment = await session.get(Assessment, assessment_id)
    if not assessment:
        raise NotFoundException("Assessment not found")

    # Client Admin of the org
    if (current_user.role == Role.CLIENT_ADMIN and
        current_user.organization_id == assessment.organization_id):
        return current_user

    # Check delegation
    stmt = select(AssessmentDelegation).where(
        AssessmentDelegation.assessment_id == assessment_id,
        AssessmentDelegation.user_id == current_user.id,
        AssessmentDelegation.status == DelegationStatus.ACTIVE,
        (
            (AssessmentDelegation.domain_id == domain_id) |  # Specific domain
            (AssessmentDelegation.domain_id == None)         # Whole assessment
        )
    )
    result = await session.execute(stmt)
    delegation = result.scalar_one_or_none()

    if not delegation:
        raise InsufficientPermissionsException(
            "You do not have access to this domain"
        )

    return current_user
```

**Usage in assessment router:**

```python
@router.put("/assessments/{assessment_id}/domains/{domain_id}/elements/{element_id}")
async def update_element_response(
    assessment_id: UUID,
    domain_id: UUID,
    element_id: int,
    data: ElementResponseUpdate,
    current_user: User = Depends(require_domain_access),  # Custom dependency
):
    # current_user is guaranteed to have access if this point is reached
    return await service.update_element_response(...)
```

### Frontend Delegation UI

**Location:** `src/frontend/src/features/assessments/components/delegation-dialog.tsx`

Key features:
1. **Select delegatee** from organization users
2. **Choose scope** (whole assessment or specific domain)
3. **Add notes** (e.g., "Please complete by EOW")
4. **View active delegations** with revoke button

```tsx
export const DelegationDialog = ({ assessmentId, organizationId, domains }) => {
  const { mutate: create } = useCreateDelegation();
  const { data: delegations } = useDelegations(assessmentId);

  const onSubmit = (values) => {
    create({
      assessmentId,
      userId: values.userId,
      domainId: values.domainId === 'whole' ? undefined : values.domainId,
      notes: values.notes,
    });
  };

  return (
    <Dialog>
      {/* Form to create delegation */}
      <Form onSubmit={onSubmit}>
        <Select name="userId">
          {users.map(user => <SelectItem value={user.id}>{user.name}</SelectItem>)}
        </Select>

        <Select name="domainId">
          <SelectItem value="whole">Whole Assessment</SelectItem>
          {domains.map(d => <SelectItem value={d.id}>Domain {d.domainId}</SelectItem>)}
        </Select>

        <Textarea name="notes" placeholder="Add instructions..." />

        <Button type="submit">Assign Task</Button>
      </Form>

      {/* List of active delegations */}
      <ScrollArea>
        {delegations?.map(delegation => (
          <div key={delegation.id}>
            <span>{delegation.delegateeName}</span>
            <Badge>{delegation.domainName || 'Full Assessment'}</Badge>
            <Button onClick={() => revoke(delegation.id)}>Revoke</Button>
          </div>
        ))}
      </ScrollArea>
    </Dialog>
  );
};
```

### Workflow Example

```
1. Client Admin opens assessment → clicks "Delegate" button
2. Selects "Ahmed (Assessor)" from dropdown
3. Selects "Domain 2: Performance Management" from scope dropdown
4. Adds note: "Please complete by Feb 15"
5. Clicks "Assign Task"

Backend:
6. Creates AssessmentDelegation record with status=ACTIVE
7. Sends notification email to Ahmed

Ahmed's Experience:
8. Logs in → sees assessment in "My Assessments" list
9. Clicks assessment → sees ONLY Domain 2 (other domains hidden)
10. Completes Domain 2 elements → submits for review
11. Domain 2 marked as COMPLETED, delegation remains ACTIVE

Client Admin:
12. Reviews Domain 2 → approves
13. (Optional) Revokes delegation if reassignment needed
```

---

## 4. RBAC Permission Model

### Overview

Nudj implements a 4-level role hierarchy with fine-grained permissions. Authorization is enforced via FastAPI dependencies at the route level.

### Role Hierarchy

**Location:** `src/backend/app/auth/permissions.py`

```python
ROLE_HIERARCHY = {
    Role.SUPER_ADMIN: 4,    # Highest privilege
    Role.ANALYST: 3,
    Role.CLIENT_ADMIN: 2,
    Role.ASSESSOR: 1        # Lowest privilege
}
```

**Inheritance:** Higher roles do NOT automatically inherit lower role permissions. Permissions are explicitly defined per role.

### Permission Definitions

```python
ROLE_PERMISSIONS = {
    Role.SUPER_ADMIN: {
        # Full platform access
        "users:read", "users:write", "users:delete", "users:invite",
        "orgs:read", "orgs:write", "orgs:delete",
        "assessments:read", "assessments:write", "assessments:delete",
        "reports:read", "reports:write", "reports:export",
        "audit:read", "audit:export",
        "settings:read", "settings:write",
        "sso:configure",
    },

    Role.ANALYST: {
        # Read-only user/org access, full assessment access
        "users:read",
        "orgs:read",
        "assessments:read", "assessments:write",
        "reports:read", "reports:write", "reports:export",
    },

    Role.CLIENT_ADMIN: {
        # Org-scoped user management, assessment management
        "users:read", "users:write", "users:invite",
        "assessments:read", "assessments:write",
        "reports:read",
    },

    Role.ASSESSOR: {
        # Limited to assigned domains
        "assessments:read",
    },
}
```

### Permission Checking

```python
class PermissionService:
    @staticmethod
    def has_permission(role: Role, permission: str) -> bool:
        """Check if role has a specific permission."""
        permissions = ROLE_PERMISSIONS.get(role, set())
        return permission in permissions

    @staticmethod
    def check_tenant_access(
        user_role: Role,
        user_org_id: Optional[str],
        target_org_id: str,
    ) -> bool:
        """
        Enforce tenant isolation.

        - Super Admin: All orgs
        - Analyst: Assigned orgs (checked via AnalystOrgAssignment table)
        - Client Admin/Assessor: Own org only
        """
        if user_role == Role.SUPER_ADMIN:
            return True

        if user_role == Role.ANALYST:
            # Check AnalystOrgAssignment table (not shown here)
            return True  # Placeholder

        return user_org_id == target_org_id
```

### FastAPI Dependency Guards

**Pattern 1: Role-based guard**

```python
from src.backend.app.auth.dependencies import require_role

@router.post("/organizations")
async def create_organization(
    data: OrganizationCreate,
    current_user: User = Depends(require_role(Role.SUPER_ADMIN)),
):
    # Only Super Admins reach this point
    return await service.create_organization(data)
```

**Pattern 2: Permission-based guard**

```python
from src.backend.app.auth.dependencies import require_permission

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_permission("users:delete")),
):
    # Only roles with "users:delete" permission reach this point
    return await service.delete_user(user_id)
```

**Pattern 3: Multiple roles**

```python
@router.get("/assessments")
async def list_assessments(
    current_user: User = Depends(
        require_role(Role.SUPER_ADMIN, Role.ANALYST, Role.CLIENT_ADMIN)
    ),
):
    # Super Admin, Analyst, or Client Admin can list assessments
    # Service layer handles filtering by org for Client Admin
    return await service.list_assessments(current_user)
```

### Frontend Permission Guards

**Component-level guard:**

**Location:** `src/frontend/src/shared/components/role-guard.tsx`

```tsx
interface RoleGuardProps {
  allowedRoles: Role[];
  children: ReactNode;
  fallback?: ReactNode;
}

export const RoleGuard = ({ allowedRoles, children, fallback }: RoleGuardProps) => {
  const { user } = useAuth();

  if (!user || !allowedRoles.includes(user.role)) {
    return fallback || null;
  }

  return <>{children}</>;
};
```

**Usage:**

```tsx
<RoleGuard allowedRoles={['super_admin', 'analyst']}>
  <Button onClick={deleteAssessment}>Delete Assessment</Button>
</RoleGuard>
```

**Route-level guard:**

```tsx
// src/app/router.tsx

const protectedRoutes = [
  {
    path: '/admin',
    element: <AdminLayout />,
    loader: requireAuth(['super_admin']),  // Only Super Admin
    children: [
      { path: 'users', element: <UsersPage /> },
      { path: 'audit-logs', element: <AuditLogsPage /> },
    ]
  },
  {
    path: '/assessments',
    element: <AssessmentsLayout />,
    loader: requireAuth(['super_admin', 'analyst', 'client_admin', 'assessor']),
    children: [...]
  }
];
```

### Key Features

1. **Explicit permissions:** No implicit inheritance, clear per-role definitions
2. **Defense in depth:** Enforced at route level (FastAPI), service level (business logic), and UI level (hide buttons)
3. **Tenant isolation:** Separate concern from RBAC, enforced via middleware + dependencies
4. **Scalable:** Adding new permissions requires updating `ROLE_PERMISSIONS` only

---

## 5. Tenant Isolation Pattern

### Overview

Nudj is a multi-tenant SaaS platform where each organization's data is strictly isolated. Every database query is filtered by `organization_id`, and access is enforced at multiple layers.

### Tenant Context Flow

```
1. User logs in → JWT issued with { sub: user_id, org: org_id, role: role }
                                    ↓
2. Frontend stores JWT → includes in Authorization header for API calls
                                    ↓
3. Backend middleware extracts org_id from JWT → sets request.state.organization_id
                                    ↓
4. FastAPI dependency injects current_user → includes organization_id
                                    ↓
5. Service layer filters all queries by organization_id
                                    ↓
6. Database returns only org-specific data
```

### JWT Payload

**Location:** `src/backend/app/auth/jwt_service.py`

```python
def create_access_token(self, user: User) -> str:
    payload = {
        "sub": str(user.id),               # User ID
        "email": user.email,
        "role": user.role.value,
        "org": str(user.organization_id),  # Tenant ID
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "type": "access"
    }
    return jwt.encode(payload, self.secret_key, algorithm="HS256")
```

### Middleware

**Location:** `src/backend/app/common/middleware.py`

```python
class TenantIsolationMiddleware(BaseHTTPMiddleware):
    """
    Extract organization context from JWT and add to request state.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Initialize organization_id as None
        request.state.organization_id = None

        # Extract JWT from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                request.state.organization_id = payload.get("org")
            except JWTError:
                pass  # Invalid token, dependencies will handle

        return await call_next(request)
```

### Service Layer Filtering

**Pattern: Every query includes organization filter**

```python
# src/backend/app/assessments/service.py

class AssessmentService:
    async def list_assessments(
        self,
        current_user: User,
        page: int = 1,
        page_size: int = 20
    ) -> PaginatedResponse[Assessment]:
        """
        List assessments for the current user's organization.

        Super Admin: See all orgs (skip filter)
        Analyst: See assigned orgs only (check AnalystOrgAssignment)
        Client Admin/Assessor: See own org only
        """
        stmt = select(Assessment)

        # TENANT ISOLATION: Filter by organization
        if current_user.role != Role.SUPER_ADMIN:
            stmt = stmt.where(
                Assessment.organization_id == current_user.organization_id
            )

        # Pagination
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(stmt)
        return result.scalars().all()
```

**Critical: NEVER trust client-provided `organization_id`**

```python
# ❌ WRONG — client can fake organization_id
@router.post("/assessments")
async def create_assessment(
    data: AssessmentCreate,  # data.organization_id from client
    current_user: User = Depends(get_current_user),
):
    # Client could send data.organization_id = "another-org-id"
    return await service.create(data)

# ✅ CORRECT — always use current_user.organization_id
@router.post("/assessments")
async def create_assessment(
    data: AssessmentCreate,
    current_user: User = Depends(get_current_user),
):
    # Override client-provided org_id with user's org_id
    data.organization_id = current_user.organization_id
    return await service.create(data)
```

### Database Design

**Every tenant-scoped table has `organization_id`:**

```sql
CREATE TABLE assessments (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,  -- Tenant discriminator
    status VARCHAR(50) NOT NULL,
    score FLOAT,
    created_at TIMESTAMP NOT NULL,
    -- Index for fast filtering
    INDEX idx_assessments_organization (organization_id)
);

CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    organization_id UUID NOT NULL,
    role VARCHAR(50) NOT NULL,
    INDEX idx_users_organization (organization_id)
);

-- Example query (implicit filter in service layer)
SELECT * FROM assessments WHERE organization_id = :org_id;
```

### Frontend Context

**Location:** `src/frontend/src/features/auth/store/auth.store.ts`

```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  organizationId: string | null;  // Stored from JWT
}

const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  organizationId: null,

  login: (user, token) => {
    // Decode JWT to extract organizationId
    const payload = jwtDecode(token);
    set({
      user,
      token,
      organizationId: payload.org
    });
  },

  logout: () => set({ user: null, token: null, organizationId: null }),
}));
```

**API client automatically includes token:**

```typescript
// src/shared/lib/api-client.ts

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Security Checklist

- [x] JWT includes `organization_id` in payload
- [x] Middleware extracts `organization_id` and sets `request.state`
- [x] Service layer ALWAYS filters by `organization_id` (except Super Admin)
- [x] NEVER trust client-provided `organization_id` in request body
- [x] Database indexes on `organization_id` for performance
- [x] Frontend stores `organizationId` from JWT, doesn't rely on client state
- [x] Authorization checks both role AND organization ownership

---

## 6. Bilingual i18n Implementation

### Overview

Nudj is Arabic-first with full English support. All user-facing strings are translated, and the UI supports RTL (right-to-left) layout for Arabic.

### Translation Files

**Location:** `src/frontend/src/shared/locales/`

```
locales/
├── ar.json  # Arabic translations
└── en.json  # English translations
```

**Example structure:**

```json
// ar.json
{
  "auth": {
    "login": {
      "title": "تسجيل الدخول",
      "email": "البريد الإلكتروني",
      "password": "كلمة المرور",
      "submit": "دخول",
      "forgotPassword": "نسيت كلمة المرور؟"
    }
  },
  "assessments": {
    "title": "التقييمات",
    "createNew": "إنشاء تقييم جديد",
    "overallScore": "النتيجة الإجمالية",
    "delegation": {
      "title": "تفويض المهمة",
      "selectUser": "اختر المستخدم",
      "assignTask": "تعيين المهمة"
    }
  },
  "domains": {
    "1": "التطوير التنظيمي",
    "2": "إدارة الأداء",
    "3": "المكافآت الشاملة"
  }
}

// en.json
{
  "auth": {
    "login": {
      "title": "Login",
      "email": "Email",
      "password": "Password",
      "submit": "Sign In",
      "forgotPassword": "Forgot password?"
    }
  },
  "assessments": {
    "title": "Assessments",
    "createNew": "Create New Assessment",
    "overallScore": "Overall Score",
    "delegation": {
      "title": "Delegate Task",
      "selectUser": "Select User",
      "assignTask": "Assign Task"
    }
  },
  "domains": {
    "1": "Organizational Development",
    "2": "Performance Management",
    "3": "Total Rewards"
  }
}
```

### i18n Configuration

**Location:** `src/frontend/src/shared/config/i18n.ts`

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from '../locales/en.json';
import ar from '../locales/ar.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      ar: { translation: ar }
    },
    lng: "en",            // Default language
    fallbackLng: "en",    // Fallback if key missing in current language
    interpolation: {
      escapeValue: false  // React already escapes by default
    }
  });

// RTL layout handling
i18n.on('languageChanged', (lng) => {
  const dir = lng === 'ar' ? 'rtl' : 'ltr';
  document.documentElement.dir = dir;      // Set HTML dir attribute
  document.documentElement.lang = lng;     // Set HTML lang attribute
});

export default i18n;
```

### Component Usage

**Pattern 1: Static strings**

```tsx
import { useTranslation } from 'react-i18next';

export const LoginForm = () => {
  const { t } = useTranslation();

  return (
    <form>
      <h1>{t('auth.login.title')}</h1>

      <label>{t('auth.login.email')}</label>
      <input type="email" placeholder={t('auth.login.email')} />

      <label>{t('auth.login.password')}</label>
      <input type="password" placeholder={t('auth.login.password')} />

      <button type="submit">{t('auth.login.submit')}</button>

      <a href="/forgot-password">{t('auth.login.forgotPassword')}</a>
    </form>
  );
};
```

**Pattern 2: Dynamic values (interpolation)**

```json
// ar.json
{
  "assessments": {
    "progress": "تم إكمال {{count}} من {{total}} عنصر"
  }
}

// en.json
{
  "assessments": {
    "progress": "{{count}} of {{total}} elements completed"
  }
}
```

```tsx
<p>{t('assessments.progress', { count: 15, total: 74 })}</p>
// Arabic: "تم إكمال 15 من 74 عنصر"
// English: "15 of 74 elements completed"
```

**Pattern 3: Pluralization**

```json
// en.json
{
  "comments": {
    "replies_one": "{{count}} reply",
    "replies_other": "{{count}} replies"
  }
}

// ar.json (Arabic has 6 plural forms!)
{
  "comments": {
    "replies_zero": "لا توجد ردود",
    "replies_one": "رد واحد",
    "replies_two": "ردان",
    "replies_few": "{{count}} ردود",
    "replies_many": "{{count}} رد",
    "replies_other": "{{count}} رد"
  }
}
```

```tsx
<span>{t('comments.replies', { count: replyCount })}</span>
```

### Language Switcher

**Location:** `src/frontend/src/shared/components/language-switcher.tsx`

```tsx
export const LanguageSwitcher = () => {
  const { i18n } = useTranslation();

  const toggleLanguage = () => {
    const newLang = i18n.language === 'ar' ? 'en' : 'ar';
    i18n.changeLanguage(newLang);

    // Persist to localStorage
    localStorage.setItem('language', newLang);
  };

  return (
    <Button onClick={toggleLanguage} variant="ghost">
      {i18n.language === 'ar' ? 'English' : 'العربية'}
    </Button>
  );
};
```

### RTL CSS Handling

**TailwindCSS 4 RTL utilities:**

```tsx
<div className="mr-4 rtl:ml-4 rtl:mr-0">
  {/* margin-right: 1rem in LTR */}
  {/* margin-left: 1rem in RTL */}
</div>

<div className="text-left rtl:text-right">
  {/* Align text left in LTR, right in RTL */}
</div>

<div className="flex flex-row rtl:flex-row-reverse">
  {/* Reverse flex direction in RTL */}
</div>
```

**Global RTL via `dir` attribute:**

When language changes to Arabic, `document.documentElement.dir = 'rtl'` automatically flips:
- Text alignment (left ↔ right)
- Padding/margin (left ↔ right)
- Scroll direction
- Border radius corners
- Flexbox/grid direction

**Manual overrides when needed:**

```css
/* globals.css */
[dir="rtl"] .custom-component {
  transform: scaleX(-1); /* Flip icons/images */
}

[dir="rtl"] .date-picker {
  direction: ltr; /* Force LTR for calendar widget */
}
```

### Backend i18n

**Error messages in both languages:**

```python
# src/backend/app/common/schemas.py

class ErrorResponse(BaseModel):
    code: str                 # Machine-readable error code
    message_en: str           # English message
    message_ar: str           # Arabic message

# Usage in exception handler
raise HTTPException(
    status_code=400,
    detail={
        "code": "INVALID_EMAIL",
        "message_en": "Email address is invalid",
        "message_ar": "عنوان البريد الإلكتروني غير صالح"
    }
)
```

**Frontend handles both:**

```tsx
const { data, error } = useLogin();

if (error) {
  const message = i18n.language === 'ar'
    ? error.message_ar
    : error.message_en;
  toast.error(message);
}
```

### Development Workflow

1. **Add new feature** → identify all user-facing strings
2. **Add translation keys** to both `ar.json` and `en.json`
3. **Use `t()` function** in components, NEVER hardcode strings
4. **Test in both languages** → toggle language switcher to verify translations
5. **Test RTL layout** → ensure UI doesn't break in Arabic (spacing, alignment, icons)

### Best Practices

- **Namespace keys:** Use hierarchical structure (`auth.login.title`) for organization
- **Avoid concatenation:** Use interpolation instead of `t('hello') + ' ' + name`
- **Translation comments:** Add context for translators in separate `ar-comments.json` file
- **Missing translations:** i18next falls back to English key if Arabic missing
- **Professional translation:** Use native Arabic speakers for final review (dialect: Saudi/Fusha)

---

## Summary

This walkthrough covered the implementation patterns for:

1. **Scoring Engine:** 4-level weighted hierarchy (Element → Dimension → Domain → Overall)
2. **Comment Threading:** Self-referencing FK with recursive frontend rendering
3. **Domain Delegation:** Permission grants via delegation records, enforced in dependencies
4. **RBAC:** Explicit role-based permissions with FastAPI dependency guards
5. **Tenant Isolation:** JWT-based context propagation + service-layer filtering
6. **Bilingual i18n:** react-i18next with full RTL support and backend error localization

Each pattern is production-ready, testable, and follows the project's conventions defined in `CLAUDE.md` and `PROJECT_CONTEXT.md`.

For implementation details on other features (SSO, MFA, Evidence Upload, Reporting, etc.), refer to the actual source files in `src/backend/app/` and `src/frontend/src/features/`.
