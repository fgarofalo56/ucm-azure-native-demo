#!/usr/bin/env bash
# =============================================================================
# seed-data.sh - Seed realistic FSIS investigation data for local development
#
# Creates investigation records based on actual FSIS (Food Safety and
# Inspection Service) programs and downloads real public FSIS documents
# from https://www.fsis.usda.gov/science-data for use as demo uploads.
#
# Usage:
#   ./seed-data.sh                  # Full run: download files + create investigations + upload
#   ./seed-data.sh --download-only  # Only download FSIS files (no API calls)
#   ./seed-data.sh --skip-download  # Skip downloads if files already exist
#   ./seed-data.sh --help           # Show usage
#
# Environment variables:
#   API_URL       - Base API URL (default: http://localhost:8000/api/v1)
#   AUTH_TOKEN    - JWT Bearer token for authenticated endpoints
#   DOWNLOAD_DIR  - Directory for downloaded FSIS files (default: temp/fsis-demo-data)
# =============================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_URL="${API_URL:-http://localhost:8000/api/v1}"
DOWNLOAD_DIR="${DOWNLOAD_DIR:-temp/fsis-demo-data}"
AUTH_TOKEN="${AUTH_TOKEN:-}"
CURL_TIMEOUT=60
DOWNLOAD_TIMEOUT=120

# Colors for output (disabled when not a terminal)
if [ -t 1 ]; then
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  RED='\033[0;31m'
  BLUE='\033[0;34m'
  CYAN='\033[0;36m'
  NC='\033[0m'
else
  GREEN='' YELLOW='' RED='' BLUE='' CYAN='' NC=''
fi

# ---------------------------------------------------------------------------
# FSIS Source Files (real public URLs from fsis.usda.gov/science-data)
# ---------------------------------------------------------------------------
# Each entry: "LOCAL_FILENAME|URL|DESCRIPTION"
FSIS_FILES=(
  "MPI_Directory_by_Establishment_Number.csv|https://www.fsis.usda.gov/sites/default/files/media_file/documents/MPI_Directory_by_Establishment_Number.csv|MPI Directory - By Establishment Number"
  "MPI_Directory_by_Establishment_Name.csv|https://www.fsis.usda.gov/sites/default/files/media_file/documents/MPI_Directory_by_Establishment_Name.csv|MPI Directory - By Establishment Name"
  "FSIS-Annual-Sampling-Plan-FY2025.pdf|https://www.fsis.usda.gov/sites/default/files/media_file/documents/FSIS-Annual-Sampling-Plan-FY2025.pdf|FSIS Annual Sampling Plan FY2025"
  "FSIS-Annual-Sampling-Plan-FY2024.pdf|https://www.fsis.usda.gov/sites/default/files/media_file/documents/FSIS-Annual-Sampling-Plan-FY2024.pdf|FSIS Annual Sampling Plan FY2024"
  "FY2024A_Sampling_Summary_Report.pdf|https://www.fsis.usda.gov/sites/default/files/media_file/documents/FY2024A_Sampling%20Summary%20Report.pdf|FY2024A Sampling Summary Report"
  "FY2021-Sampling-Summary-Report.pdf|https://www.fsis.usda.gov/sites/default/files/media_file/2022-02/FY2021-Sampling-Summary-Report.pdf|FY2021 Sampling Summary Report"
  "FY2019-Red-Book.pdf|https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/fy2019-red-book.pdf|FY2019 FSIS Red Book"
  "2019-Blue-Book.pdf|https://www.fsis.usda.gov/sites/default/files/media_file/2020-07/2019-blue-book.pdf|2019 FSIS Blue Book"
  "CSV_Guide.pdf|https://www.fsis.usda.gov/sites/default/files/media_file/documents/CSV_Guide.pdf|CSV Data Guide"
  "Residue_Tolerances_SummaryReport_FY23Q2.pdf|https://www.fsis.usda.gov/sites/default/files/media_file/documents/Dataset_QSR_Residue_Tolerances_SummaryReport_FY23Q2.pdf|QSR Residue Tolerances Summary Report FY23 Q2"
)

# ---------------------------------------------------------------------------
# Investigation Definitions (realistic FSIS investigation types)
#
# Each entry: "RECORD_ID|TITLE|DESCRIPTION|STATUS|FILE_INDICES"
#   FILE_INDICES is a comma-separated list of indices into FSIS_FILES (0-based)
# ---------------------------------------------------------------------------
INVESTIGATIONS=(
  "INVESTIGATION-10001|FY2025 Annual Sampling Program|Annual microbiological and chemical sampling program for federally inspected meat, poultry, and processed egg products establishments. Covers FSIS routine and risk-based sampling across all districts per the FY2025 Sampling Plan directive.|active|2,4"
  "INVESTIGATION-10002|National Residue Program - Chemical Testing Q2|Quarterly residue monitoring and surveillance testing under the National Residue Program (NRP). Evaluates compliance with established tolerances for veterinary drugs, pesticides, and environmental contaminants in meat and poultry products.|active|9,7"
  "INVESTIGATION-10003|Microbiology Baseline Data Collection - Poultry|Baseline survey for Salmonella and Campylobacter prevalence in young chicken carcasses and comminuted poultry. Data supports performance standards updates and risk assessment modeling per FSIS Directive 10,250.2.|active|3,5"
  "INVESTIGATION-10004|Humane Handling Verification - District 50|Systematic review of humane handling and slaughter compliance at federally inspected establishments within District 50. Encompasses ante-mortem and post-mortem inspection observations, PHIS data analysis, and Humane Activities Tracking records.|active|6,8"
  "INVESTIGATION-10005|MPI Directory Establishment Audit|Comprehensive audit of the Meat, Poultry, and Egg Products Inspection (MPI) Directory. Cross-references establishment numbers, grant details, and operational status against current FSIS records to identify discrepancies and ensure directory accuracy.|active|0,1"
  "INVESTIGATION-10006|Quarterly Enforcement Review FY2024|Review of enforcement, investigations, and analysis activities for FY2024. Includes Noncompliance Records (NRs), Notice of Intended Enforcement (NOIEs), and suspension actions. Covers administrative enforcement, recall activities, and criminal referrals.|active|3,4"
  "INVESTIGATION-10007|STEC Sampling Results Analysis|Analysis of Shiga toxin-producing Escherichia coli (STEC) sampling results from raw beef manufacturing and trim operations. Reviews positive confirmation rates, establishment categorization, and follow-up sampling per FSIS Directive 10,010.3.|active|2,5"
  "INVESTIGATION-10008|Import Sampling Program Compliance|Assessment of imported meat, poultry, and egg products sampling at ports of entry. Evaluates reinspection results, country-of-origin compliance, and equivalence determinations for foreign food safety systems under FSIS import regulations (9 CFR 327/381).|active|6,7"
)

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

log_info() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
  echo -e "${GREEN}[OK]${NC}   $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERR]${NC}  $1"
}

log_step() {
  echo ""
  echo -e "${CYAN}=== $1 ===${NC}"
}

show_usage() {
  echo "Usage: $(basename "$0") [OPTIONS]"
  echo ""
  echo "Seed realistic FSIS investigation data for local development."
  echo ""
  echo "Options:"
  echo "  --download-only   Only download FSIS files, skip API calls"
  echo "  --skip-download   Skip file downloads (use existing files in ${DOWNLOAD_DIR})"
  echo "  --dry-run         Show what would be done without making changes"
  echo "  --help            Show this help message"
  echo ""
  echo "Environment variables:"
  echo "  API_URL       Base API URL (default: http://localhost:8000/api/v1)"
  echo "  AUTH_TOKEN    JWT Bearer token for authenticated API calls"
  echo "  DOWNLOAD_DIR  Download directory (default: temp/fsis-demo-data)"
  echo ""
  echo "Examples:"
  echo "  # Download files only"
  echo "  ./seed-data.sh --download-only"
  echo ""
  echo "  # Full seed with auth token"
  echo "  AUTH_TOKEN=\$(az account get-access-token --query accessToken -o tsv) ./seed-data.sh"
  echo ""
  echo "  # Skip downloads, just create investigations and upload existing files"
  echo "  AUTH_TOKEN=eyJ... ./seed-data.sh --skip-download"
}

# Build the auth header if a token is provided
auth_header() {
  if [ -n "${AUTH_TOKEN}" ]; then
    echo "-H" "Authorization: Bearer ${AUTH_TOKEN}"
  fi
}

# Make an API call and return the HTTP status code + body
# Usage: api_call METHOD ENDPOINT [DATA]
api_call() {
  local method="$1"
  local endpoint="$2"
  local data="${3:-}"
  local url="${API_URL}${endpoint}"

  local -a curl_args=(
    -s -w "\n%{http_code}"
    --max-time "${CURL_TIMEOUT}"
    -X "${method}"
  )

  if [ -n "${AUTH_TOKEN}" ]; then
    curl_args+=(-H "Authorization: Bearer ${AUTH_TOKEN}")
  fi

  if [ -n "${data}" ]; then
    curl_args+=(-H "Content-Type: application/json" -d "${data}")
  fi

  curl_args+=("${url}")

  local response
  response=$(curl "${curl_args[@]}" 2>/dev/null) || {
    echo "000"
    return 1
  }

  echo "${response}"
}

# Upload a file to an investigation
# Usage: upload_file INVESTIGATION_UUID FILE_PATH
upload_file() {
  local inv_uuid="$1"
  local file_path="$2"
  local filename
  filename=$(basename "${file_path}")
  local url="${API_URL}/documents/upload/${inv_uuid}"

  local -a curl_args=(
    -s -w "\n%{http_code}"
    --max-time "${CURL_TIMEOUT}"
    -X POST
    -F "file=@${file_path}"
  )

  if [ -n "${AUTH_TOKEN}" ]; then
    curl_args+=(-H "Authorization: Bearer ${AUTH_TOKEN}")
  fi

  curl_args+=("${url}")

  local response
  response=$(curl "${curl_args[@]}" 2>/dev/null) || {
    echo "000"
    return 1
  }

  echo "${response}"
}

# Check if an investigation with a given record_id already exists
# Returns the investigation UUID if found, empty string otherwise
check_investigation_exists() {
  local record_id="$1"
  local response
  response=$(api_call GET "/investigations/?page=1&page_size=100")

  local http_code
  http_code=$(echo "${response}" | tail -1)

  if [ "${http_code}" != "200" ]; then
    echo ""
    return
  fi

  local body
  body=$(echo "${response}" | sed '$d')

  # Extract UUID for matching record_id using basic text parsing
  # Look for the record_id in the response and extract the corresponding id
  local uuid
  uuid=$(echo "${body}" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for inv in data.get('data', []):
        if inv.get('record_id') == '${record_id}':
            print(inv['id'])
            break
except:
    pass
" 2>/dev/null) || true

  echo "${uuid}"
}

# ---------------------------------------------------------------------------
# Download Functions
# ---------------------------------------------------------------------------

download_fsis_files() {
  log_step "Downloading FSIS Source Files"
  log_info "Target directory: ${DOWNLOAD_DIR}"

  mkdir -p "${DOWNLOAD_DIR}"

  local total=${#FSIS_FILES[@]}
  local downloaded=0
  local skipped=0
  local failed=0

  for entry in "${FSIS_FILES[@]}"; do
    IFS='|' read -r filename url description <<< "${entry}"
    local filepath="${DOWNLOAD_DIR}/${filename}"

    if [ -f "${filepath}" ] && [ -s "${filepath}" ]; then
      log_success "Already exists: ${filename}"
      ((skipped++))
      continue
    fi

    log_info "Downloading: ${description}"
    log_info "  URL: ${url}"

    if curl -fSL --max-time "${DOWNLOAD_TIMEOUT}" \
         --retry 2 --retry-delay 5 \
         -o "${filepath}" \
         "${url}" 2>/dev/null; then
      local size
      size=$(wc -c < "${filepath}" 2>/dev/null | tr -d ' ')
      local size_human
      if [ "${size}" -gt 1048576 ]; then
        size_human="$(( size / 1048576 )) MB"
      elif [ "${size}" -gt 1024 ]; then
        size_human="$(( size / 1024 )) KB"
      else
        size_human="${size} bytes"
      fi
      log_success "Downloaded: ${filename} (${size_human})"
      ((downloaded++))
    else
      log_error "Failed to download: ${filename}"
      # Remove partial download
      rm -f "${filepath}"
      ((failed++))
    fi
  done

  echo ""
  log_info "Download summary: ${downloaded} downloaded, ${skipped} skipped (already exist), ${failed} failed"

  if [ "${failed}" -gt 0 ]; then
    log_warn "Some downloads failed. The script will continue but those files will not be uploaded."
  fi
}

# ---------------------------------------------------------------------------
# Investigation Seeding Functions
# ---------------------------------------------------------------------------

create_investigations() {
  log_step "Creating FSIS Investigation Records"
  log_info "API endpoint: ${API_URL}"

  if [ -z "${AUTH_TOKEN}" ]; then
    log_warn "No AUTH_TOKEN set. API calls requiring authentication may fail."
    log_info "Set AUTH_TOKEN or run: export AUTH_TOKEN=\$(az account get-access-token --resource api://YOUR_CLIENT_ID --query accessToken -o tsv)"
  fi

  # First verify API connectivity
  log_info "Checking API health..."
  local health_response
  health_response=$(curl -s --max-time 10 "${API_URL}/health" 2>/dev/null) || {
    log_error "Cannot reach API at ${API_URL}/health"
    log_error "Make sure the backend is running: cd src/backend && uvicorn app.main:app --reload"
    return 1
  }
  log_success "API is reachable"

  local total=${#INVESTIGATIONS[@]}
  local created=0
  local skipped=0
  local failed=0

  # Declare associative array for investigation UUIDs (record_id -> uuid)
  declare -A INV_UUIDS

  for entry in "${INVESTIGATIONS[@]}"; do
    IFS='|' read -r record_id title description inv_status file_indices <<< "${entry}"

    log_info "Processing: ${record_id} - ${title}"

    # Check if investigation already exists (idempotency)
    local existing_uuid
    existing_uuid=$(check_investigation_exists "${record_id}")

    if [ -n "${existing_uuid}" ]; then
      log_success "Already exists: ${record_id} (${existing_uuid})"
      INV_UUIDS["${record_id}"]="${existing_uuid}"
      ((skipped++))
      continue
    fi

    # Create the investigation via API (use python3 for safe JSON encoding)
    local payload
    payload=$(python3 -c "
import json, sys
print(json.dumps({
    'record_id': sys.argv[1],
    'title': sys.argv[2],
    'description': sys.argv[3]
}))
" "${record_id}" "${title}" "${description}" 2>/dev/null)

    local response
    response=$(api_call POST "/investigations/" "${payload}")

    local http_code
    http_code=$(echo "${response}" | tail -1)
    local body
    body=$(echo "${response}" | sed '$d')

    case "${http_code}" in
      201)
        local uuid
        uuid=$(echo "${body}" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null) || true
        if [ -n "${uuid}" ]; then
          INV_UUIDS["${record_id}"]="${uuid}"
          log_success "Created: ${record_id} -> ${uuid}"
          ((created++))
        else
          log_error "Created but could not parse UUID for ${record_id}"
          ((failed++))
        fi
        ;;
      409)
        log_success "Already exists (409): ${record_id}"
        # Try to retrieve the UUID from list endpoint
        existing_uuid=$(check_investigation_exists "${record_id}")
        if [ -n "${existing_uuid}" ]; then
          INV_UUIDS["${record_id}"]="${existing_uuid}"
        fi
        ((skipped++))
        ;;
      401|403)
        log_error "Authentication failed (${http_code}) for ${record_id}. Check AUTH_TOKEN."
        ((failed++))
        ;;
      *)
        log_error "Failed to create ${record_id} (HTTP ${http_code}): ${body}"
        ((failed++))
        ;;
    esac
  done

  echo ""
  log_info "Investigation summary: ${created} created, ${skipped} skipped (already exist), ${failed} failed"

  # Export the associative array for upload phase
  # Store UUIDs in a temp file for the upload phase
  local uuid_map_file="${DOWNLOAD_DIR}/.inv_uuid_map"
  > "${uuid_map_file}"
  for key in "${!INV_UUIDS[@]}"; do
    echo "${key}=${INV_UUIDS[${key}]}" >> "${uuid_map_file}"
  done
}

# ---------------------------------------------------------------------------
# Document Upload Functions
# ---------------------------------------------------------------------------

upload_documents() {
  log_step "Uploading FSIS Documents to Investigations"

  if [ -z "${AUTH_TOKEN}" ]; then
    log_warn "No AUTH_TOKEN set. Document upload requires authentication."
    log_warn "Skipping uploads. Set AUTH_TOKEN and re-run, or use --skip-download."
    return 0
  fi

  local uuid_map_file="${DOWNLOAD_DIR}/.inv_uuid_map"
  if [ ! -f "${uuid_map_file}" ]; then
    log_error "Investigation UUID map not found. Run investigation creation first."
    return 1
  fi

  # Load the UUID map
  declare -A INV_UUIDS
  while IFS='=' read -r key value; do
    INV_UUIDS["${key}"]="${value}"
  done < "${uuid_map_file}"

  local total_uploads=0
  local uploaded=0
  local upload_skipped=0
  local upload_failed=0

  for entry in "${INVESTIGATIONS[@]}"; do
    IFS='|' read -r record_id title description inv_status file_indices <<< "${entry}"

    local inv_uuid="${INV_UUIDS[${record_id}]:-}"
    if [ -z "${inv_uuid}" ]; then
      log_warn "No UUID found for ${record_id}, skipping uploads for this investigation"
      continue
    fi

    log_info "Uploading files for: ${record_id} - ${title}"

    # Parse the comma-separated file indices
    IFS=',' read -ra indices <<< "${file_indices}"
    for idx in "${indices[@]}"; do
      idx=$(echo "${idx}" | tr -d ' ')
      local file_entry="${FSIS_FILES[${idx}]}"
      IFS='|' read -r filename url file_description <<< "${file_entry}"
      local filepath="${DOWNLOAD_DIR}/${filename}"

      if [ ! -f "${filepath}" ] || [ ! -s "${filepath}" ]; then
        log_warn "File not found or empty: ${filename} (skipping)"
        ((upload_skipped++))
        continue
      fi

      ((total_uploads++))

      log_info "  Uploading: ${filename} -> ${record_id}"

      local response
      response=$(upload_file "${inv_uuid}" "${filepath}")

      local http_code
      http_code=$(echo "${response}" | tail -1)
      local body
      body=$(echo "${response}" | sed '$d')

      case "${http_code}" in
        201)
          local file_id
          file_id=$(echo "${body}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('file_id','?'))" 2>/dev/null) || true
          log_success "  Uploaded: ${filename} (file_id: ${file_id})"
          ((uploaded++))
          ;;
        401|403)
          log_error "  Auth failed (${http_code}) uploading ${filename}"
          ((upload_failed++))
          ;;
        413)
          log_warn "  File too large: ${filename}"
          ((upload_skipped++))
          ;;
        *)
          log_error "  Failed (HTTP ${http_code}): ${filename}"
          ((upload_failed++))
          ;;
      esac
    done
  done

  echo ""
  log_info "Upload summary: ${uploaded} uploaded, ${upload_skipped} skipped, ${upload_failed} failed (${total_uploads} total attempted)"
}

# ---------------------------------------------------------------------------
# Dry Run
# ---------------------------------------------------------------------------

dry_run() {
  log_step "Dry Run - Showing Planned Actions"

  echo ""
  echo "Files to download (${#FSIS_FILES[@]} total):"
  for entry in "${FSIS_FILES[@]}"; do
    IFS='|' read -r filename url description <<< "${entry}"
    echo "  - ${filename}"
    echo "    ${description}"
    echo "    ${url}"
  done

  echo ""
  echo "Investigations to create (${#INVESTIGATIONS[@]} total):"
  for entry in "${INVESTIGATIONS[@]}"; do
    IFS='|' read -r record_id title description inv_status file_indices <<< "${entry}"
    echo ""
    echo "  ${record_id}: ${title}"
    echo "    Status: ${inv_status}"
    echo "    Description: ${description:0:100}..."
    echo "    Files to attach:"
    IFS=',' read -ra indices <<< "${file_indices}"
    for idx in "${indices[@]}"; do
      idx=$(echo "${idx}" | tr -d ' ')
      local file_entry="${FSIS_FILES[${idx}]}"
      IFS='|' read -r filename url file_description <<< "${file_entry}"
      echo "      - ${filename} (${file_description})"
    done
  done

  echo ""
  log_info "No changes were made (dry run)."
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

main() {
  local download_only=false
  local skip_download=false
  local dry_run_mode=false

  # Parse arguments
  while [ $# -gt 0 ]; do
    case "$1" in
      --download-only)
        download_only=true
        shift
        ;;
      --skip-download)
        skip_download=true
        shift
        ;;
      --dry-run)
        dry_run_mode=true
        shift
        ;;
      --help|-h)
        show_usage
        exit 0
        ;;
      *)
        log_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
    esac
  done

  echo ""
  echo -e "${CYAN}============================================================${NC}"
  echo -e "${CYAN}  FSIS Demo Data Seeder - AssuranceNet UCM                  ${NC}"
  echo -e "${CYAN}============================================================${NC}"
  echo ""
  log_info "API URL:      ${API_URL}"
  log_info "Download Dir: ${DOWNLOAD_DIR}"
  log_info "Auth Token:   ${AUTH_TOKEN:+set (${#AUTH_TOKEN} chars)}${AUTH_TOKEN:-NOT SET}"

  # Dry run mode
  if [ "${dry_run_mode}" = true ]; then
    dry_run
    exit 0
  fi

  # Download-only mode
  if [ "${download_only}" = true ]; then
    download_fsis_files
    echo ""
    log_success "Download-only mode complete. Files are in: ${DOWNLOAD_DIR}"
    echo ""
    echo "To complete seeding, run again without --download-only:"
    echo "  AUTH_TOKEN=<your-token> $(basename "$0") --skip-download"
    exit 0
  fi

  # Full run or skip-download
  if [ "${skip_download}" = true ]; then
    if [ ! -d "${DOWNLOAD_DIR}" ]; then
      log_error "Download directory does not exist: ${DOWNLOAD_DIR}"
      log_error "Run with --download-only first, or without --skip-download."
      exit 1
    fi
    log_info "Skipping downloads (using existing files)"
  else
    download_fsis_files
  fi

  # Create investigations
  create_investigations

  # Upload documents
  upload_documents

  # Final summary
  log_step "Seed Complete"
  echo ""
  echo "Investigations created:"
  for entry in "${INVESTIGATIONS[@]}"; do
    IFS='|' read -r record_id title description inv_status file_indices <<< "${entry}"
    echo "  ${record_id}: ${title}"
  done
  echo ""
  echo "Downloaded FSIS files are in: ${DOWNLOAD_DIR}/"
  echo ""
  log_info "View investigations: ${API_URL}/investigations/"
  log_info "View API docs:       ${API_URL/\/api\/v1/}/docs"
  echo ""
}

main "$@"
