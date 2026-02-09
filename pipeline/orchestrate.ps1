# =============================================================================
# Nudj Development Pipeline Orchestrator (PowerShell)
# =============================================================================
# Usage:
#   .\pipeline\orchestrate.ps1 -Feature "auth-system" [-Stage "all"]
#
# Stages: all, analyze, split, code, review, security
# =============================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$Feature,

    [Parameter(Mandatory=$false)]
    [ValidateSet("all", "analyze", "split", "code", "review", "security")]
    [string]$Stage = "all"
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$PipelineDir = Join-Path $ProjectDir "pipeline"

function Write-Log { param($msg) Write-Host "[PIPELINE] $msg" -ForegroundColor Cyan }
function Write-OK { param($msg) Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "[WARNING] $msg" -ForegroundColor Yellow }
function Write-Err { param($msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }

# =============================================================================
# Stage 1: Requirements Analysis
# =============================================================================
function Invoke-Analyze {
    Write-Log "Stage 1: Analyzing requirements for '$Feature'..."

    $reqFile = Join-Path $PipelineDir "requirements\$Feature-requirements.json"
    if (Test-Path $reqFile) { Write-Warn "Requirements file exists. Will overwrite." }

    $prompt = @"
You are the requirements-analyst agent. Analyze the requirements for the '$Feature' feature of the Nudj platform.

Read PROJECT_CONTEXT.md first, then analyze the PRD documents for everything related to '$Feature'.
Write your structured analysis to pipeline/requirements/$Feature-requirements.json following the format in your agent definition.

Be thorough - identify ALL functional requirements, acceptance criteria, component mappings, and dependencies.
"@

    claude -p $prompt `
        --allowedTools "Read,Grep,Glob,Bash,Write" `
        --permission-mode acceptEdits `
        --output-format json > (Join-Path $PipelineDir "requirements\$Feature-analysis-log.json") 2>&1

    if (Test-Path $reqFile) {
        Write-OK "Requirements analysis complete: pipeline/requirements/$Feature-requirements.json"
    } else {
        Write-Err "Requirements analysis failed"
        exit 1
    }
}

# =============================================================================
# Stage 2: Task Splitting
# =============================================================================
function Invoke-Split {
    Write-Log "Stage 2: Splitting requirements into tasks for '$Feature'..."

    $reqFile = Join-Path $PipelineDir "requirements\$Feature-requirements.json"
    if (-not (Test-Path $reqFile)) {
        Write-Err "No requirements file found. Run 'analyze' stage first."
        exit 1
    }

    $prompt = @"
You are the task-splitter agent. Read the analyzed requirements from pipeline/requirements/$Feature-requirements.json.

Decompose them into parallelizable coding tasks with clear file ownership boundaries.
Read PROJECT_CONTEXT.md and CLAUDE.md for conventions.
Write your task manifest to pipeline/tasks/$Feature-tasks.json following the format in your agent definition.

Critical: NO two tasks should own the same file. Define clear execution phases.
"@

    claude -p $prompt `
        --allowedTools "Read,Grep,Glob,Write" `
        --permission-mode acceptEdits `
        --output-format json > (Join-Path $PipelineDir "tasks\$Feature-split-log.json") 2>&1

    $taskFile = Join-Path $PipelineDir "tasks\$Feature-tasks.json"
    if (Test-Path $taskFile) {
        Write-OK "Task splitting complete: pipeline/tasks/$Feature-tasks.json"
    } else {
        Write-Err "Task splitting failed"
        exit 1
    }
}

# =============================================================================
# Stage 3: Parallel Coding
# =============================================================================
function Invoke-Code {
    Write-Log "Stage 3: Implementing tasks for '$Feature'..."

    $taskFile = Join-Path $PipelineDir "tasks\$Feature-tasks.json"
    if (-not (Test-Path $taskFile)) {
        Write-Err "No task manifest found. Run 'split' stage first."
        exit 1
    }

    $manifest = Get-Content $taskFile | ConvertFrom-Json
    $tasksById = @{}
    foreach ($task in $manifest.tasks) { $tasksById[$task.id] = $task }

    $executionPlan = $manifest.executionPlan.PSObject.Properties | Sort-Object Name

    foreach ($phase in $executionPlan) {
        $phaseName = $phase.Name
        $taskIds = $phase.Value
        Write-Log "--- $phaseName`: $($taskIds.Count) tasks ---"

        $jobs = @()
        foreach ($taskId in $taskIds) {
            $task = $tasksById[$taskId]
            if (-not $task) {
                Write-Warn "Task $taskId not found in manifest"
                continue
            }

            $filesOwned = ($task.filesOwned -join ", ")
            $criteria = ($task.acceptanceCriteria -join "`n")

            $taskPrompt = @"
You are the coder agent. Implement this specific task:

Task ID: $($task.id)
Title: $($task.title)
Layer: $($task.layer)
Description: $($task.description)
Files to create/modify: $filesOwned
Acceptance Criteria:
$criteria
Context: $($task.contextFromOtherTasks)

Read PROJECT_CONTEXT.md and CLAUDE.md first.
ONLY modify files listed in filesOwned.
Write your result to pipeline/tasks/$($task.id)-result.md when done.
"@

            Write-Log "  Starting: $taskId - $($task.title)"

            $logFile = Join-Path $PipelineDir "tasks\$taskId-log.json"
            $job = Start-Job -ScriptBlock {
                param($p, $log)
                claude -p $p `
                    --allowedTools "Read,Write,Edit,Bash,Glob,Grep" `
                    --permission-mode acceptEdits `
                    --output-format json > $log 2>&1
            } -ArgumentList $taskPrompt, $logFile

            $jobs += @{ Id = $taskId; Job = $job }
        }

        # Wait for all jobs in this phase
        foreach ($j in $jobs) {
            $j.Job | Wait-Job | Out-Null
            $state = $j.Job.State
            Write-Log "  Completed: $($j.Id) - $state"
            Remove-Job $j.Job
        }
    }

    Write-OK "Coding phase complete for '$Feature'"
}

# =============================================================================
# Stage 4: Code Review
# =============================================================================
function Invoke-Review {
    Write-Log "Stage 4: Reviewing code for '$Feature'..."

    $prompt = @"
You are the code-reviewer agent. Review ALL code changes for the '$Feature' feature.

1. Read PROJECT_CONTEXT.md and CLAUDE.md for conventions
2. Read the task manifest: pipeline/tasks/$Feature-tasks.json
3. Read all task results: pipeline/tasks/TASK-*-result.md
4. Read the original requirements: pipeline/requirements/$Feature-requirements.json
5. Review EVERY file mentioned in the task manifest
6. Write your review to pipeline/reviews/$Feature-review.json

Be thorough but fair. Only flag issues at 80%+ confidence.
"@

    claude -p $prompt `
        --allowedTools "Read,Grep,Glob,Bash" `
        --output-format json > (Join-Path $PipelineDir "reviews\$Feature-review-log.json") 2>&1

    $reviewFile = Join-Path $PipelineDir "reviews\$Feature-review.json"
    if (Test-Path $reviewFile) {
        Write-OK "Code review complete: pipeline/reviews/$Feature-review.json"
    } else {
        Write-Err "Code review failed"
        exit 1
    }
}

# =============================================================================
# Stage 5: Security Review
# =============================================================================
function Invoke-Security {
    Write-Log "Stage 5: Security review for '$Feature'..."

    $prompt = @"
You are the security-reviewer agent. Perform a focused security review for the '$Feature' feature.

1. Read PROJECT_CONTEXT.md for platform context
2. Read all files mentioned in pipeline/tasks/$Feature-tasks.json
3. Check OWASP Top 10, tenant isolation, PDPL compliance, and AI Coach safety
4. Write your findings to pipeline/reviews/$Feature-security-review.json

This platform handles sensitive HR data for Saudi organizations. Be thorough.
"@

    claude -p $prompt `
        --allowedTools "Read,Grep,Glob,Bash" `
        --output-format json > (Join-Path $PipelineDir "reviews\$Feature-security-log.json") 2>&1

    $secFile = Join-Path $PipelineDir "reviews\$Feature-security-review.json"
    if (Test-Path $secFile) {
        Write-OK "Security review complete: pipeline/reviews/$Feature-security-review.json"
    } else {
        Write-Err "Security review failed"
        exit 1
    }
}

# =============================================================================
# Main Execution
# =============================================================================
Write-Log "Nudj Pipeline | Feature: '$Feature' | Stage: '$Stage'"
Write-Log "Project: $ProjectDir"
Write-Host ""

switch ($Stage) {
    "all" {
        Invoke-Analyze
        Invoke-Split
        Invoke-Code
        Invoke-Review
        Invoke-Security
        Write-Host ""
        Write-OK "=== FULL PIPELINE COMPLETE for '$Feature' ==="
    }
    "analyze"  { Invoke-Analyze }
    "split"    { Invoke-Split }
    "code"     { Invoke-Code }
    "review"   { Invoke-Review }
    "security" { Invoke-Security }
}
