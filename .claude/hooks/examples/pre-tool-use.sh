#!/bin/bash
# =============================================================================
# Pre-Tool-Use Hook - Claude Code
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
#   1. Copy to ~/.claude/hooks/pre-tool-use.sh
#   2. chmod +x ~/.claude/hooks/pre-tool-use.sh
#   3. Configure in ~/.claude/settings.json or .claude/settings.json
# =============================================================================

set -euo pipefail

# Configuration
LOG_DIR="${HOME}/.claude/logs"
LOG_FILE="${LOG_DIR}/tool-usage.log"
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "rm -rf \$HOME"
    ":(){ :|:& };:"
    "> /dev/sda"
    "mkfs."
    "dd if="
    "chmod -R 777 /"
    ":(){:|:&};"
)

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Extract tool info (with fallbacks)
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
TOOL_INPUT="${CLAUDE_TOOL_INPUT:-{}}"
SESSION_ID="${CLAUDE_SESSION_ID:-no-session}"

# =============================================================================
# LOGGING
# =============================================================================

# Log tool invocation
log_entry() {
    echo "[${TIMESTAMP}] SESSION=${SESSION_ID} TOOL=${TOOL_NAME} INPUT=${TOOL_INPUT}" >> "$LOG_FILE"
}

# Log to stderr (visible to user in verbose mode)
log_debug() {
    echo "[pre-hook] $1" >&2
}

# =============================================================================
# VALIDATION
# =============================================================================

# Check for dangerous commands in Bash tool
check_dangerous_commands() {
    if [[ "$TOOL_NAME" == "Bash" ]]; then
        local command
        command=$(echo "$TOOL_INPUT" | jq -r '.command // empty' 2>/dev/null || echo "")

        for pattern in "${DANGEROUS_PATTERNS[@]}"; do
            if [[ "$command" == *"$pattern"* ]]; then
                echo "BLOCKED: Dangerous command pattern detected: $pattern" >&2
                echo "[${TIMESTAMP}] BLOCKED SESSION=${SESSION_ID} TOOL=${TOOL_NAME} REASON=dangerous_pattern PATTERN=${pattern}" >> "$LOG_FILE"
                exit 1
            fi
        done
    fi
}

# Check for sensitive file access
check_sensitive_files() {
    local sensitive_patterns=(
        ".env"
        ".env.local"
        ".env.production"
        "secrets/"
        "credentials"
        ".ssh/id_"
        ".aws/credentials"
        ".kube/config"
    )

    # Check Read tool
    if [[ "$TOOL_NAME" == "Read" ]]; then
        local file_path
        file_path=$(echo "$TOOL_INPUT" | jq -r '.file_path // empty' 2>/dev/null || echo "")

        for pattern in "${sensitive_patterns[@]}"; do
            if [[ "$file_path" == *"$pattern"* ]]; then
                log_debug "Warning: Accessing potentially sensitive file: $file_path"
                echo "[${TIMESTAMP}] WARNING SESSION=${SESSION_ID} TOOL=${TOOL_NAME} FILE=${file_path} REASON=sensitive_file" >> "$LOG_FILE"
                # Note: We warn but don't block - adjust as needed
            fi
        done
    fi
}

# Validate working directory
check_working_directory() {
    local cwd="${CLAUDE_WORKING_DIR:-$(pwd)}"

    # Block operations outside of safe directories
    local safe_dirs=(
        "$HOME/repos"
        "$HOME/projects"
        "$HOME/code"
        "/tmp"
    )

    local is_safe=false
    for safe_dir in "${safe_dirs[@]}"; do
        if [[ "$cwd" == "$safe_dir"* ]]; then
            is_safe=true
            break
        fi
    done

    # Uncomment to enforce directory restrictions
    # if [[ "$is_safe" == "false" ]]; then
    #     echo "BLOCKED: Operations not allowed outside safe directories" >&2
    #     exit 1
    # fi
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    # Always log the tool usage
    log_entry

    # Run validation checks
    check_dangerous_commands
    check_sensitive_files
    # check_working_directory  # Uncomment to enable

    # Log successful validation
    log_debug "Tool validated: $TOOL_NAME"

    # Exit 0 to allow tool execution
    exit 0
}

main "$@"
