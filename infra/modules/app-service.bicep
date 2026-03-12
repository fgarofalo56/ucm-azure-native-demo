// ============================================================================
// App Service Module - FastAPI Backend
// ============================================================================

@description('Environment name')
param environment string

@description('Azure region')
param location string

@description('Project name prefix')
param projectName string

@description('Resource tags')
param tags object

@description('Backend subnet ID for VNet integration')
param subnetId string

@description('User-assigned Managed Identity resource ID')
param managedIdentityId string

@description('Managed Identity client ID')
param managedIdentityClientId string

@description('Application Insights connection string')
param appInsightsConnectionString string

@description('Log Analytics workspace ID')
param logAnalyticsWorkspaceId string

@description('Storage account name')
param storageAccountName string

@description('SQL Server FQDN')
param sqlServerFqdn string

@description('SQL Database name')
param sqlDatabaseName string

@description('Key Vault URI')
param keyVaultUri string

var isProduction = environment == 'prod'
var appServicePlanName = 'asp-${projectName}-${environment}'
var appServiceName = 'app-${projectName}-api-${environment}'

// ============================================================================
// App Service Plan
// ============================================================================

resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: appServicePlanName
  location: location
  tags: tags
  kind: 'linux'
  sku: {
    name: isProduction ? 'P1v3' : 'B1'
    tier: isProduction ? 'PremiumV3' : 'Basic'
  }
  properties: {
    reserved: true // Linux
  }
}

// ============================================================================
// App Service
// ============================================================================

resource appService 'Microsoft.Web/sites@2023-12-01' = {
  name: appServiceName
  location: location
  tags: tags
  kind: 'app,linux'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    virtualNetworkSubnetId: subnetId
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      http20Enabled: true
      alwaysOn: isProduction
      appCommandLine: 'gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000'
      appSettings: [
        { name: 'ENVIRONMENT', value: environment }
        { name: 'AZURE_CLIENT_ID', value: managedIdentityClientId }
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsightsConnectionString }
        { name: 'AZURE_STORAGE_ACCOUNT_NAME', value: storageAccountName }
        { name: 'AZURE_SQL_SERVER', value: sqlServerFqdn }
        { name: 'AZURE_SQL_DATABASE', value: sqlDatabaseName }
        { name: 'AZURE_KEY_VAULT_URI', value: keyVaultUri }
        { name: 'SCM_DO_BUILD_DURING_DEPLOYMENT', value: 'true' }
      ]
    }
  }
}

// ============================================================================
// Staging Deployment Slot (Blue/Green)
// ============================================================================

resource stagingSlot 'Microsoft.Web/sites/slots@2023-12-01' = if (isProduction) {
  parent: appService
  name: 'staging'
  location: location
  tags: tags
  kind: 'app,linux'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    virtualNetworkSubnetId: subnetId
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      http20Enabled: true
      appCommandLine: 'gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000'
    }
  }
}

// ============================================================================
// Diagnostic Settings
// ============================================================================

resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'diag-app-${environment}'
  scope: appService
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      { category: 'AppServiceHTTPLogs', enabled: true }
      { category: 'AppServiceConsoleLogs', enabled: true }
      { category: 'AppServiceAuditLogs', enabled: true }
    ]
    metrics: [
      { category: 'AllMetrics', enabled: true }
    ]
  }
}

// ============================================================================
// Outputs
// ============================================================================

output appServiceId string = appService.id
output appServiceName string = appService.name
output appServiceHostname string = appService.properties.defaultHostName
