# =============================================================================
# Pre-Tool-Use Hook - Claude Code (PowerShell)
# =============================================================================
# This hook runs BEFORE Claude executes any tool.
# Use it for logging, validation, or blocking dangerous operations.
#
# Environment variables available:
#   CLAUDE_TOOL_NAME      - Name of the tool being invoked
#   CLAUDE_TOOL_INPUT     - JSON string of tool input parameters
#   CLAUDE_SESSION_ID     - Current session identifier
#   CLAUDE_WORKING_DIR    - Current working directory
#
# Exit codes:
#   0 - Allow tool execution to proceed
#   1 - Block tool execution (Claude will see the error message)
#
# Installation:
#   1. Copy to ~/.claude/hooks/pre-tool-use.ps1
#   2. Configure in ~/.claude/settings.json or .claude/settings.json
# =============================================================================

#Requires -Version 5.1

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

# Configuration
$LogDir = Join-Path $env:USERPROFILE '.claude\logs'
$LogFile = Join-Path $LogDir 'tool-usage.log'

$DangerousPatterns = @(
    'Remove-Item -Recurse -Force [/\\]',
    'Remove-Item -Recurse -Force \$env:',
    'Remove-Item -Recurse -Force \$HOME',
    'Format-Volume',
    'Clear-Disk',
    'Initialize-Disk',
    'Stop-Service WinDefend',
    'Set-MpPreference -Disable',
    'Disable-WindowsOptionalFeature',
    'reg add.*DisableAntiSpyware'
)

$SensitiveFilePatterns = @(
    '\.env$',
    '\.env\.local$',
    '\.env\.production$',
    'secrets[/\\]',
    'credentials',
    '\.ssh[/\\]id_',
    '\.aws[/\\]credentials',
    '\.kube[/\\]config'
)

# =============================================================================
# INITIALIZATION
# =============================================================================

# Ensure log directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Get current timestamp
$Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

# Extract tool info from environment variables
$ToolName = $env:CLAUDE_TOOL_NAME
if ([string]::IsNullOrEmpty($ToolName)) { $ToolName = 'unknown' }

$ToolInput = $env:CLAUDE_TOOL_INPUT
if ([string]::IsNullOrEmpty($ToolInput)) { $ToolInput = '{}' }

$SessionId = $env:CLAUDE_SESSION_ID
if ([string]::IsNullOrEmpty($SessionId)) { $SessionId = 'no-session' }

$WorkingDir = $env:CLAUDE_WORKING_DIR
if ([string]::IsNullOrEmpty($WorkingDir)) { $WorkingDir = Get-Location }

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
    Write-Host "[pre-hook] $Message" -ForegroundColor Cyan
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

function Test-DangerousCommand {
    if ($ToolName -eq 'Bash') {
        try {
            $InputObj = $ToolInput | ConvertFrom-Json
            $Command = $InputObj.command

            if ([string]::IsNullOrEmpty($Command)) { return $true }

            foreach ($Pattern in $DangerousPatterns) {
                if ($Command -match $Pattern) {
                    Write-Host "BLOCKED: Dangerous command pattern detected: $Pattern" -ForegroundColor Red
                    Write-ToolLog "BLOCKED SESSION=$SessionId TOOL=$ToolName REASON=dangerous_pattern PATTERN=$Pattern"
                    return $false
                }
            }
        }
        catch {
            Write-DebugLog "Warning: Could not parse tool input JSON"
        }
    }
    return $true
}

function Test-SensitiveFileAccess {
    if ($ToolName -eq 'Read') {
        try {
            $InputObj = $ToolInput | ConvertFrom-Json
            $FilePath = $InputObj.file_path

            if ([string]::IsNullOrEmpty($FilePath)) { return $true }

            foreach ($Pattern in $SensitiveFilePatterns) {
                if ($FilePath -match $Pattern) {
                    Write-DebugLog "Warning: Accessing potentially sensitive file: $FilePath"
                    Write-ToolLog "WARNING SESSION=$SessionId TOOL=$ToolName FILE=$FilePath REASON=sensitive_file"
                    # Warning only - don't block. Uncomment to block:
                    # return $false
                }
            }
        }
        catch {
            Write-DebugLog "Warning: Could not parse tool input JSON"
        }
    }
    return $true
}

function Test-WorkingDirectory {
    $SafeDirs = @(
        (Join-Path $env:USERPROFILE 'repos'),
        (Join-Path $env:USERPROFILE 'projects'),
        (Join-Path $env:USERPROFILE 'code'),
        $env:TEMP
    )

    $IsSafe = $false
    foreach ($SafeDir in $SafeDirs) {
        if ($WorkingDir -like "$SafeDir*") {
            $IsSafe = $true
            break
        }
    }

    # Uncomment to enforce directory restrictions:
    # if (-not $IsSafe) {
    #     Write-Host "BLOCKED: Operations not allowed outside safe directories" -ForegroundColor Red
    #     return $false
    # }

    return $true
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

function Main {
    # Log tool invocation
    Write-ToolLog "SESSION=$SessionId TOOL=$ToolName INPUT=$ToolInput"

    # Run validation checks
    if (-not (Test-DangerousCommand)) {
        exit 1
    }

    if (-not (Test-SensitiveFileAccess)) {
        exit 1
    }

    if (-not (Test-WorkingDirectory)) {
        exit 1
    }

    # Log successful validation
    Write-DebugLog "Tool validated: $ToolName"

    # Exit 0 to allow tool execution
    exit 0
}

# Run main function
Main
