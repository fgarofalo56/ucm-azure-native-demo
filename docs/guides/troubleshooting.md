[Home](../../README.md) > [Guides](.) > **Troubleshooting Guide**

# AssuranceNet Document Management System - Troubleshooting Guide

> **TL;DR:** Comprehensive troubleshooting guide for the AssuranceNet platform covering authentication, uploads, PDF conversion, database, storage, networking, monitoring, local development, and CI/CD issues. Each section includes symptoms, root causes, diagnostic KQL queries, and step-by-step solutions. For operational procedures, see [Operations Guide](operations-guide.md). For incident response, see [Incident Response Runbook](../runbooks/incident-response.md).

This guide covers common issues across the AssuranceNet Document Management System, organized by functional area. Each issue includes symptoms, root causes, diagnostic steps, and solutions.

**System components**: React SPA (Static Web Apps) / FastAPI backend (App Service) / Azure Functions (PDF conversion) / Gotenberg (Container Apps) / Azure Blob Storage / Azure SQL / Entra ID / Event Grid / Front Door + WAF / Application Insights / Log Analytics / Splunk via Event Hub.

> [!TIP]
> Start with the [Quick Reference: Diagnostic Commands](#-quick-reference-diagnostic-commands) section at the bottom for a fast overview of health checks, KQL queries, and CLI commands.

---

## Table of Contents

1. [Authentication & Authorization Issues](#-1-authentication--authorization-issues)
2. [Document Upload Issues](#-2-document-upload-issues)
3. [PDF Conversion Issues](#-3-pdf-conversion-issues)
4. [PDF Merge Issues](#-4-pdf-merge-issues)
5. [Database Issues](#%EF%B8%8F-5-database-issues)
6. [Storage Issues](#-6-storage-issues)
7. [Infrastructure / Networking Issues](#-7-infrastructure--networking-issues)
8. [Monitoring & Logging Issues](#-8-monitoring--logging-issues)
9. [Local Development Issues](#%EF%B8%8F-9-local-development-issues)
10. [CI/CD Pipeline Issues](#-10-cicd-pipeline-issues)
11. [Quick Reference: Diagnostic Commands](#-quick-reference-diagnostic-commands)
12. [Escalation Path](#-escalation-path)

---

## 🔐 1. Authentication & Authorization Issues

### 1.1 "Unable to sign in" / Redirect loop

**Symptoms:**
- Browser redirects repeatedly between the app and `login.microsoftonline.com`.
- MSAL throws an `interaction_required` or `BrowserAuthError` in the browser console.
- The page never finishes loading after clicking "Sign in".

**Causes:**
- `VITE_REDIRECT_URI` (set at build time) does not match the redirect URI registered in the Entra ID app registration.
- `VITE_ENTRA_TENANT_ID` or `VITE_ENTRA_CLIENT_ID` are empty or incorrect.
- `VITE_AUTHORITY_HOST` points to the wrong cloud (`login.microsoftonline.com` vs. `login.microsoftonline.us` for GovCloud).
- Stale MSAL state in `sessionStorage` after a config change or failed auth attempt.
- Third-party cookie blocking in the browser prevents MSAL from completing the token exchange.

**Diagnostic steps:**

```bash
# Check what redirect URIs are registered on the app registration
az ad app show --id <CLIENT_ID> --query "web.redirectUris"

# Check the SPA redirect URIs (MSAL uses SPA platform)
az ad app show --id <CLIENT_ID> --query "spa.redirectUris"
```

In the browser developer console:

```javascript
// Check current MSAL config
console.log(sessionStorage);  // Look for msal.* keys with stale state

// Check what redirect URI MSAL is using
// Look for the redirect_uri parameter in the authentication request URL
```

**Solutions:**

1. **Verify redirect URI match.** The value of `VITE_REDIRECT_URI` (defaults to `window.location.origin`) must exactly match one of the redirect URIs registered under **Authentication > Single-page application** in the Entra ID app registration. Trailing slashes matter.

2. **Clear browser session state.** Open DevTools > Application > Session Storage and delete all `msal.*` keys, then try again.

3. **Verify environment variables.** Confirm all `VITE_*` values are set correctly in the Static Web App configuration or `.env` file:
   ```
   VITE_ENTRA_TENANT_ID=<your-tenant-id>
   VITE_ENTRA_CLIENT_ID=<your-client-id>
   VITE_REDIRECT_URI=https://your-app-domain.com
   VITE_AUTHORITY_HOST=https://login.microsoftonline.com
   VITE_API_SCOPE=api://assurancenet-api/Documents.ReadWrite
   ```

4. **Check browser cookie settings.** If using Chrome with strict cookie blocking, MSAL redirect flow may fail. Test in a private window or temporarily allow third-party cookies for `login.microsoftonline.com`.

5. **Verify the authority host matches the cloud environment.** Commercial: `https://login.microsoftonline.com`. GovCloud: `https://login.microsoftonline.us`.

---

### 1.2 "Access Denied" / 403 on API calls

**Symptoms:**
- API calls return `403 Forbidden` with body `{"detail": "Insufficient permissions"}`.
- The user can sign in successfully but cannot perform certain operations.

**Causes:**
- The user has not been assigned the required app role (`Documents.Reader`, `Documents.Contributor`, `Investigations.Manager`, or `Admin`) in Entra ID.
- The JWT token's `roles` claim is empty or does not include the role required by the endpoint.
- The `audience` claim in the token does not match the backend's `ENTRA_AUDIENCE` setting (`api://assurancenet-api`).

**Diagnostic steps:**

```bash
# List app role assignments for a specific user
az ad app show --id <CLIENT_ID> --query "appRoles"

# Check user's role assignments on the service principal
az ad sp show --id <CLIENT_ID> --query "appRoles[].{Name:displayName, Id:id, Value:value}"
```

Decode the JWT at [jwt.ms](https://jwt.ms) and check:
- `aud` (audience) matches `ENTRA_AUDIENCE`
- `roles` array contains the expected role
- `iss` (issuer) matches `https://login.microsoftonline.com/{tenant-id}/v2.0`

```kql
// KQL: Check authorization failures in Application Insights
AppTraces
| where TimeGenerated > ago(1h)
| where Message contains "authorization_denied"
| project TimeGenerated, Message, Properties
| order by TimeGenerated desc
```

**Solutions:**

1. **Assign the user to the correct app role.** In Azure Portal: Entra ID > Enterprise Applications > AssuranceNet API > Users and Groups > Add Assignment. Select the user and assign the appropriate role.

2. **Verify audience configuration.** The backend expects `ENTRA_AUDIENCE=api://assurancenet-api`. The frontend requests a token with scope `api://assurancenet-api/Documents.ReadWrite`. These must be consistent with the app registration's **Expose an API** settings.

3. **Force a fresh token.** After role assignments change, the user must sign out and sign back in (or wait for the token to expire, typically 1 hour) to get a new token with updated claims.

4. **Check for required roles on the endpoint.** The backend uses `require_role()` dependency. For example, an endpoint guarded by `require_role("Documents.Contributor", "Admin")` rejects users who only have `Documents.Reader`.

---

### 1.3 "Invalid token" / 401 Unauthorized

**Symptoms:**
- API calls return `401 Unauthorized` with body `{"detail": "Invalid or expired token"}`.
- Browser console shows token acquisition succeeded, but API rejects it.

**Causes:**
- The access token has expired (default lifetime is 1 hour).
- The token was issued by a different tenant than `ENTRA_TENANT_ID` configured on the backend.
- The JWKS endpoint (`login.microsoftonline.com/{tenant}/discovery/v2.0/keys`) is unreachable from the App Service (network/DNS issue).
- The token's signing key (`kid`) does not match any key in the cached JWKS (key rotation occurred and cache is stale).

**Diagnostic steps:**

```bash
# Verify the backend can reach the Entra ID endpoints
az webapp ssh --resource-group rg-assurancenet-app-dev --name app-assurancenet-api-dev
# Then from the SSH session:
curl -s https://login.microsoftonline.com/<TENANT_ID>/v2.0/.well-known/openid-configuration | python3 -m json.tool
```

```kql
// KQL: Check JWT validation failures
AppTraces
| where TimeGenerated > ago(1h)
| where Message contains "jwt_validation_failed"
| project TimeGenerated, Message, Properties
| order by TimeGenerated desc
```

**Solutions:**

1. **Force re-authentication.** On the frontend, call `msalInstance.logoutRedirect()` then have the user sign in again to get a fresh token.

2. **Verify tenant ID consistency.** The backend's `ENTRA_TENANT_ID` must match the tenant the frontend authenticates against (`VITE_ENTRA_TENANT_ID`). Check both:
   ```bash
   # Backend config
   az webapp config appsettings list --name app-assurancenet-api-dev \
     --resource-group rg-assurancenet-app-dev \
     --query "[?name=='ENTRA_TENANT_ID'].value" -o tsv

   # Compare with Entra ID
   az account show --query "tenantId" -o tsv
   ```

3. **Check network access to login.microsoftonline.com.** If the App Service has VNet integration with restrictive NSGs, ensure outbound HTTPS (port 443) to `AzureActiveDirectory` service tag is allowed.

4. **Clear JWKS cache.** The backend caches JWKS keys in memory. Restart the App Service to clear the cache if a key rotation has occurred:
   ```bash
   az webapp restart --name app-assurancenet-api-dev --resource-group rg-assurancenet-app-dev
   ```

---

### 1.4 "AADSTS" Errors

Microsoft Entra ID errors use the `AADSTS` prefix. Here are the most common ones and what they mean.

#### AADSTS50011: Reply URL mismatch

**Meaning:** The redirect URI sent by the client does not match any registered redirect URI on the app registration.

**Solution:** Update the app registration to include the exact redirect URI. In Azure Portal: Entra ID > App Registrations > AssuranceNet Frontend > Authentication. Add the missing URI under **Single-page application**.

```bash
# Check registered redirect URIs
az ad app show --id <CLIENT_ID> --query "spa.redirectUris" -o json

# Add a redirect URI
az ad app update --id <CLIENT_ID> --spa-redirect-uris "https://your-app.com" "http://localhost:5173"
```

#### AADSTS65001: Consent not granted

**Meaning:** The user or admin has not consented to the permissions requested by the application.

**Solution:** An admin must grant consent for the API permissions. In Azure Portal: Entra ID > App Registrations > AssuranceNet Frontend > API Permissions > Grant admin consent.

```bash
# Grant admin consent via CLI
az ad app permission admin-consent --id <CLIENT_ID>
```

#### AADSTS700016: Application not found in tenant

**Meaning:** The `client_id` specified does not correspond to any application in the target tenant.

**Solution:** Verify the application exists in the correct tenant. Check that `VITE_ENTRA_CLIENT_ID` and `VITE_ENTRA_TENANT_ID` are correct and correspond to each other.

```bash
# Verify application exists in tenant
az ad app show --id <CLIENT_ID> 2>/dev/null && echo "Found" || echo "Not found"
```

#### AADSTS50076: MFA required

**Meaning:** Conditional Access policy requires multi-factor authentication but MFA was not completed.

**Solution:** The user must complete MFA. If MFA is not set up, the user should register at [aka.ms/mfasetup](https://aka.ms/mfasetup). MSAL should automatically handle the `interaction_required` claim and prompt for MFA -- if it does not, check that `loginRequest.scopes` is correctly configured.

#### AADSTS90002: Tenant not found

**Meaning:** The tenant ID is invalid or the tenant does not exist.

**Solution:** Verify `VITE_ENTRA_TENANT_ID` is a valid GUID. Check for typos. Confirm the tenant exists:

```bash
az account show --query tenantId -o tsv
```

---

## 📤 2. Document Upload Issues

### 2.1 Upload fails with "413 Request Entity Too Large"

**Symptoms:**
- Upload returns HTTP 413 with body `{"detail": "File exceeds maximum size of 500MB"}`.
- Large files consistently fail while smaller files succeed.

**Causes:**
- The file exceeds `MAX_UPLOAD_SIZE_MB` (default: 500 MB, configured in `app/config.py`).
- Azure Front Door has a request body size limit configured in the WAF policy.
- The App Service has a default request size limit.

**Diagnostic steps:**

```bash
# Check current configured limit
az webapp config appsettings list --name app-assurancenet-api-dev \
  --resource-group rg-assurancenet-app-dev \
  --query "[?name=='MAX_UPLOAD_SIZE_MB'].value" -o tsv

# Check Front Door WAF policy for body size limits
az network front-door waf-policy show --name <WAF_POLICY_NAME> \
  --resource-group rg-assurancenet-network-dev \
  --query "policySettings.requestBodyCheck"
```

**Solutions:**

1. **Reduce file size** before uploading. Compress images, split large documents, or remove unnecessary embedded content.

2. **Adjust the upload limit** if a larger maximum is justified:
   ```bash
   az webapp config appsettings set --name app-assurancenet-api-dev \
     --resource-group rg-assurancenet-app-dev \
     --settings MAX_UPLOAD_SIZE_MB=1000
   ```

3. **Check the App Service request size limit.** The default Kestrel/Uvicorn limit may need adjustment. For FastAPI on App Service Linux, add `--limit-max-request-size` to the startup command if needed.

4. **Check Front Door WAF body inspection limits.** Azure Front Door Premium WAF inspects request bodies up to a configurable limit (default 128 KB for rule evaluation; passthrough for larger). Ensure the WAF is not blocking the upload based on content inspection rules.

---

### 2.2 Upload fails with network error

**Symptoms:**
- Upload appears to start but fails with a generic "Network Error" or timeout.
- The browser DevTools Network tab shows the request as `(failed)` or `net::ERR_CONNECTION_RESET`.
- Smaller files upload fine but larger files fail.

**Causes:**
- The request timed out (App Service default timeout is 230 seconds).
- Azure Front Door WAF is blocking the request due to a rule match (e.g., file content triggers a SQL injection or XSS rule).
- Rate limiting on Front Door (configured at 1000 requests per minute per IP).
- The file type or content is being blocked by a managed WAF rule.

**Diagnostic steps:**

```kql
// KQL: Check WAF logs for blocked requests
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.CDN" or ResourceProvider == "MICROSOFT.NETWORK"
| where Category == "FrontDoorWebApplicationFirewallLog"
| where action_s == "Block"
| where TimeGenerated > ago(1h)
| project TimeGenerated, clientIP_s, requestUri_s, ruleName_s, action_s, details_msg_s
| order by TimeGenerated desc
```

```kql
// KQL: Check for rate limiting
AzureDiagnostics
| where Category == "FrontDoorWebApplicationFirewallLog"
| where ruleName_s contains "RateLimit"
| where TimeGenerated > ago(1h)
| project TimeGenerated, clientIP_s, action_s
```

**Solutions:**

1. **Check WAF logs** for blocked requests using the KQL query above. If a managed rule is triggering a false positive, create an exclusion in the WAF policy for the upload endpoint.

2. **Verify the content type is not blocked.** The WAF may block certain file extensions. Review the custom rules in the WAF policy:
   ```bash
   az network front-door waf-policy managed-rule-set list \
     --policy-name <WAF_POLICY_NAME> \
     --resource-group rg-assurancenet-network-dev
   ```

3. **Check rate limiting.** If the rate limit (1000 req/min) is being hit, the client will receive 429 responses. Implement exponential backoff on the frontend or adjust the rate limit rule.

4. **Increase timeouts** for large file uploads. Ensure the Front Door origin timeout and App Service request timeout are sufficient.

---

### 2.3 Upload succeeds but document doesn't appear

**Symptoms:**
- The upload API returns `201 Created` with a valid `document_id`.
- The document does not appear in the document list when the user navigates back.
- The document appears after a browser refresh (eventual consistency).

**Causes:**
- The database write succeeded but the frontend is using cached/stale data (React Query or SWR cache not invalidated).
- The SQL database write failed silently (transaction rollback) even though the blob upload succeeded.
- The readiness endpoint shows database connectivity issues.

**Diagnostic steps:**

```bash
# Check the readiness endpoint to verify database and storage health
curl -s https://app-assurancenet-api-dev.azurewebsites.net/api/v1/health/ready | python3 -m json.tool
```

```kql
// KQL: Check for database errors around the upload time
AppExceptions
| where TimeGenerated > ago(1h)
| where ExceptionType contains "SQL" or ExceptionType contains "sqlalchemy"
| project TimeGenerated, ExceptionType, OuterMessage, ProblemId
| order by TimeGenerated desc
```

**Solutions:**

1. **Check the readiness endpoint** (`GET /api/v1/health/ready`). If `database: false`, investigate SQL connectivity (see [Section 5: Database Issues](#5-database-issues)).

2. **Verify the document exists in the database:**
   ```sql
   -- Run against Azure SQL (via SSMS, Azure Data Studio, or az sql query)
   SELECT id, file_id, original_filename, created_at, pdf_conversion_status
   FROM documents
   WHERE file_id = '<file_id_from_upload_response>'
   ```

3. **Check the frontend cache invalidation.** After a successful upload, the frontend should invalidate the document list query. Verify the React Query `invalidateQueries` call is working correctly.

4. **Check for async processing delay.** The document may be in the list but with `pdf_conversion_status: "pending"` -- the conversion happens asynchronously. The UI may filter out pending documents depending on the view.

---

## 📄 3. PDF Conversion Issues

### 3.1 Document stuck on "pending" conversion

**Symptoms:**
- After uploading a non-PDF document, the `pdf_conversion_status` remains `"pending"` indefinitely.
- The converted PDF never appears in blob storage.
- No errors appear in the Function App logs.

**Causes:**
- The Event Grid system topic on the storage account is not created or is inactive.
- The Event Grid subscription filter is misconfigured (not matching the blob path or not excluding `.pdf` files).
- The Function App (`func-assurancenet-pdf-dev`) is stopped or in an error state.
- Events are being sent to the dead-letter container due to delivery failures.

**Diagnostic steps:**

```bash
# Check if the Event Grid system topic exists on the storage account
az eventgrid system-topic list --resource-group rg-assurancenet-data-dev \
  --query "[].{Name:name, Source:source, Status:provisioningState}" -o table

# Check Event Grid subscriptions
az eventgrid system-topic event-subscription list \
  --system-topic-name <SYSTEM_TOPIC_NAME> \
  --resource-group rg-assurancenet-data-dev \
  --query "[].{Name:name, Status:provisioningState, Endpoint:destination.endpointType}" -o table

# Check Function App status
az functionapp show --name func-assurancenet-pdf-dev \
  --resource-group rg-assurancenet-app-dev \
  --query "state" -o tsv

# Check Event Grid metrics for delivery failures
az monitor metrics list --resource <SYSTEM_TOPIC_RESOURCE_ID> \
  --metric "DeliveryAttemptFailCount" --interval PT1H
```

```kql
// KQL: Check Event Grid delivery metrics
AzureMetrics
| where ResourceProvider == "MICROSOFT.EVENTGRID"
| where MetricName in ("DeliverySuccessCount", "DeliveryAttemptFailCount", "DeadLetteredCount")
| where TimeGenerated > ago(4h)
| summarize Total=sum(Total) by MetricName, bin(TimeGenerated, 15m)
| order by TimeGenerated desc
```

**Solutions:**

1. **Verify the Event Grid system topic exists** on the storage account and is in `Succeeded` provisioning state. If not, recreate it:
   ```bash
   az eventgrid system-topic create \
     --name sgtopic-assurancenet-storage-dev \
     --resource-group rg-assurancenet-data-dev \
     --source /subscriptions/<SUB_ID>/resourceGroups/rg-assurancenet-data-dev/providers/Microsoft.Storage/storageAccounts/<STORAGE_NAME> \
     --topic-type Microsoft.Storage.StorageAccounts \
     --location eastus
   ```

2. **Check the subscription filter.** The subscription should filter for `Microsoft.Storage.BlobCreated` events on blobs in the `/blob/` path segment and exclude files already in the `/pdf/` path. Verify the subject filter:
   ```bash
   az eventgrid system-topic event-subscription show \
     --system-topic-name <SYSTEM_TOPIC_NAME> \
     --name <SUBSCRIPTION_NAME> \
     --resource-group rg-assurancenet-data-dev \
     --query "filter"
   ```

3. **Ensure the Function App is running:**
   ```bash
   az functionapp start --name func-assurancenet-pdf-dev --resource-group rg-assurancenet-app-dev
   ```

4. **Check the dead-letter container** for failed event deliveries. Dead-lettered events are stored in a blob container (configured on the Event Grid subscription). Download and inspect them to understand why delivery failed.

5. **Manually trigger a test.** Upload a small test file (`.txt` or `.docx`) and immediately check the Function App log stream:
   ```bash
   az functionapp log tail --name func-assurancenet-pdf-dev --resource-group rg-assurancenet-app-dev
   ```

---

### 3.2 Document shows "failed" conversion

**Symptoms:**
- The document's `pdf_conversion_status` changes to `"failed"`.
- The original file is accessible but no PDF version exists.

**Causes:**
- The file format variant is not supported by the conversion service (e.g., password-protected Office docs, corrupted files, uncommon image formats).
- Gotenberg timed out processing a very large or complex Office document (default timeout: 120 seconds).
- The original file is corrupted or zero-length.
- The Function App ran out of memory processing a large file.

**Diagnostic steps:**

```kql
// KQL: Check Function App error logs
FunctionAppLogs
| where TimeGenerated > ago(4h)
| where Level == "Error" or Level == "Warning"
| where FunctionName == "pdf_converter" or Message contains "pdf"
| project TimeGenerated, Level, Message, ExceptionDetails
| order by TimeGenerated desc
```

```kql
// KQL: Check conversion durations and failures
AppMetrics
| where Name == "pdf.conversion.duration" or Name == "pdf.conversion.status"
| where TimeGenerated > ago(4h)
| project TimeGenerated, Name, Sum, Properties
| order by TimeGenerated desc
```

```bash
# Check Gotenberg health directly (from Function App or within VNet)
curl -s http://ca-gotenberg-dev:3000/health
```

**Solutions:**

1. **Check the Function App logs** with the KQL query above. The error message will indicate whether the failure was in file download, conversion, or PDF upload.

2. **Verify Gotenberg is healthy** (see [Section 3.3](#33-gotenberg-container-not-responding)).

3. **Try re-uploading the file.** Delete the failed document and upload again. Transient network issues between Functions and Gotenberg can cause one-time failures.

4. **Check file compatibility.** The conversion pipeline supports:
   - **Office documents** (DOCX, XLSX, PPTX) via Gotenberg/LibreOffice
   - **Images** (JPEG, PNG, TIFF, BMP) via Pillow + img2pdf
   - **Text files** (TXT, RTF) via fpdf2

   Password-protected files, macro-heavy spreadsheets, and files with extensive embedded OLE objects may fail.

5. **Check file size.** Very large files (> 100 MB) may cause the Function App to run out of memory. Consider the Function App's memory allocation and increase if needed.

---

### 3.3 Gotenberg container not responding

**Symptoms:**
- Office document (DOCX, XLSX, PPTX) conversions fail consistently.
- Image and text conversions still work (they do not use Gotenberg).
- Function App logs show `RuntimeError: Gotenberg conversion failed with status <code>` or connection timeouts to Gotenberg.

**Causes:**
- The Container App (`ca-gotenberg-dev`) has scaled to zero replicas and is slow to start (cold start).
- The Gotenberg container is in a crash loop (out of memory, disk space, or a LibreOffice process zombie).
- The health probe is failing, causing the Container App to be marked unhealthy and restarted repeatedly.
- Network connectivity between the Functions subnet (`snet-functions`, `10.0.2.0/24`) and the Container Apps subnet (`snet-container-apps`, `10.0.5.0/24`) is blocked.

**Diagnostic steps:**

```bash
# Check Container App status and replica count
az containerapp show --name ca-gotenberg-dev \
  --resource-group rg-assurancenet-app-dev \
  --query "{Status:properties.runningStatus, Replicas:properties.template.scale}" -o json

# Check Container App logs
az containerapp logs show --name ca-gotenberg-dev \
  --resource-group rg-assurancenet-app-dev \
  --tail 100
```

```kql
// KQL: Check Container App logs in Log Analytics
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "ca-gotenberg-dev"
| where TimeGenerated > ago(1h)
| project TimeGenerated, Log_s, RevisionName_s
| order by TimeGenerated desc

# Check for OOM kills
ContainerAppSystemLogs_CL
| where ContainerAppName_s == "ca-gotenberg-dev"
| where Reason_s == "OOMKilled" or Log_s contains "memory"
| where TimeGenerated > ago(24h)
```

**Solutions:**

1. **Check if the container is running** and has at least one active replica:
   ```bash
   az containerapp revision list --name ca-gotenberg-dev \
     --resource-group rg-assurancenet-app-dev \
     --query "[].{Name:name, Active:properties.active, Replicas:properties.replicas}" -o table
   ```

2. **Set minimum replicas to 1** in production to avoid cold-start delays:
   ```bash
   az containerapp update --name ca-gotenberg-dev \
     --resource-group rg-assurancenet-app-dev \
     --min-replicas 1
   ```

3. **Increase memory allocation** if Gotenberg is being OOM-killed. LibreOffice conversion of complex documents can require significant memory:
   ```bash
   az containerapp update --name ca-gotenberg-dev \
     --resource-group rg-assurancenet-app-dev \
     --cpu 1.0 --memory 2.0Gi
   ```

4. **Verify the Gotenberg health probe** is configured correctly. The container exposes `/health` on port 3000:
   ```bash
   az containerapp show --name ca-gotenberg-dev \
     --resource-group rg-assurancenet-app-dev \
     --query "properties.template.containers[0].probes"
   ```

5. **Check NSG rules** between `snet-functions` and `snet-container-apps`. Traffic from the Functions subnet to port 3000 on the Container Apps subnet must be allowed.

---

### 3.4 Event Grid not triggering Functions

**Symptoms:**
- No conversion attempts at all after uploading documents.
- Function App logs show zero invocations.
- Event Grid metrics show no delivery attempts.

**Causes:**
- The Event Grid system topic does not exist on the storage account.
- The event subscription filter is wrong (path filter does not match the actual blob path structure `INVESTIGATION-{RecordId}/{FileId}/blob/{filename}`).
- The Function App is stopped or the Event Grid trigger function is disabled.
- The Function App's Event Grid endpoint is not reachable (VNet/NSG issue).

**Diagnostic steps:**

```bash
# Verify system topic exists
az eventgrid system-topic list --resource-group rg-assurancenet-data-dev -o table

# Verify subscription exists and its filter
az eventgrid system-topic event-subscription list \
  --system-topic-name <SYSTEM_TOPIC_NAME> \
  --resource-group rg-assurancenet-data-dev -o json

# Check Function App functions list (is the function registered?)
az functionapp function list --name func-assurancenet-pdf-dev \
  --resource-group rg-assurancenet-app-dev \
  --query "[].{Name:name, IsDisabled:isDisabled}" -o table

# Check Event Grid delivery metrics
az monitor metrics list \
  --resource <SYSTEM_TOPIC_RESOURCE_ID> \
  --metric "PublishSuccessCount,DeliverySuccessCount,DeliveryAttemptFailCount" \
  --interval PT1H --aggregation Total
```

**Solutions:**

1. **Create the system topic** if it does not exist (see the command in Section 3.1).

2. **Verify the subscription filter** matches the blob path pattern. The subject filter should match blobs under the `assurancenet-documents` container whose path contains `/blob/` (the original file segment):
   - Subject begins with: `/blobServices/default/containers/assurancenet-documents/blobs/`
   - Subject does not end with: `.pdf` (or use an advanced filter to exclude `/pdf/` path segments)

3. **Ensure the Function App is running and the function is enabled:**
   ```bash
   az functionapp start --name func-assurancenet-pdf-dev --resource-group rg-assurancenet-app-dev
   ```

4. **Re-register the Event Grid endpoint.** If the Function App was redeployed and the endpoint URL changed, the subscription may need updating. Delete and recreate the subscription if the endpoint validation fails.

---

### 3.5 Conversion timeout

**Symptoms:**
- Large or complex Office documents fail with a timeout error.
- Function App logs show `httpx.ReadTimeout` or `httpcore.ReadTimeout` after 120 seconds.
- Simple documents convert fine, only complex ones fail.

**Causes:**
- The Gotenberg client timeout (120 seconds in `services/gotenberg_client.py`) is too short for the file.
- The file is very large (> 50 MB) or has many pages/sheets/slides.
- Gotenberg is overloaded because multiple conversions are running concurrently.

**Solutions:**

1. **Increase the Gotenberg client timeout.** The current value is `CONVERSION_TIMEOUT = 120` seconds in `src/functions/services/gotenberg_client.py`. Consider increasing to 300 seconds for production workloads.

2. **Increase the Function App timeout.** Check `host.json` for the `functionTimeout` setting:
   ```json
   {
     "version": "2.0",
     "functionTimeout": "00:10:00"
   }
   ```

3. **Scale Gotenberg replicas** to handle concurrent conversions:
   ```bash
   az containerapp update --name ca-gotenberg-dev \
     --resource-group rg-assurancenet-app-dev \
     --max-replicas 5
   ```

4. **Split large files** before uploading. For example, split a 200-page Word document into smaller sections.

---

## 🔀 4. PDF Merge Issues

### 4.1 "At least 2 files required" / Validation error

**Symptoms:**
- Merge request returns `400 Bad Request`.
- Error indicates too few files provided.

**Causes:**
- The `file_ids` array in the `PdfMergeRequest` body contains fewer than 2 entries.
- The frontend is not correctly collecting selected document IDs.

**Solutions:**

1. **Select at least 2 documents** with completed PDF conversion before attempting a merge.

2. **Verify all selected documents have PDF available.** Documents with `pdf_conversion_status` of `"pending"` or `"failed"` cannot be included in a merge. The API will return `400` with detail: `"PDF not available for {file_id}. Status: {status}"`.

3. **Check the request payload** in the browser DevTools Network tab. The body should be:
   ```json
   {
     "file_ids": ["file-id-1", "file-id-2", "..."]
   }
   ```

---

### 4.2 Merge fails with timeout

**Symptoms:**
- Merge request hangs for a long time then returns a timeout error (504 from Front Door, or network error from the client).
- Large merge operations with many files consistently fail.

**Causes:**
- Too many files selected (exceeding `MAX_MERGE_FILES`, default: 50).
- Combined file size exceeds `MAX_MERGE_SIZE_MB` (default: 500 MB).
- Downloading all source PDFs from blob storage takes too long.
- The in-memory merge with pypdf exhausts App Service memory for very large merges.

**Diagnostic steps:**

```kql
// KQL: Check merge operation timing
AppTraces
| where TimeGenerated > ago(4h)
| where Message contains "document.merge"
| project TimeGenerated, Properties
| extend FileCount = tolong(Properties["file_count"]), MergedSize = tolong(Properties["merged_size_bytes"])
| order by TimeGenerated desc
```

**Solutions:**

1. **Reduce file count.** Stay well below the 50-file limit. For very large merges, consider splitting into batches.

2. **Reduce total size.** The API enforces a 500 MB combined limit. If individual PDFs are large, reduce their number.

3. **Increase App Service timeout.** The Front Door origin timeout and App Service request timeout may need to be increased for large merges.

4. **Monitor App Service memory** during merge operations. Large in-memory merges can cause memory pressure:
   ```kql
   // KQL: Check App Service memory usage
   AppServiceHTTPLogs
   | where TimeGenerated > ago(1h)
   | where CsUriStem contains "merge-pdf"
   | project TimeGenerated, TimeTaken, ScStatus
   ```

---

### 4.3 Merged PDF is corrupted

**Symptoms:**
- The merged PDF downloads but cannot be opened in a PDF reader.
- PDF reader shows "file is damaged" or "not a valid PDF".

**Causes:**
- One or more source PDFs are corrupted or malformed.
- A source PDF uses features that pypdf cannot handle (e.g., certain encryption, unusual PDF structures).
- The merge was interrupted mid-stream (network timeout during download).

**Diagnostic steps:**

1. Download each individual PDF and try opening it separately to identify which one is corrupted.
2. Check if the corrupted PDF was produced by the conversion pipeline (possible Gotenberg issue) or was an original upload.

**Solutions:**

1. **Identify and exclude the corrupted source file.** Download each PDF individually via `GET /api/v1/documents/{id}/pdf` and verify it opens correctly.

2. **Re-convert the source document** if the PDF was produced by the conversion pipeline. Delete and re-upload the original file.

3. **Verify source file integrity** by comparing checksums:
   ```sql
   SELECT file_id, original_filename, checksum_sha256, pdf_conversion_status, pdf_path
   FROM documents
   WHERE investigation_id = '<investigation_id>'
   AND pdf_conversion_status IN ('completed', 'not_required')
   ```

---

## 🗄️ 5. Database Issues

### 5.1 "Connection refused" / SQL connectivity

**Symptoms:**
- API returns 500 errors on all endpoints that access the database.
- Readiness endpoint (`/api/v1/health/ready`) shows `"database": false`.
- Logs show `Cannot open server` or `Connection refused` errors.

**Causes:**
- Private Endpoint DNS is not resolving correctly (Private DNS zone `privatelink.database.windows.net` not linked to the VNet).
- The Managed Identity (`mi-app-assurancenet-{env}`) is not assigned as a user on the SQL database.
- The SQL Server firewall rules block access from the App Service subnet.
- ODBC Driver 18 for SQL Server is not available in the container/environment.

**Diagnostic steps:**

```bash
# Check Private DNS zone link to VNet
az network private-dns link vnet list \
  --resource-group rg-assurancenet-network-dev \
  --zone-name privatelink.database.windows.net \
  --query "[].{Name:name, VNet:virtualNetwork.id, Status:provisioningState}" -o table

# Check SQL Server connection policy
az sql server show --name sql-assurancenet-dev \
  --resource-group rg-assurancenet-data-dev \
  --query "{FirewallRules:firewallRules, PublicAccess:publicNetworkAccess}" -o json

# Test DNS resolution from App Service
az webapp ssh --resource-group rg-assurancenet-app-dev --name app-assurancenet-api-dev
# Then:
nslookup sql-assurancenet-dev.database.windows.net
# Should resolve to a 10.0.3.x address (private endpoint), not a public IP

# Check Managed Identity role assignments on SQL
az sql server ad-admin list --server-name sql-assurancenet-dev \
  --resource-group rg-assurancenet-data-dev
```

```kql
// KQL: Check for SQL connection errors
AppExceptions
| where TimeGenerated > ago(1h)
| where ExceptionType contains "pyodbc" or ExceptionType contains "sqlalchemy" or OuterMessage contains "SQL"
| project TimeGenerated, ExceptionType, OuterMessage
| order by TimeGenerated desc
```

**Solutions:**

1. **Verify Private DNS zone configuration.** The zone `privatelink.database.windows.net` must be linked to the VNet (`vnet-assurancenet-{env}`):
   ```bash
   az network private-dns link vnet create \
     --resource-group rg-assurancenet-network-dev \
     --zone-name privatelink.database.windows.net \
     --name link-to-assurancenet-vnet \
     --virtual-network /subscriptions/<SUB_ID>/resourceGroups/rg-assurancenet-network-dev/providers/Microsoft.Network/virtualNetworks/vnet-assurancenet-dev \
     --registration-enabled false
   ```

2. **Verify Managed Identity database access.** The MI must be created as a user in the SQL database with appropriate roles:
   ```sql
   -- Run as the Entra ID admin of the SQL Server
   CREATE USER [mi-app-assurancenet-dev] FROM EXTERNAL PROVIDER;
   ALTER ROLE db_datareader ADD MEMBER [mi-app-assurancenet-dev];
   ALTER ROLE db_datawriter ADD MEMBER [mi-app-assurancenet-dev];
   ```

3. **Check SQL Server public access settings.** If public access is disabled (as expected with Private Endpoints), ensure the Private Endpoint for SQL is correctly provisioned and the A record exists in the Private DNS zone.

4. **Verify ODBC driver availability.** The App Service Linux container must have ODBC Driver 18 installed. Check the Dockerfile or startup script.

---

### 5.2 Alembic migration fails

**Symptoms:**
- `alembic upgrade head` fails with an error.
- The GitHub Actions `db-migrate` workflow fails.
- New database schema changes are not applied.

**Causes:**
- Schema conflict: the migration tries to create a table or column that already exists.
- Connection string is wrong or permissions are insufficient.
- The migration was applied out of order (revision chain is broken).

**Diagnostic steps:**

```bash
# Check current Alembic revision
cd src/backend/app/db/migrations
alembic current

# Check if there are pending migrations
alembic check

# Show migration history
alembic history --verbose
```

**Solutions:**

1. **Check the current database state** against the migration history:
   ```bash
   alembic current    # Shows what the DB thinks the current revision is
   alembic heads      # Shows what the latest migration file is
   ```

2. **If schema conflict**, stamp the database to the current state without running the migration:
   ```bash
   alembic stamp head  # Only if you've verified the schema is already correct
   ```

3. **Verify the ODBC connection string.** The backend uses `Authentication=ActiveDirectoryMsi` for Managed Identity authentication. For local development, ensure `.env` has the correct `AZURE_SQL_SERVER` and `AZURE_SQL_DATABASE` values, and you have an appropriate authentication method configured.

4. **Check permissions.** The Managed Identity needs `db_datareader`, `db_datawriter`, and `ddl_admin` (or `db_owner` for migrations) on the database.

---

### 5.3 Slow queries

**Symptoms:**
- API response times increase significantly.
- Application Insights shows high dependency duration for SQL calls.
- The readiness endpoint is slow to respond.

**Causes:**
- Missing indexes on frequently queried columns (e.g., `investigation_id`, `file_id`, `record_id`).
- DTU (Database Transaction Unit) exhaustion on the Azure SQL tier.
- Large result sets being returned without pagination.
- Lock contention from concurrent writes (bulk uploads).

**Diagnostic steps:**

```kql
// KQL: Check SQL dependency duration
AppDependencies
| where DependencyType == "SQL"
| where TimeGenerated > ago(4h)
| summarize avg(DurationMs), percentile(DurationMs, 95), percentile(DurationMs, 99), count() by bin(TimeGenerated, 15m)
| order by TimeGenerated desc
```

```bash
# Check DTU usage
az monitor metrics list \
  --resource /subscriptions/<SUB_ID>/resourceGroups/rg-assurancenet-data-dev/providers/Microsoft.Sql/servers/sql-assurancenet-dev/databases/sqldb-assurancenet-dev \
  --metric "dtu_consumption_percent" \
  --interval PT5M --aggregation Average \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ)
```

```sql
-- Check for missing indexes (run against Azure SQL)
SELECT
    mig.index_group_handle, mid.index_handle,
    CONVERT(decimal(28, 1), migs.avg_total_user_cost * migs.avg_user_impact * (migs.user_seeks + migs.user_scans)) AS improvement_measure,
    mid.statement AS table_name,
    mid.equality_columns, mid.inequality_columns, mid.included_columns
FROM sys.dm_db_missing_index_groups AS mig
INNER JOIN sys.dm_db_missing_index_group_stats AS migs ON migs.group_handle = mig.index_group_handle
INNER JOIN sys.dm_db_missing_index_details AS mid ON mig.index_handle = mid.index_handle
ORDER BY improvement_measure DESC
```

**Solutions:**

1. **Add missing indexes** identified by the DMV query above or by reviewing slow query plans.

2. **Scale up the SQL tier** if DTU consumption is consistently above 80%:
   ```bash
   az sql db update --name sqldb-assurancenet-dev \
     --server sql-assurancenet-dev \
     --resource-group rg-assurancenet-data-dev \
     --edition GeneralPurpose --capacity 4 --family Gen5
   ```

3. **Use pagination** for large result sets. All list endpoints should use `OFFSET`/`LIMIT` (or keyset pagination) instead of returning all rows.

4. **Review query plans** for the slowest queries using Query Performance Insight in the Azure Portal or by running `SET STATISTICS IO ON` and `SET STATISTICS TIME ON` in SSMS.

---

## 💾 6. Storage Issues

### 6.1 "BlobNotFound" / 404 on download

**Symptoms:**
- Download request returns `404 Not Found`.
- The document metadata exists in the database but the blob is missing from storage.

**Causes:**
- The blob was deleted (outside of soft-delete retention window).
- The blob path in the database does not match the actual path in storage (e.g., path encoding mismatch with special characters in filenames).
- The version ID requested does not exist (blob versioning was disabled or the version was deleted).
- Wrong storage container name.

**Diagnostic steps:**

```bash
# Check if the blob exists at the expected path
az storage blob show \
  --account-name <STORAGE_ACCOUNT_NAME> \
  --container-name assurancenet-documents \
  --name "<blob_path_from_database>" \
  --auth-mode login

# List blobs in the path prefix
az storage blob list \
  --account-name <STORAGE_ACCOUNT_NAME> \
  --container-name assurancenet-documents \
  --prefix "<record_id>/<file_id>/" \
  --auth-mode login \
  --output table

# Check soft-delete status
az storage blob list \
  --account-name <STORAGE_ACCOUNT_NAME> \
  --container-name assurancenet-documents \
  --prefix "<record_id>/<file_id>/" \
  --include d \
  --auth-mode login \
  --output table
```

```sql
-- Check the stored blob path in the database
SELECT file_id, blob_path, pdf_path, blob_version_id, original_filename
FROM documents
WHERE id = '<document_id>'
```

**Solutions:**

1. **Verify the blob path** stored in the database matches the actual blob path format: `INVESTIGATION-{RecordId}/{FileId}/blob/{filename}`.

2. **Check soft-delete.** If soft-delete is enabled on the storage account, the blob may be recoverable:
   ```bash
   az storage blob undelete \
     --account-name <STORAGE_ACCOUNT_NAME> \
     --container-name assurancenet-documents \
     --name "<blob_path>" \
     --auth-mode login
   ```

3. **Check blob versioning.** If the specific version was requested, verify it exists:
   ```bash
   az storage blob list \
     --account-name <STORAGE_ACCOUNT_NAME> \
     --container-name assurancenet-documents \
     --prefix "<record_id>/<file_id>/" \
     --include v \
     --auth-mode login \
     --output table
   ```

---

### 6.2 "AuthorizationPermissionMismatch" on blob operations

**Symptoms:**
- Storage operations fail with `AuthorizationPermissionMismatch` (HTTP 403).
- The error occurs for the API backend or the Function App when trying to read, write, or list blobs.

**Causes:**
- The Managed Identity is missing the `Storage Blob Data Contributor` role on the storage account.
- The role assignment scope is wrong (e.g., assigned at resource group level but the storage account is in a different resource group).
- A new Managed Identity was created but the old role assignments were not recreated.
- The storage account has `allowSharedKeyAccess: false` and the code is accidentally trying to use a shared key.

**Diagnostic steps:**

```bash
# Check role assignments for the App Service Managed Identity
az role assignment list \
  --assignee <MI_PRINCIPAL_ID> \
  --scope /subscriptions/<SUB_ID>/resourceGroups/rg-assurancenet-data-dev/providers/Microsoft.Storage/storageAccounts/<STORAGE_NAME> \
  --query "[].{Role:roleDefinitionName, Scope:scope}" -o table

# Get the MI principal ID
az identity show --name mi-app-assurancenet-dev \
  --resource-group rg-assurancenet-security-dev \
  --query principalId -o tsv
```

**Solutions:**

1. **Assign the correct role** to the Managed Identity:
   ```bash
   # For the App Service MI
   az role assignment create \
     --assignee <MI_PRINCIPAL_ID> \
     --role "Storage Blob Data Contributor" \
     --scope /subscriptions/<SUB_ID>/resourceGroups/rg-assurancenet-data-dev/providers/Microsoft.Storage/storageAccounts/<STORAGE_NAME>

   # For the Function App MI
   az role assignment create \
     --assignee <FUNC_MI_PRINCIPAL_ID> \
     --role "Storage Blob Data Contributor" \
     --scope /subscriptions/<SUB_ID>/resourceGroups/rg-assurancenet-data-dev/providers/Microsoft.Storage/storageAccounts/<STORAGE_NAME>
   ```

2. **Wait for propagation.** Azure RBAC role assignments can take up to 10 minutes to propagate. If you just assigned the role, wait and retry.

3. **Verify the MI client ID** is correctly configured in the App Service or Function App settings (`AZURE_CLIENT_ID`).

---

### 6.3 Storage capacity concerns

**Symptoms:**
- Storage costs are increasing unexpectedly.
- Blob count or total storage size is higher than expected.
- Old document versions are not being cleaned up.

**Diagnostic steps:**

```bash
# Check storage account usage
az storage account show --name <STORAGE_ACCOUNT_NAME> \
  --resource-group rg-assurancenet-data-dev \
  --query "{Sku:sku.name, Kind:kind, AccessTier:accessTier}"

# Check blob tier distribution
az storage blob list \
  --account-name <STORAGE_ACCOUNT_NAME> \
  --container-name assurancenet-documents \
  --query "[].{Name:name, Tier:properties.blobTier, Size:properties.contentLength}" \
  --num-results 100 \
  --auth-mode login -o table
```

**Solutions:**

1. **Review lifecycle management policies.** Set up policies to move old blobs to cooler tiers or delete old versions:
   ```bash
   az storage account management-policy show \
     --account-name <STORAGE_ACCOUNT_NAME> \
     --resource-group rg-assurancenet-data-dev
   ```

2. **Configure version cleanup.** If blob versioning creates many old versions, set a lifecycle policy to delete versions older than a retention period (e.g., 90 days for non-current versions).

3. **Move infrequently accessed blobs to Cool or Archive tier** to reduce costs.

4. **Monitor storage metrics** in the Azure Portal under the storage account's Metrics blade. Track "Blob Capacity" and "Blob Count" trends.

---

## 🌐 7. Infrastructure / Networking Issues

### 7.1 Resources can't communicate (Private Endpoints)

**Symptoms:**
- Timeouts between services (App Service to SQL, Functions to Storage, Functions to Gotenberg).
- DNS resolution returns a public IP instead of a private IP for a PaaS service.
- The readiness endpoint shows one or more dependencies as unhealthy.

**Causes:**
- Private DNS zones are not linked to the VNet.
- NSG rules on subnets are blocking traffic between services.
- VNet integration is not configured on the App Service or Function App.
- The Private Endpoint is in a failed provisioning state.

**Diagnostic steps:**

```bash
# Check all Private DNS zone links
for zone in privatelink.blob.core.windows.net privatelink.database.windows.net privatelink.vaultcore.azure.net privatelink.servicebus.windows.net; do
  echo "=== $zone ==="
  az network private-dns link vnet list \
    --resource-group rg-assurancenet-network-dev \
    --zone-name $zone \
    --query "[].{Name:name, VNet:virtualNetwork.id, Status:provisioningState}" -o table 2>/dev/null || echo "Zone not found"
done

# Check VNet integration on App Service
az webapp vnet-integration list \
  --name app-assurancenet-api-dev \
  --resource-group rg-assurancenet-app-dev -o table

# Check Private Endpoint provisioning state
az network private-endpoint list \
  --resource-group rg-assurancenet-network-dev \
  --query "[].{Name:name, Subnet:subnet.id, Status:provisioningState, Service:privateLinkServiceConnections[0].groupIds[0]}" -o table

# Check NSG rules on the private endpoints subnet
az network nsg rule list \
  --nsg-name nsg-private-endpoints \
  --resource-group rg-assurancenet-network-dev -o table
```

```kql
// KQL: Check NSG flow logs for denied traffic
AzureNetworkAnalytics_CL
| where FlowStatus_s == "D"  // Denied
| where TimeGenerated > ago(1h)
| project TimeGenerated, SrcIP_s, DestIP_s, DestPort_d, NSGRule_s
| order by TimeGenerated desc
```

**Solutions:**

1. **Link Private DNS zones to the VNet.** Each Private Endpoint requires its corresponding Private DNS zone linked to the VNet:
   | Service | DNS Zone |
   |---------|----------|
   | Blob Storage | `privatelink.blob.core.windows.net` |
   | Azure SQL | `privatelink.database.windows.net` |
   | Key Vault | `privatelink.vaultcore.azure.net` |
   | Event Hub | `privatelink.servicebus.windows.net` |

2. **Enable VNet integration** on App Service and Function App if not already configured:
   ```bash
   az webapp vnet-integration add \
     --name app-assurancenet-api-dev \
     --resource-group rg-assurancenet-app-dev \
     --vnet vnet-assurancenet-dev \
     --subnet snet-backend
   ```

3. **Review NSG rules.** The expected allowed traffic flow:
   - `snet-backend` (10.0.1.0/24): Inbound HTTPS from `AzureFrontDoor.Backend` only. Outbound to `snet-private-endpoints`.
   - `snet-functions` (10.0.2.0/24): Inbound from `EventGrid` service tag. Outbound to `snet-private-endpoints` and `snet-container-apps`.
   - `snet-private-endpoints` (10.0.3.0/24): Inbound from `snet-backend` and `snet-functions` only.
   - `snet-container-apps` (10.0.5.0/24): Inbound from `snet-functions` only.

4. **Verify DNS resolution.** From within the App Service SSH session:
   ```bash
   nslookup <storage-account>.blob.core.windows.net
   # Should resolve to 10.0.3.x (private endpoint IP), not a public IP
   ```

---

### 7.2 Front Door 502/504 errors

**Symptoms:**
- Users see a generic "502 Bad Gateway" or "504 Gateway Timeout" error page from Front Door.
- The app was previously working and suddenly started returning these errors.

**Causes:**
- The backend origin (App Service) health probe is failing.
- The origin is not reachable from Front Door (VNet misconfiguration, App Service stopped).
- The App Service is taking too long to respond (504).
- The App Service deployment slot swap is in progress.

**Diagnostic steps:**

```bash
# Check backend health directly (bypass Front Door)
curl -s -o /dev/null -w "%{http_code}" \
  https://app-assurancenet-api-dev.azurewebsites.net/api/v1/health

# Check Front Door origin health
az afd origin show --profile-name <FRONT_DOOR_PROFILE> \
  --origin-group-name <ORIGIN_GROUP> \
  --origin-name <ORIGIN_NAME> \
  --resource-group rg-assurancenet-network-dev \
  --query "{HostName:hostName, Enabled:enabledState, HealthProbe:originGroupName}"

# Check App Service status
az webapp show --name app-assurancenet-api-dev \
  --resource-group rg-assurancenet-app-dev \
  --query "{State:state, DefaultHostName:defaultHostName}" -o json
```

```kql
// KQL: Check Front Door access logs for 502/504
AzureDiagnostics
| where Category == "FrontDoorAccessLog"
| where httpStatusCode_d in (502, 504)
| where TimeGenerated > ago(1h)
| project TimeGenerated, httpStatusCode_d, requestUri_s, originUrl_s, timeTaken_d, errorInfo_s
| order by TimeGenerated desc
```

**Solutions:**

1. **Verify the backend health endpoint responds.** Front Door probes `/api/v1/health` and expects a 200 response. If this endpoint is down, Front Door marks the origin as unhealthy.
   ```bash
   curl -v https://app-assurancenet-api-dev.azurewebsites.net/api/v1/health
   ```

2. **Restart the App Service** if it is in a bad state:
   ```bash
   az webapp restart --name app-assurancenet-api-dev --resource-group rg-assurancenet-app-dev
   ```

3. **Check the Front Door health probe configuration.** Ensure the probe path, interval, and protocol match the backend:
   ```bash
   az afd origin-group show --profile-name <FRONT_DOOR_PROFILE> \
     --origin-group-name <ORIGIN_GROUP> \
     --resource-group rg-assurancenet-network-dev \
     --query "healthProbeSettings"
   ```

4. **For 504 errors**, increase the origin response timeout in the Front Door route configuration. Default is 60 seconds; large uploads or merges may need more.

---

### 7.3 Deployment fails with "ResourceNotFound"

**Symptoms:**
- Bicep deployment fails with error code `ResourceNotFound` or `DeploymentFailed`.
- The error references a resource that should exist but does not.

**Causes:**
- Dependency ordering in Bicep modules is incorrect (a resource references another that hasn't been created yet).
- The target resource group does not exist.
- A referenced existing resource (e.g., VNet, subnet) has been deleted or renamed.
- The Bicep parameter file references an incorrect resource name or ID.

**Diagnostic steps:**

```bash
# List recent deployments and their status
az deployment sub list --query "[?properties.provisioningState!='Succeeded'].{Name:name, State:properties.provisioningState, Error:properties.error.message}" -o table

# Get detailed error for a specific deployment
az deployment sub show --name <DEPLOYMENT_NAME> --query "properties.error" -o json

# Check if resource group exists
az group show --name rg-assurancenet-app-dev 2>/dev/null && echo "Exists" || echo "Not found"

# Validate Bicep without deploying
az deployment sub validate --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/parameters/dev.bicepparam
```

**Solutions:**

1. **Check deployment error details.** The error message will indicate which resource was not found and which resource was trying to reference it.

2. **Verify resource groups exist.** The system uses five resource groups per environment:
   - `rg-assurancenet-network-{env}`
   - `rg-assurancenet-app-{env}`
   - `rg-assurancenet-data-{env}`
   - `rg-assurancenet-security-{env}`
   - `rg-assurancenet-monitoring-{env}`

3. **Run `what-if` before deploying** to preview changes and catch issues:
   ```bash
   az deployment sub what-if --location eastus \
     --template-file infra/main.bicep \
     --parameters infra/parameters/dev.bicepparam
   ```

4. **Check Bicep module dependencies.** Ensure that modules use `dependsOn` or implicit dependencies (via resource references) to guarantee creation order.

5. **Build Bicep locally to check for syntax issues:**
   ```bash
   az bicep build --file infra/main.bicep
   ```

---

## 📊 8. Monitoring & Logging Issues

### 8.1 No data in Application Insights

**Symptoms:**
- Application Insights shows no requests, traces, or exceptions.
- Custom metrics (`documents.uploaded`, `pdf.conversion.duration`, etc.) are not appearing.
- The Application Map is empty.

**Causes:**
- `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable is not set on the App Service or Function App.
- The OpenTelemetry SDK is not initialized (the `configure_telemetry()` function in `app/telemetry/setup.py` is not called or is failing silently).
- Sampling is configured too aggressively, dropping most telemetry.
- The Application Insights resource is in a different subscription or has ingestion disabled.

**Diagnostic steps:**

```bash
# Check if the connection string is set
az webapp config appsettings list --name app-assurancenet-api-dev \
  --resource-group rg-assurancenet-app-dev \
  --query "[?name=='APPLICATIONINSIGHTS_CONNECTION_STRING'].value" -o tsv

# Verify Application Insights resource exists and is accessible
az monitor app-insights component show \
  --app appi-backend-dev \
  --resource-group rg-assurancenet-monitoring-dev \
  --query "{Name:name, InstrumentationKey:instrumentationKey, ConnectionString:connectionString}" -o json

# Check if telemetry is being ingested (last 1 hour)
az monitor app-insights metrics show \
  --app appi-backend-dev \
  --resource-group rg-assurancenet-monitoring-dev \
  --metric requests/count --interval PT1H
```

**Solutions:**

1. **Set the connection string** on the App Service:
   ```bash
   # Get the connection string from App Insights
   CONNECTION_STRING=$(az monitor app-insights component show \
     --app appi-backend-dev \
     --resource-group rg-assurancenet-monitoring-dev \
     --query connectionString -o tsv)

   # Set it on the App Service
   az webapp config appsettings set --name app-assurancenet-api-dev \
     --resource-group rg-assurancenet-app-dev \
     --settings "APPLICATIONINSIGHTS_CONNECTION_STRING=$CONNECTION_STRING"
   ```

2. **Verify telemetry initialization.** Check the App Service logs for any errors during startup related to telemetry setup. The `configure_telemetry()` function in `app/telemetry/setup.py` is called during the FastAPI lifespan event.

3. **Check sampling configuration.** If adaptive sampling is configured, it may drop low-volume telemetry. Review the OpenTelemetry SDK configuration and adjust sampling rates if needed.

4. **Restart the App Service** after changing the connection string:
   ```bash
   az webapp restart --name app-assurancenet-api-dev --resource-group rg-assurancenet-app-dev
   ```

---

### 8.2 Splunk not receiving logs

**Symptoms:**
- Splunk dashboards show no data or stale data from AssuranceNet.
- Azure Log Analytics has data, but Splunk does not.

**Causes:**
- The Data Export rule in Log Analytics is inactive or misconfigured.
- Event Hub is receiving messages but Splunk is not consuming them.
- The Splunk Add-on for Microsoft Cloud Services is not configured correctly.
- The `splunk` consumer group on the Event Hub does not exist.

**Diagnostic steps:**

```bash
# Check Event Hub namespace and hubs
az eventhubs namespace show --name evhns-assurancenet-splunk-dev \
  --resource-group rg-assurancenet-monitoring-dev \
  --query "{Status:status, Sku:sku.name}" -o json

# Check Event Hub metrics (incoming vs outgoing messages)
az monitor metrics list \
  --resource /subscriptions/<SUB_ID>/resourceGroups/rg-assurancenet-monitoring-dev/providers/Microsoft.EventHub/namespaces/evhns-assurancenet-splunk-dev \
  --metric "IncomingMessages,OutgoingMessages" \
  --interval PT1H --aggregation Total

# Verify consumer group exists
az eventhubs eventhub consumer-group list \
  --namespace-name evhns-assurancenet-splunk-dev \
  --eventhub-name evh-audit-logs \
  --resource-group rg-assurancenet-monitoring-dev -o table
```

```kql
// KQL: Check Data Export rule status in Log Analytics
_LogOperation
| where Category == "DataExport"
| where TimeGenerated > ago(24h)
| project TimeGenerated, Detail, Level
| order by TimeGenerated desc
```

**Solutions:**

1. **Verify the Data Export rules** are active in the Log Analytics workspace. Check in Azure Portal: Log Analytics workspace > Data Export.

2. **Check Event Hub incoming/outgoing message counts.** If incoming messages are non-zero but outgoing messages are zero, Splunk is not consuming. If incoming messages are zero, the Data Export rule is not working.

3. **Verify the consumer group** `splunk` exists on both `evh-audit-logs` and `evh-diagnostic-logs`:
   ```bash
   az eventhubs eventhub consumer-group create \
     --namespace-name evhns-assurancenet-splunk-dev \
     --eventhub-name evh-audit-logs \
     --name splunk \
     --resource-group rg-assurancenet-monitoring-dev
   ```

4. **Check Splunk Add-on configuration.** Verify the data input settings in Splunk:
   - Event Hub namespace connection string or Managed Identity configuration
   - Consumer group name matches (`splunk`)
   - Event Hub name matches

5. **Check Splunk's internal logs** for ingestion errors:
   ```
   index=_internal sourcetype=splunkd ERROR eventhub
   ```

---

### 8.3 Alert not firing

**Symptoms:**
- A condition that should trigger an alert (e.g., 5xx rate > 5%) is occurring but no notification is sent.
- The alert appears as "Not fired" in the Azure Portal even though the condition is met.

**Causes:**
- The alert rule's action group is not configured or has no contacts.
- The alert threshold is too high for the current traffic volume.
- The evaluation window or frequency does not capture the event (e.g., a spike that resolves within the evaluation period).
- The alert rule is disabled.

**Diagnostic steps:**

```bash
# List alert rules and their status
az monitor metrics alert list \
  --resource-group rg-assurancenet-monitoring-dev \
  --query "[].{Name:name, Enabled:enabled, Severity:severity, Criteria:criteria}" -o table

# Check action groups
az monitor action-group list \
  --resource-group rg-assurancenet-monitoring-dev \
  --query "[].{Name:name, EmailReceivers:emailReceivers[].emailAddress, SMSReceivers:smsReceivers[].phoneNumber}" -o json

# Check alert history
az monitor metrics alert show \
  --name <ALERT_NAME> \
  --resource-group rg-assurancenet-monitoring-dev \
  --query "{Enabled:enabled, Severity:severity, WindowSize:windowSize, EvalFrequency:evaluationFrequency}"
```

**Solutions:**

1. **Verify the action group** has the correct contacts (email, SMS, Teams webhook):
   ```bash
   az monitor action-group show --name <ACTION_GROUP_NAME> \
     --resource-group rg-assurancenet-monitoring-dev
   ```

2. **Review the alert threshold and window.** The 4-tier alert strategy is:
   | Severity | Trigger | Window |
   |----------|---------|--------|
   | Sev 0 (Critical) | 5xx rate > 5%, DLQ > 100 | 5 min |
   | Sev 1 (Error) | p95 > 3s, PDF timeout | 15 min |
   | Sev 2 (Warning) | p95 > 2s, capacity > 80% | 30 min |
   | Sev 3 (Info) | Daily counts | 24 hours |

3. **Enable the alert rule** if it is disabled:
   ```bash
   az monitor metrics alert update --name <ALERT_NAME> \
     --resource-group rg-assurancenet-monitoring-dev \
     --enabled true
   ```

4. **Test the action group** to verify notifications are being delivered:
   ```bash
   # Send a test notification
   az monitor action-group test-notifications create \
     --resource-group rg-assurancenet-monitoring-dev \
     --action-group-name <ACTION_GROUP_NAME> \
     --alert-type "metricstaticthreshold" \
     --receivers '[{"name":"test","emailAddress":"your@email.com"}]'
   ```

---

## 🛠️ 9. Local Development Issues

### 9.1 Backend won't start

**Symptoms:**
- Running `uvicorn app.main:app` fails immediately.
- Import errors or `ModuleNotFoundError` exceptions.
- Configuration validation errors from pydantic-settings.

**Causes:**
- Python dependencies are not installed or the virtual environment is not activated.
- Wrong Python version (requires 3.11+).
- `.env` file is missing or not configured.
- ODBC Driver 18 for SQL Server is not installed locally.

**Solutions:**

1. **Install dependencies:**
   ```bash
   cd src/backend
   python -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

2. **Verify Python version:**
   ```bash
   python --version   # Must be 3.11 or higher
   ```

3. **Create and configure `.env`:**
   ```bash
   cp .env.example .env
   # Edit .env with your local/dev values
   ```
   Required variables:
   ```
   ENVIRONMENT=dev
   ENTRA_TENANT_ID=<your-tenant-id>
   ENTRA_CLIENT_ID=<your-client-id>
   ENTRA_AUDIENCE=api://assurancenet-api
   AZURE_STORAGE_ACCOUNT_NAME=<your-storage-account>
   AZURE_SQL_SERVER=<your-sql-server>.database.windows.net
   AZURE_SQL_DATABASE=<your-database>
   ```

4. **Start the backend:**
   ```bash
   cd src/backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

---

### 9.2 Frontend won't start

**Symptoms:**
- `npm run dev` fails or the page loads but shows a blank screen.
- TypeScript compilation errors.
- MSAL authentication fails immediately.

**Causes:**
- Node modules are not installed or are corrupted.
- Wrong Node.js version (requires 20+).
- `VITE_*` environment variables are not set.

**Solutions:**

1. **Install dependencies:**
   ```bash
   cd src/frontend
   npm install
   ```

2. **Verify Node.js version:**
   ```bash
   node --version   # Must be 20 or higher
   ```

3. **Set environment variables.** Create a `.env.local` file in `src/frontend/`:
   ```
   VITE_ENTRA_TENANT_ID=<your-tenant-id>
   VITE_ENTRA_CLIENT_ID=<your-client-id>
   VITE_REDIRECT_URI=http://localhost:5173
   VITE_AUTHORITY_HOST=https://login.microsoftonline.com
   VITE_API_SCOPE=api://assurancenet-api/Documents.ReadWrite
   ```

4. **Start the frontend:**
   ```bash
   cd src/frontend
   npm run dev
   ```
   The dev server starts on port 5173 and proxies `/api` requests to `http://localhost:8000` (configured in `vite.config.ts`).

---

### 9.3 CORS errors in browser

**Symptoms:**
- Browser console shows `Access to XMLHttpRequest has been blocked by CORS policy`.
- API calls from the frontend fail but the same calls work in Postman or curl.

**Causes:**
- The FastAPI CORS middleware does not include the frontend's origin.
- The Vite proxy is not configured or not being used (frontend calling the API directly instead of through the proxy).
- The browser is sending preflight OPTIONS requests that the backend is not handling.

**Solutions:**

1. **Use the Vite proxy for local development.** The `vite.config.ts` already proxies `/api` requests to `http://localhost:8000`. Make sure frontend API calls use relative paths (e.g., `/api/v1/documents`) instead of absolute URLs (e.g., `http://localhost:8000/api/v1/documents`).

2. **Verify FastAPI CORS configuration.** The backend allows these origins by default (`app/main.py`):
   ```python
   allow_origins=[
       "http://localhost:3000",
       "http://localhost:5173",
   ]
   ```
   If your frontend runs on a different port, add it to this list.

3. **Check that OPTIONS requests are handled.** The `CORSMiddleware` in FastAPI handles preflight requests automatically. Ensure the middleware is added before the router (which it is in the current `main.py`).

---

### 9.4 ODBC Driver not found

**Symptoms:**
- Backend fails to connect to Azure SQL with: `[IM002] [Microsoft][ODBC Driver Manager] Data source name not found and no default driver specified`.
- Error referencing `ODBC Driver 18 for SQL Server` not being available.

**Causes:**
- The Microsoft ODBC Driver 18 for SQL Server is not installed on your local machine.
- The driver name in the connection string does not match the installed version.

**Solutions:**

Install ODBC Driver 18 for SQL Server:

**Windows:**
```
Download from: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
Run the MSI installer for "Microsoft ODBC Driver 18 for SQL Server"
```

**macOS (Homebrew):**
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18
```

**Linux (Ubuntu/Debian):**
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql18
```

After installation, verify:
```bash
odbcinst -j    # Check ODBC config location
odbcinst -q -d # List installed drivers (should show "ODBC Driver 18 for SQL Server")
```

---

## 🔄 10. CI/CD Pipeline Issues

### 10.1 GitHub Actions OIDC authentication fails

**Symptoms:**
- The `azure/login@v2` step fails with `AADSTS700024: Client assertion is not within its valid time range` or `AADSTS700016`.
- The workflow log shows `Error: Login failed with Error: Could not login to Azure...`.

**Causes:**
- Federated credential is not configured on the Entra ID app registration for the GitHub repository and branch.
- The `audience` in the federated credential does not match (`api://AzureADTokenExchange`).
- The branch filter in the federated credential does not match the workflow branch (e.g., configured for `main` but workflow runs on `develop`).
- GitHub secrets `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, or `AZURE_SUBSCRIPTION_ID` are missing or incorrect.

**Diagnostic steps:**

```bash
# List federated credentials on the app registration
az ad app federated-credential list --id <APP_REGISTRATION_ID> -o table

# Check specific federated credential
az ad app federated-credential show --id <APP_REGISTRATION_ID> \
  --federated-credential-id <CREDENTIAL_ID> -o json
```

Check that the federated credential matches:
- **Issuer**: `https://token.actions.githubusercontent.com`
- **Subject**: `repo:<org>/<repo>:ref:refs/heads/main` (or the branch/environment)
- **Audience**: `api://AzureADTokenExchange`

**Solutions:**

1. **Create or update the federated credential:**
   ```bash
   az ad app federated-credential create --id <APP_REGISTRATION_ID> --parameters '{
     "name": "github-main-branch",
     "issuer": "https://token.actions.githubusercontent.com",
     "subject": "repo:<org>/ucm-azure-native-demo:ref:refs/heads/main",
     "audiences": ["api://AzureADTokenExchange"],
     "description": "GitHub Actions - main branch"
   }'
   ```

2. **For environment-based deployment** (staging, production), create federated credentials with environment subjects:
   ```
   subject: repo:<org>/ucm-azure-native-demo:environment:production
   ```

3. **Verify GitHub secrets** are set correctly in the repository settings: Settings > Secrets and variables > Actions. Required secrets:
   - `AZURE_CLIENT_ID` - Application (client) ID of the app registration
   - `AZURE_TENANT_ID` - Directory (tenant) ID
   - `AZURE_SUBSCRIPTION_ID` - Azure subscription ID

4. **Ensure `id-token: write` permission** is set in the workflow:
   ```yaml
   permissions:
     id-token: write
     contents: read
   ```

---

### 10.2 Bicep what-if fails

**Symptoms:**
- The `az deployment sub what-if` step fails in CI.
- Errors include syntax errors, missing parameters, or unsupported API versions.

**Causes:**
- A Bicep syntax error introduced in a recent commit.
- A parameter required by the template is missing from the parameter file.
- The Bicep CLI version in CI is different from local (using deprecated syntax or API versions).

**Diagnostic steps:**

```bash
# Build Bicep locally to check for syntax errors
az bicep build --file infra/main.bicep

# Validate without deploying
az deployment sub validate --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/parameters/dev.bicepparam

# Check Bicep version
az bicep version
```

**Solutions:**

1. **Run `bicep build` locally** before pushing to catch syntax errors early:
   ```bash
   az bicep build --file infra/main.bicep
   ```

2. **Check parameter file** for completeness. Every parameter in the template without a default value must be provided in the parameter file:
   ```bash
   # Compare template params with parameter file
   az bicep build --file infra/main.bicep --stdout | python3 -m json.tool | grep -A2 '"parameters"'
   ```

3. **Update the Bicep CLI** locally to match CI:
   ```bash
   az bicep upgrade
   az bicep version
   ```

4. **Check API version availability.** If a Bicep module references a resource API version that doesn't exist in the target Azure region or subscription, the deployment will fail. Use the latest stable API versions.

---

### 10.3 Tests fail in CI but pass locally

**Symptoms:**
- `pytest` or `vitest` passes locally but fails in the GitHub Actions CI pipeline.
- Failures are inconsistent (sometimes pass, sometimes fail).
- Error messages reference missing files, environment variables, or connection issues.

**Causes:**
- Python or Node.js version difference between local and CI (CI uses Python 3.11, Node 20).
- Missing test dependencies not installed in CI.
- Tests depend on local `.env` file values that are not available in CI.
- File path assumptions that differ between Windows (local) and Linux (CI).
- Tests depend on execution order or shared state.

**Diagnostic steps:**

Review the CI workflow configuration (`.github/workflows/ci.yml`) and compare with your local setup:

```bash
# Check CI Python version
python --version   # Local
# CI uses: python-version: '3.11'

# Check CI Node version
node --version     # Local
# CI uses: node-version: '20'

# Run tests locally with CI-like settings
cd src/backend
pip install -e ".[dev]"
pytest ../../tests/backend/ --cov=app --cov-report=term-missing --cov-fail-under=80 -v

cd src/frontend
npm ci
npx vitest run --coverage
```

**Solutions:**

1. **Match versions.** Ensure your local Python and Node.js versions match CI. Use `pyenv` or `nvm` to manage versions.

2. **Use `npm ci` instead of `npm install`** locally to match CI's clean install behavior.

3. **Avoid relying on `.env` in tests.** Tests should mock external dependencies. Use `conftest.py` fixtures to set up test configuration:
   ```python
   # tests/conftest.py
   import os
   os.environ["ENVIRONMENT"] = "test"
   os.environ["ENTRA_TENANT_ID"] = "test-tenant"
   # ... etc
   ```

4. **Use absolute paths in test configuration.** If `conftest.py` references files relative to the working directory, use `pathlib.Path(__file__).parent` to build absolute paths that work in both local and CI environments.

5. **Run tests in random order** locally to catch order-dependent failures:
   ```bash
   pip install pytest-randomly
   pytest tests/backend/ -p randomly -v
   ```

6. **Check test coverage threshold.** The CI enforces `--cov-fail-under=80`. If new code was added without tests, coverage may drop below 80% in CI.

---

## 📋 Quick Reference: Diagnostic Commands

### 💚 Health Checks

```bash
# Basic health (should always return 200)
curl -s https://app-assurancenet-api-dev.azurewebsites.net/api/v1/health | python3 -m json.tool

# Readiness check (database + storage)
curl -s https://app-assurancenet-api-dev.azurewebsites.net/api/v1/health/ready | python3 -m json.tool

# Gotenberg health (from within VNet or directly if accessible)
curl -s http://ca-gotenberg-dev:3000/health
```

### 🔍 KQL Queries for Common Investigations

```kql
// Recent exceptions
AppExceptions
| where TimeGenerated > ago(1h)
| project TimeGenerated, ExceptionType, OuterMessage, ProblemId
| order by TimeGenerated desc
| take 50

// API request performance
AppRequests
| where TimeGenerated > ago(1h)
| summarize count(), avg(DurationMs), percentile(DurationMs, 95) by Name, ResultCode
| order by count_ desc

// Dependency failures (SQL, Storage, Gotenberg)
AppDependencies
| where Success == false
| where TimeGenerated > ago(1h)
| summarize count() by DependencyType, Name, ResultCode
| order by count_ desc

// PDF conversion tracking
FunctionAppLogs
| where TimeGenerated > ago(4h)
| where FunctionName == "pdf_converter"
| project TimeGenerated, Level, Message
| order by TimeGenerated desc

// Event Grid delivery tracking
AzureMetrics
| where ResourceProvider == "MICROSOFT.EVENTGRID"
| where MetricName in ("DeliverySuccessCount", "DeliveryAttemptFailCount", "DeadLetteredCount")
| where TimeGenerated > ago(4h)
| summarize Total=sum(Total) by MetricName, bin(TimeGenerated, 15m)

// WAF blocked requests
AzureDiagnostics
| where Category == "FrontDoorWebApplicationFirewallLog"
| where action_s == "Block"
| where TimeGenerated > ago(1h)
| project TimeGenerated, clientIP_s, requestUri_s, ruleName_s, details_msg_s
```

### ⌨️ Azure CLI Quick Diagnostics

```bash
# App Service status
az webapp show --name app-assurancenet-api-dev --resource-group rg-assurancenet-app-dev --query "state" -o tsv

# Function App status
az functionapp show --name func-assurancenet-pdf-dev --resource-group rg-assurancenet-app-dev --query "state" -o tsv

# Container App replica count
az containerapp show --name ca-gotenberg-dev --resource-group rg-assurancenet-app-dev --query "properties.template.scale" -o json

# SQL DTU usage (last hour)
az monitor metrics list \
  --resource /subscriptions/<SUB_ID>/resourceGroups/rg-assurancenet-data-dev/providers/Microsoft.Sql/servers/sql-assurancenet-dev/databases/sqldb-assurancenet-dev \
  --metric "dtu_consumption_percent" --interval PT5M --aggregation Average

# Storage account connectivity
az storage account show-connection-string --name <STORAGE_ACCOUNT_NAME> --resource-group rg-assurancenet-data-dev

# Event Grid delivery metrics
az monitor metrics list --resource <SYSTEM_TOPIC_RESOURCE_ID> --metric "DeliverySuccessCount,DeliveryAttemptFailCount" --interval PT1H --aggregation Total

# Private DNS resolution check
az network private-dns record-set a list --zone-name privatelink.blob.core.windows.net --resource-group rg-assurancenet-network-dev -o table
```

---

## 🚨 Escalation Path

| Severity | Response Time | First Responder | Escalation |
|----------|--------------|-----------------|------------|
| Sev 0 - Service down | 15 minutes | On-call engineer | Page platform team lead |
| Sev 1 - Degraded | 30 minutes | On-call engineer | Notify team channel |
| Sev 2 - Minor issue | 4 hours | Assigned engineer | Team standup |
| Sev 3 - Informational | Next business day | Backlog | Sprint planning |

For issues not covered in this guide, check the [Incident Response Runbook](../runbooks/incident-response.md) for escalation procedures.

---

> **Related:** [Operations Guide](operations-guide.md) | [Deployment Guide](deployment-guide.md) | [Developer Guide](developer-guide.md) | [Incident Response Runbook](../runbooks/incident-response.md) | [Splunk Integration](../runbooks/splunk-integration.md)
