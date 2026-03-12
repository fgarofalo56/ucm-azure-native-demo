#!/bin/bash
# =============================================================================
# Post-Tool-Use Hook - Claude Code
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
#   1. Copy to ~/.claude/hooks/post-tool-use.sh
#   2. chmod +x ~/.claude/hooks/post-tool-use.sh
#   3. Configure in ~/.claude/settings.json or .claude/settings.json
# =============================================================================

set -euo pipefail

# Configuration
LOG_DIR="${HOME}/.claude/logs"
LOG_FILE="${LOG_DIR}/tool-usage.log"
METRICS_FILE="${LOG_DIR}/tool-metrics.jsonl"
ALERT_THRESHOLD_MS=30000  # Alert if tool takes longer than 30 seconds
ERROR_LOG="${LOG_DIR}/tool-errors.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
TIMESTAMP_ISO=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

# Extract tool info (with fallbacks)
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
TOOL_INPUT="${CLAUDE_TOOL_INPUT:-{}}"
TOOL_OUTPUT="${CLAUDE_TOOL_OUTPUT:-}"
EXIT_CODE="${CLAUDE_TOOL_EXIT_CODE:-0}"
DURATION="${CLAUDE_TOOL_DURATION:-0}"
SESSION_ID="${CLAUDE_SESSION_ID:-no-session}"

# =============================================================================
# LOGGING
# =============================================================================

# Log completion to standard log
log_completion() {
    local status="SUCCESS"
    [[ "$EXIT_CODE" != "0" ]] && status="FAILED"

    echo "[${TIMESTAMP}] COMPLETED SESSION=${SESSION_ID} TOOL=${TOOL_NAME} STATUS=${status} EXIT=${EXIT_CODE} DURATION=${DURATION}ms" >> "$LOG_FILE"
}

# Log metrics in JSONL format for analysis
log_metrics() {
    local output_length=${#TOOL_OUTPUT}
    local input_summary
    input_summary=$(echo "$TOOL_INPUT" | jq -c '.' 2>/dev/null || echo '{}')

    cat >> "$METRICS_FILE" << EOF
{"timestamp":"${TIMESTAMP_ISO}","session":"${SESSION_ID}","tool":"${TOOL_NAME}","exit_code":${EXIT_CODE},"duration_ms":${DURATION},"output_length":${output_length},"input":${input_summary}}
EOF
}

# Log to stderr (visible to user in verbose mode)
log_debug() {
    echo "[post-hook] $1" >&2
}

# =============================================================================
# ERROR HANDLING
# =============================================================================

# Log errors with context
log_error() {
    if [[ "$EXIT_CODE" != "0" ]]; then
        cat >> "$ERROR_LOG" << EOF

================================================================================
[${TIMESTAMP}] Tool Execution Failed
================================================================================
Session:  ${SESSION_ID}
Tool:     ${TOOL_NAME}
Exit:     ${EXIT_CODE}
Duration: ${DURATION}ms
Input:    ${TOOL_INPUT}
Output:   ${TOOL_OUTPUT:0:1000}
================================================================================
EOF
        log_debug "ERROR: Tool $TOOL_NAME failed with exit code $EXIT_CODE"
    fi
}

# =============================================================================
# ALERTING
# =============================================================================

# Alert on slow operations
check_performance() {
    if [[ "$DURATION" -gt "$ALERT_THRESHOLD_MS" ]]; then
        log_debug "WARNING: Tool $TOOL_NAME took ${DURATION}ms (threshold: ${ALERT_THRESHOLD_MS}ms)"

        # Could integrate with notification systems here:
        # curl -X POST "https://your-webhook.com/alert" -d "{\"tool\": \"$TOOL_NAME\", \"duration\": $DURATION}"
    fi
}

# Alert on specific tool failures
check_critical_failures() {
    local critical_tools=(
        "Bash"
        "Write"
        "Edit"
    )

    if [[ "$EXIT_CODE" != "0" ]]; then
        for tool in "${critical_tools[@]}"; do
            if [[ "$TOOL_NAME" == "$tool" ]]; then
                log_debug "CRITICAL: Essential tool $TOOL_NAME failed"
                # Could send alert here
            fi
        done
    fi
}

# =============================================================================
# ACTIONS
# =============================================================================

# Track file modifications
track_file_changes() {
    if [[ "$TOOL_NAME" == "Write" ]] || [[ "$TOOL_NAME" == "Edit" ]]; then
        local file_path
        file_path=$(echo "$TOOL_INPUT" | jq -r '.file_path // empty' 2>/dev/null || echo "")

        if [[ -n "$file_path" ]] && [[ "$EXIT_CODE" == "0" ]]; then
            echo "[${TIMESTAMP}] FILE_MODIFIED ${file_path}" >> "${LOG_DIR}/file-changes.log"
        fi
    fi
}

# Track git operations
track_git_operations() {
    if [[ "$TOOL_NAME" == "Bash" ]]; then
        local command
        command=$(echo "$TOOL_INPUT" | jq -r '.command // empty' 2>/dev/null || echo "")

        if [[ "$command" == git* ]]; then
            echo "[${TIMESTAMP}] GIT_OP ${command}" >> "${LOG_DIR}/git-operations.log"
        fi
    fi
}

# =============================================================================
# SUMMARY STATISTICS
# =============================================================================

# Update session statistics
update_session_stats() {
    local stats_file="${LOG_DIR}/session-${SESSION_ID}-stats.json"

    # Create or update stats file
    if [[ -f "$stats_file" ]]; then
        # Read existing stats and update
        local existing
        existing=$(cat "$stats_file")
        local tool_count
        tool_count=$(echo "$existing" | jq '.tool_count + 1')
        local total_duration
        total_duration=$(echo "$existing" | jq ".total_duration_ms + ${DURATION}")
        local error_count
        error_count=$(echo "$existing" | jq ".error_count + $([ "$EXIT_CODE" != "0" ] && echo 1 || echo 0)")

        cat > "$stats_file" << EOF
{
  "session_id": "${SESSION_ID}",
  "tool_count": ${tool_count},
  "total_duration_ms": ${total_duration},
  "error_count": ${error_count},
  "last_tool": "${TOOL_NAME}",
  "last_updated": "${TIMESTAMP_ISO}"
}
EOF
    else
        # Create new stats file
        cat > "$stats_file" << EOF
{
  "session_id": "${SESSION_ID}",
  "tool_count": 1,
  "total_duration_ms": ${DURATION},
  "error_count": $([ "$EXIT_CODE" != "0" ] && echo 1 || echo 0),
  "last_tool": "${TOOL_NAME}",
  "last_updated": "${TIMESTAMP_ISO}"
}
EOF
    fi
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    # Core logging
    log_completion
    log_metrics
    log_error

    # Performance monitoring
    check_performance
    check_critical_failures

    # Action tracking
    track_file_changes
    track_git_operations

    # Update statistics
    update_session_stats

    # Log success
    log_debug "Post-hook completed for $TOOL_NAME (${DURATION}ms, exit: ${EXIT_CODE})"

    exit 0
}

main "$@"
