#!/bin/bash
# =============================================================================
# Nudj Development Pipeline Orchestrator
# =============================================================================
# Usage:
#   ./pipeline/orchestrate.sh <feature-name> [stage]
#
# Stages:
#   all         - Run full pipeline (default)
#   analyze     - Stage 1: Requirements analysis only
#   split       - Stage 2: Task splitting only
#   code        - Stage 3: Parallel coding only
#   review      - Stage 4: Code review only
#   security    - Stage 5: Security review only
#
# Examples:
#   ./pipeline/orchestrate.sh auth-system
#   ./pipeline/orchestrate.sh auth-system analyze
#   ./pipeline/orchestrate.sh assessment-scoring code
# =============================================================================

set -e

FEATURE_NAME="${1:?Usage: $0 <feature-name> [stage]}"
STAGE="${2:-all}"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PIPELINE_DIR="$PROJECT_DIR/pipeline"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() { echo -e "${BLUE}[PIPELINE]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# =============================================================================
# Stage 1: Requirements Analysis
# =============================================================================
stage_analyze() {
    log "Stage 1: Analyzing requirements for '$FEATURE_NAME'..."

    if [ -f "$PIPELINE_DIR/requirements/${FEATURE_NAME}-requirements.json" ]; then
        warn "Requirements file already exists. Overwriting..."
    fi

    claude -p "You are the requirements-analyst agent. Analyze the requirements for the '$FEATURE_NAME' feature of the Nudj platform.

Read PROJECT_CONTEXT.md first, then analyze the PRD documents for everything related to '$FEATURE_NAME'.
Write your structured analysis to pipeline/requirements/${FEATURE_NAME}-requirements.json following the format in your agent definition.

Be thorough — identify ALL functional requirements, acceptance criteria, component mappings, and dependencies." \
        --allowedTools "Read,Grep,Glob,Bash,Write" \
        --permission-mode acceptEdits \
        --output-format json > "$PIPELINE_DIR/requirements/${FEATURE_NAME}-analysis-log.json" 2>&1

    if [ -f "$PIPELINE_DIR/requirements/${FEATURE_NAME}-requirements.json" ]; then
        success "Requirements analysis complete: pipeline/requirements/${FEATURE_NAME}-requirements.json"
    else
        error "Requirements analysis failed — no output file generated"
        exit 1
    fi
}

# =============================================================================
# Stage 2: Task Splitting
# =============================================================================
stage_split() {
    log "Stage 2: Splitting requirements into coding tasks for '$FEATURE_NAME'..."

    if [ ! -f "$PIPELINE_DIR/requirements/${FEATURE_NAME}-requirements.json" ]; then
        error "No requirements file found. Run 'analyze' stage first."
        exit 1
    fi

    claude -p "You are the task-splitter agent. Read the analyzed requirements from pipeline/requirements/${FEATURE_NAME}-requirements.json.

Decompose them into parallelizable coding tasks with clear file ownership boundaries.
Read PROJECT_CONTEXT.md and CLAUDE.md for conventions.
Write your task manifest to pipeline/tasks/${FEATURE_NAME}-tasks.json following the format in your agent definition.

Critical: NO two tasks should own the same file. Define clear execution phases." \
        --allowedTools "Read,Grep,Glob,Write" \
        --permission-mode acceptEdits \
        --output-format json > "$PIPELINE_DIR/tasks/${FEATURE_NAME}-split-log.json" 2>&1

    if [ -f "$PIPELINE_DIR/tasks/${FEATURE_NAME}-tasks.json" ]; then
        success "Task splitting complete: pipeline/tasks/${FEATURE_NAME}-tasks.json"
    else
        error "Task splitting failed — no output file generated"
        exit 1
    fi
}

# =============================================================================
# Stage 3: Parallel Coding
# =============================================================================
stage_code() {
    log "Stage 3: Implementing coding tasks for '$FEATURE_NAME'..."

    if [ ! -f "$PIPELINE_DIR/tasks/${FEATURE_NAME}-tasks.json" ]; then
        error "No task manifest found. Run 'split' stage first."
        exit 1
    fi

    # Read the task manifest and extract tasks
    TASK_COUNT=$(python3 -c "
import json
with open('$PIPELINE_DIR/tasks/${FEATURE_NAME}-tasks.json') as f:
    manifest = json.load(f)
print(len(manifest.get('tasks', [])))
" 2>/dev/null || echo "0")

    if [ "$TASK_COUNT" = "0" ]; then
        error "No tasks found in manifest"
        exit 1
    fi

    log "Found $TASK_COUNT tasks. Executing by phase..."

    # Extract execution plan phases and run tasks in each phase in parallel
    python3 -c "
import json, subprocess, sys, os

with open('$PIPELINE_DIR/tasks/${FEATURE_NAME}-tasks.json') as f:
    manifest = json.load(f)

execution_plan = manifest.get('executionPlan', {})
tasks_by_id = {t['id']: t for t in manifest.get('tasks', [])}

for phase_name, task_ids in sorted(execution_plan.items()):
    print(f'\n--- {phase_name}: {len(task_ids)} tasks ---')
    processes = []

    for task_id in task_ids:
        task = tasks_by_id.get(task_id)
        if not task:
            print(f'WARNING: Task {task_id} not found in manifest')
            continue

        prompt = f'''You are the coder agent. Implement this specific task:

Task ID: {task['id']}
Title: {task['title']}
Layer: {task['layer']}
Description: {task['description']}
Files to create/modify: {', '.join(task.get('filesOwned', []))}
Acceptance Criteria: {chr(10).join(task.get('acceptanceCriteria', []))}
Context: {task.get('contextFromOtherTasks', 'None')}

Read PROJECT_CONTEXT.md and CLAUDE.md first.
ONLY modify files listed in filesOwned.
Write your result to pipeline/tasks/{task['id']}-result.md when done.'''

        print(f'  Starting: {task_id} - {task[\"title\"]}')

        proc = subprocess.Popen(
            ['claude', '-p', prompt,
             '--allowedTools', 'Read,Write,Edit,Bash,Glob,Grep',
             '--permission-mode', 'acceptEdits',
             '--output-format', 'json'],
            stdout=open(f'$PIPELINE_DIR/tasks/{task_id}-log.json', 'w'),
            stderr=subprocess.STDOUT
        )
        processes.append((task_id, proc))

    # Wait for all tasks in this phase to complete
    for task_id, proc in processes:
        returncode = proc.wait()
        status = 'OK' if returncode == 0 else f'FAILED (exit {returncode})'
        print(f'  Completed: {task_id} - {status}')

print('\nAll phases complete.')
" 2>&1

    success "Coding phase complete for '$FEATURE_NAME'"
}

# =============================================================================
# Stage 4: Code Review
# =============================================================================
stage_review() {
    log "Stage 4: Reviewing code for '$FEATURE_NAME'..."

    claude -p "You are the code-reviewer agent. Review ALL code changes for the '$FEATURE_NAME' feature.

1. Read PROJECT_CONTEXT.md and CLAUDE.md for conventions
2. Read the task manifest: pipeline/tasks/${FEATURE_NAME}-tasks.json
3. Read all task results: pipeline/tasks/TASK-*-result.md
4. Read the original requirements: pipeline/requirements/${FEATURE_NAME}-requirements.json
5. Review EVERY file mentioned in the task manifest
6. Write your review to pipeline/reviews/${FEATURE_NAME}-review.json

Be thorough but fair. Only flag issues at 80%+ confidence." \
        --allowedTools "Read,Grep,Glob,Bash" \
        --output-format json > "$PIPELINE_DIR/reviews/${FEATURE_NAME}-review-log.json" 2>&1

    if [ -f "$PIPELINE_DIR/reviews/${FEATURE_NAME}-review.json" ]; then
        success "Code review complete: pipeline/reviews/${FEATURE_NAME}-review.json"
    else
        error "Code review failed — no output file generated"
        exit 1
    fi
}

# =============================================================================
# Stage 5: Security Review
# =============================================================================
stage_security() {
    log "Stage 5: Security review for '$FEATURE_NAME'..."

    claude -p "You are the security-reviewer agent. Perform a focused security review for the '$FEATURE_NAME' feature.

1. Read PROJECT_CONTEXT.md for platform context
2. Read all files mentioned in pipeline/tasks/${FEATURE_NAME}-tasks.json
3. Run the security scan commands from your agent definition
4. Check OWASP Top 10, tenant isolation, PDPL compliance, and AI Coach safety
5. Write your findings to pipeline/reviews/${FEATURE_NAME}-security-review.json

This platform handles sensitive HR data for Saudi organizations. Be thorough." \
        --allowedTools "Read,Grep,Glob,Bash" \
        --output-format json > "$PIPELINE_DIR/reviews/${FEATURE_NAME}-security-log.json" 2>&1

    if [ -f "$PIPELINE_DIR/reviews/${FEATURE_NAME}-security-review.json" ]; then
        success "Security review complete: pipeline/reviews/${FEATURE_NAME}-security-review.json"
    else
        error "Security review failed — no output file generated"
        exit 1
    fi
}

# =============================================================================
# Main Execution
# =============================================================================
log "Nudj Development Pipeline — Feature: '$FEATURE_NAME' — Stage: '$STAGE'"
log "Project: $PROJECT_DIR"
log "Started: $TIMESTAMP"
echo ""

case "$STAGE" in
    all)
        stage_analyze
        stage_split
        stage_code
        stage_review
        stage_security
        echo ""
        success "=== FULL PIPELINE COMPLETE for '$FEATURE_NAME' ==="
        log "Requirements: pipeline/requirements/${FEATURE_NAME}-requirements.json"
        log "Task Manifest: pipeline/tasks/${FEATURE_NAME}-tasks.json"
        log "Code Review: pipeline/reviews/${FEATURE_NAME}-review.json"
        log "Security Review: pipeline/reviews/${FEATURE_NAME}-security-review.json"
        ;;
    analyze)  stage_analyze ;;
    split)    stage_split ;;
    code)     stage_code ;;
    review)   stage_review ;;
    security) stage_security ;;
    *)
        error "Unknown stage: $STAGE"
        echo "Valid stages: all, analyze, split, code, review, security"
        exit 1
        ;;
esac
