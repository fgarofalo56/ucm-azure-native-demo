// ============================================================================
// Functions Module - PDF Conversion Azure Function
// ============================================================================

@description('Environment name')
param environment string

@description('Azure region')
param location string

@description('Project name prefix')
param projectName string

@description('Resource tags')
param tags object

@description('Functions subnet ID for VNet integration')
param subnetId string

@description('User-assigned Managed Identity resource ID')
param managedIdentityId string

@description('Managed Identity client ID')
param managedIdentityClientId string

@description('Application Insights connection string')
param appInsightsConnectionString string

@description('Storage account name for trigger')
param storageAccountName string

@description('Storage account ID')
param storageAccountId string

@description('Log Analytics workspace ID')
param logAnalyticsWorkspaceId string

var functionPlanName = 'asp-func-${environment}'
var functionAppName = 'func-pdf-converter-${environment}'
var isProduction = environment == 'prod'

// ============================================================================
// Function App Service Plan (Premium for prod, Consumption for dev/staging)
// ============================================================================

resource functionPlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: functionPlanName
  location: location
  tags: tags
  kind: 'linux'
  sku: isProduction ? {
    name: 'EP1'
    tier: 'ElasticPremium'
  } : {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {
    reserved: true
    maximumElasticWorkerCount: isProduction ? 5 : 1
  }
}

// Function-specific storage (required for Azure Functions runtime)
resource functionStorage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'stfunc${replace(projectName, '-', '')}${environment}'
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}

// ============================================================================
// Function App
// ============================================================================

resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: functionAppName
  location: location
  tags: tags
  kind: 'functionapp,linux'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    serverFarmId: functionPlan.id
    httpsOnly: true
    virtualNetworkSubnetId: isProduction ? subnetId : null
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      appSettings: [
        { name: 'FUNCTIONS_WORKER_RUNTIME', value: 'python' }
        { name: 'FUNCTIONS_EXTENSION_VERSION', value: '~4' }
        { name: 'AzureWebJobsStorage', value: 'DefaultEndpointsProtocol=https;AccountName=${functionStorage.name};AccountKey=${functionStorage.listKeys().keys[0].value}' }
        { name: 'AZURE_CLIENT_ID', value: managedIdentityClientId }
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsightsConnectionString }
        { name: 'AZURE_STORAGE_ACCOUNT_NAME', value: storageAccountName }
        { name: 'ENVIRONMENT', value: environment }
      ]
    }
  }
}

// ============================================================================
// Diagnostic Settings
// ============================================================================

resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'diag-func-${environment}'
  scope: functionApp
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      { category: 'FunctionAppLogs', enabled: true }
    ]
    metrics: [
      { category: 'AllMetrics', enabled: true }
    ]
  }
}

// ============================================================================
// Outputs
// ============================================================================

output functionAppId string = functionApp.id
output functionAppName string = functionApp.name
output functionAppHostname string = functionApp.properties.defaultHostName
