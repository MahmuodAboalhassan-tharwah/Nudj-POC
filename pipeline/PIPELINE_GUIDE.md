# Nudj Development Pipeline — Usage Guide

## Overview

Your project has a 5-agent development pipeline that takes a feature from requirements to reviewed code:

```
PRD Documents
     |
     v
[requirements-analyst] --> pipeline/requirements/*.json
     |
     v
[task-splitter] ----------> pipeline/tasks/*.json
     |
     v
[coder] (parallel) ------> src/ (code) + pipeline/tasks/*-result.md
     |
     v
[code-reviewer] ----------> pipeline/reviews/*-review.json
[security-reviewer] ------> pipeline/reviews/*-security-review.json
```

---

## Method 1: Interactive (VS Code Extension)

Use this when you want control over each step. In the Claude Code sidebar:

### Step 1 — Analyze Requirements
```
@requirements-analyst Analyze all requirements for the Authentication & Authorization
feature from our PRDs. Focus on REQ-AUTH-001 through REQ-AUTH-003.
```

### Step 2 — Split into Tasks
```
@task-splitter Read pipeline/requirements/auth-requirements.json and decompose
into parallelizable coding tasks with clear file ownership.
```

### Step 3 — Code (run for each task or batch)
```
@coder Implement TASK-001 from pipeline/tasks/auth-tasks.json.
Read the task manifest for your specific scope and files.
```

### Step 4 — Review
```
@code-reviewer Review all code changes for the auth feature.
Read the task manifest and all task results, then review every modified file.
```

### Step 5 — Security Review
```
@security-reviewer Perform a security audit on the auth feature.
Focus on JWT handling, tenant isolation, and PDPL compliance.
```

---

## Method 2: CLI with Orchestration Script

### Full Pipeline (all stages)
```powershell
# PowerShell (Windows)
.\pipeline\orchestrate.ps1 -Feature "auth-system"

# Bash (Git Bash / WSL)
./pipeline/orchestrate.sh auth-system
```

### Individual Stages
```powershell
# Run only requirements analysis
.\pipeline\orchestrate.ps1 -Feature "auth-system" -Stage "analyze"

# Run only task splitting
.\pipeline\orchestrate.ps1 -Feature "auth-system" -Stage "split"

# Run only coding (parallel)
.\pipeline\orchestrate.ps1 -Feature "auth-system" -Stage "code"

# Run only code review
.\pipeline\orchestrate.ps1 -Feature "auth-system" -Stage "review"

# Run only security review
.\pipeline\orchestrate.ps1 -Feature "auth-system" -Stage "security"
```

---

## Method 3: CLI Manual (Most Control)

Run each agent directly via `claude -p`:

```bash
# Stage 1: Requirements
claude -p "Analyze requirements for Assessment Management from the PRDs. \
  Read PROJECT_CONTEXT.md first. Write analysis to \
  pipeline/requirements/assessment-requirements.json" \
  --allowedTools "Read,Grep,Glob,Write" \
  --permission-mode acceptEdits

# Stage 2: Task Split
claude -p "Read pipeline/requirements/assessment-requirements.json. \
  Decompose into coding tasks. Write to \
  pipeline/tasks/assessment-tasks.json" \
  --allowedTools "Read,Grep,Glob,Write" \
  --permission-mode acceptEdits

# Stage 3: Code (one per task)
claude -p "Implement TASK-001 from pipeline/tasks/assessment-tasks.json. \
  Read PROJECT_CONTEXT.md and CLAUDE.md. Only modify owned files." \
  --allowedTools "Read,Write,Edit,Bash,Glob,Grep" \
  --permission-mode acceptEdits

# Stage 4: Review
claude -p "Review all code for assessment feature. Read task manifest \
  and requirements. Write to pipeline/reviews/assessment-review.json" \
  --allowedTools "Read,Grep,Glob,Bash"

# Stage 5: Security
claude -p "Security review for assessment feature. Check OWASP, \
  tenant isolation, PDPL. Write to \
  pipeline/reviews/assessment-security-review.json" \
  --allowedTools "Read,Grep,Glob,Bash"
```

---

## Pipeline Artifacts

After running the pipeline, you'll find these files:

```
pipeline/
├── requirements/
│   ├── auth-requirements.json          # Structured requirements
│   └── auth-analysis-log.json          # Agent execution log
├── tasks/
│   ├── auth-tasks.json                 # Task manifest with execution plan
│   ├── TASK-001-result.md              # Per-task completion report
│   ├── TASK-001-log.json               # Per-task execution log
│   └── auth-split-log.json             # Splitter execution log
└── reviews/
    ├── auth-review.json                # Code review findings
    ├── auth-security-review.json       # Security findings
    ├── auth-review-log.json            # Review execution log
    └── auth-security-log.json          # Security review execution log
```

---

## Feature Breakdown (Suggested Order)

Based on the PRDs, here's a recommended order for implementing features:

### Phase 1: Foundation
1. `auth-system` — Authentication, registration, RBAC, JWT
2. `org-management` — Organization CRUD with sector/size/region
3. `user-management` — Invitation flow, role assignment

### Phase 2: Core Assessment
4. `framework-config` — HR maturity framework data model and configuration
5. `assessment-management` — Project creation, workflow states
6. `questionnaire` — Assessment questionnaire interface
7. `evidence-upload` — Evidence upload and management
8. `scoring-engine` — Automated weighted scoring

### Phase 3: Analytics & Reporting
9. `portfolio-dashboard` — Tharwah portfolio view
10. `client-dashboard` — Client organization dashboard
11. `progress-tracker` — Real-time assessment progress
12. `maturity-report` — PDF report generation
13. `comparative-report` — Side-by-side and benchmark reports

### Phase 4: Collaboration & Notifications
14. `notifications` — Email + in-app notifications
15. `comments` — Threaded comments and discussions
16. `delegation` — Assessment delegation

### Phase 5: V2 Intelligence
17. `benchmark-warehouse` — BDW data model and ETL pipeline
18. `benchmark-reports` — Comparison and longitudinal reports
19. `industry-insights` — Query engine for aggregate analytics
20. `ai-coach` — AI HR Maturity Coach (RAG + LLM)
21. `coach-knowledge-base` — Knowledge base management
22. `coach-analytics` — Interaction analytics

### Phase 6: Administration
23. `audit-trail` — Comprehensive audit logging
24. `framework-versioning` — Framework version management

---

## Tips

- **Start small**: Run `analyze` first and review the output before proceeding
- **Iterate**: If the requirements analysis misses something, edit the JSON and re-run `split`
- **Review early**: Don't wait until all coding is done — review each phase
- **File ownership**: If the task splitter assigns the same file to two tasks, fix the manifest before coding
- **Context is king**: The more specific your prompts to agents, the better the output
- **Check memory**: Agents with `memory: user` accumulate knowledge across sessions
