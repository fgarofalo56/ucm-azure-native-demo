# =============================================================================
# Post-Tool-Use Hook - Claude Code (PowerShell)
# =============================================================================
# This hook runs AFTER Claude executes any tool.
# Use it for logging completion, tracking metrics, or triggering actions.
#
# Environment variables available:
#   CLAUDE_TOOL_NAME      - Name of the tool that was invoked
#   CLAUDE_TOOL_INPUT     - JSON string of tool input parameters
#   CLAUDE_TOOL_OUTPUT    - Tool execution result (may be truncated)
#   CLAUDE_TOOL_EXIT_CODE - Exit code from the tool (0 = success)
#   CLAUDE_TOOL_DURATION  - Execution time in milliseconds
#   CLAUDE_SESSION_ID     - Current session identifier
#   CLAUDE_WORKING_DIR    - Current working directory
#
# Exit codes:
#   0 - Normal completion
#   Non-zero - Log error but don't affect Claude's response
#
# Installation:
#   1. Copy to ~/.claude/hooks/post-tool-use.ps1
#   2. Configure in ~/.claude/settings.json or .claude/settings.json
# =============================================================================

#Requires -Version 5.1

[CmdletBinding()]
param()

$ErrorActionPreference = 'SilentlyContinue'

# Configuration
$LogDir = Join-Path $env:USERPROFILE '.claude\logs'
$LogFile = Join-Path $LogDir 'tool-usage.log'
$MetricsFile = Join-Path $LogDir 'tool-metrics.jsonl'
$ErrorLog = Join-Path $LogDir 'tool-errors.log'
$AlertThresholdMs = 30000  # Alert if tool takes longer than 30 seconds

# =============================================================================
# INITIALIZATION
# =============================================================================

# Ensure log directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Get timestamps
$Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$TimestampISO = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'

# Extract tool info from environment variables
$ToolName = if ($env:CLAUDE_TOOL_NAME) { $env:CLAUDE_TOOL_NAME } else { 'unknown' }
$ToolInput = if ($env:CLAUDE_TOOL_INPUT) { $env:CLAUDE_TOOL_INPUT } else { '{}' }
$ToolOutput = if ($env:CLAUDE_TOOL_OUTPUT) { $env:CLAUDE_TOOL_OUTPUT } else { '' }
$ExitCode = if ($env:CLAUDE_TOOL_EXIT_CODE) { [int]$env:CLAUDE_TOOL_EXIT_CODE } else { 0 }
$Duration = if ($env:CLAUDE_TOOL_DURATION) { [int]$env:CLAUDE_TOOL_DURATION } else { 0 }
$SessionId = if ($env:CLAUDE_SESSION_ID) { $env:CLAUDE_SESSION_ID } else { 'no-session' }
$WorkingDir = if ($env:CLAUDE_WORKING_DIR) { $env:CLAUDE_WORKING_DIR } else { Get-Location }

# =============================================================================
# LOGGING FUNCTIONS
# =============================================================================

function Write-ToolLog {
    param([string]$Message)
    $LogEntry = "[$Timestamp] $Message"
    Add-Content -Path $LogFile -Value $LogEntry -ErrorAction SilentlyContinue
}

function Write-DebugLog {
    param([string]$Message)
    Write-Host "[post-hook] $Message" -ForegroundColor Cyan
}

function Write-Completion {
    $Status = if ($ExitCode -eq 0) { 'SUCCESS' } else { 'FAILED' }
    Write-ToolLog "COMPLETED SESSION=$SessionId TOOL=$ToolName STATUS=$Status EXIT=$ExitCode DURATION=${Duration}ms"
}

function Write-Metrics {
    $OutputLength = $ToolOutput.Length

    try {
        $InputSummary = $ToolInput | ConvertFrom-Json | ConvertTo-Json -Compress
    }
    catch {
        $InputSummary = '{}'
    }

    $MetricEntry = @{
        timestamp = $TimestampISO
        session = $SessionId
        tool = $ToolName
        exit_code = $ExitCode
        duration_ms = $Duration
        output_length = $OutputLength
        input = $InputSummary
    } | ConvertTo-Json -Compress

    Add-Content -Path $MetricsFile -Value $MetricEntry -ErrorAction SilentlyContinue
}

# =============================================================================
# ERROR HANDLING
# =============================================================================

function Write-ErrorDetails {
    if ($ExitCode -ne 0) {
        $ErrorEntry = @"

================================================================================
[$Timestamp] Tool Execution Failed
================================================================================
Session:  $SessionId
Tool:     $ToolName
Exit:     $ExitCode
Duration: ${Duration}ms
Input:    $ToolInput
Output:   $($ToolOutput.Substring(0, [Math]::Min(1000, $ToolOutput.Length)))
================================================================================
"@
        Add-Content -Path $ErrorLog -Value $ErrorEntry -ErrorAction SilentlyContinue
        Write-DebugLog "ERROR: Tool $ToolName failed with exit code $ExitCode"
    }
}

# =============================================================================
# ALERTING
# =============================================================================

function Test-Performance {
    if ($Duration -gt $AlertThresholdMs) {
        Write-DebugLog "WARNING: Tool $ToolName took ${Duration}ms (threshold: ${AlertThresholdMs}ms)"

        # Could integrate with notification systems here:
        # Invoke-RestMethod -Uri "https://your-webhook.com/alert" -Method Post -Body @{ tool = $ToolName; duration = $Duration }
    }
}

function Test-CriticalFailures {
    $CriticalTools = @('Bash', 'Write', 'Edit')

    if ($ExitCode -ne 0 -and $ToolName -in $CriticalTools) {
        Write-DebugLog "CRITICAL: Essential tool $ToolName failed"
        # Could send alert here
    }
}

# =============================================================================
# TRACKING
# =============================================================================

function Write-FileChanges {
    if ($ToolName -eq 'Write' -or $ToolName -eq 'Edit') {
        try {
            $InputObj = $ToolInput | ConvertFrom-Json
            $FilePath = $InputObj.file_path

            if (-not [string]::IsNullOrEmpty($FilePath) -and $ExitCode -eq 0) {
                $FileChangesLog = Join-Path $LogDir 'file-changes.log'
                Add-Content -Path $FileChangesLog -Value "[$Timestamp] FILE_MODIFIED $FilePath" -ErrorAction SilentlyContinue
            }
        }
        catch {
            # Ignore JSON parse errors
        }
    }
}

function Write-GitOperations {
    if ($ToolName -eq 'Bash') {
        try {
            $InputObj = $ToolInput | ConvertFrom-Json
            $Command = $InputObj.command

            if ($Command -like 'git*') {
                $GitLog = Join-Path $LogDir 'git-operations.log'
                Add-Content -Path $GitLog -Value "[$Timestamp] GIT_OP $Command" -ErrorAction SilentlyContinue
            }
        }
        catch {
            # Ignore JSON parse errors
        }
    }
}

# =============================================================================
# SESSION STATISTICS
# =============================================================================

function Update-SessionStats {
    $StatsFile = Join-Path $LogDir "session-$SessionId-stats.json"

    if (Test-Path $StatsFile) {
        try {
            $Existing = Get-Content $StatsFile -Raw | ConvertFrom-Json

            $Stats = @{
                session_id = $SessionId
                tool_count = $Existing.tool_count + 1
                total_duration_ms = $Existing.total_duration_ms + $Duration
                error_count = $Existing.error_count + $(if ($ExitCode -ne 0) { 1 } else { 0 })
                last_tool = $ToolName
                last_updated = $TimestampISO
            }
        }
        catch {
            $Stats = @{
                session_id = $SessionId
                tool_count = 1
                total_duration_ms = $Duration
                error_count = $(if ($ExitCode -ne 0) { 1 } else { 0 })
                last_tool = $ToolName
                last_updated = $TimestampISO
            }
        }
    }
    else {
        $Stats = @{
            session_id = $SessionId
            tool_count = 1
            total_duration_ms = $Duration
            error_count = $(if ($ExitCode -ne 0) { 1 } else { 0 })
            last_tool = $ToolName
            last_updated = $TimestampISO
        }
    }

    $Stats | ConvertTo-Json | Set-Content -Path $StatsFile -ErrorAction SilentlyContinue
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

function Main {
    # Core logging
    Write-Completion
    Write-Metrics
    Write-ErrorDetails

    # Performance monitoring
    Test-Performance
    Test-CriticalFailures

    # Action tracking
    Write-FileChanges
    Write-GitOperations

    # Update statistics
    Update-SessionStats

    # Log success
    Write-DebugLog "Post-hook completed for $ToolName (${Duration}ms, exit: $ExitCode)"

    exit 0
}

# Run main function
Main
