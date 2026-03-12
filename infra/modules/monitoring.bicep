// ============================================================================
// Monitoring Module - Log Analytics + Application Insights
// ============================================================================

@description('Environment name')
param environment string

@description('Azure region')
param location string

@description('Project name prefix')
param projectName string

@description('Resource tags')
param tags object

var isProduction = environment == 'prod'

// ============================================================================
// Log Analytics Workspace
// ============================================================================

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'law-${projectName}-${environment}'
  location: location
  tags: tags
  properties: {
    sku: {
      name: isProduction ? 'PerGB2018' : 'PerGB2018'
    }
    retentionInDays: 90
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    workspaceCapping: {
      dailyQuotaGb: isProduction ? -1 : 5
    }
  }
}

// Archive policy for NIST AU-11 (3-year retention)
resource archivePolicy 'Microsoft.OperationalInsights/workspaces/tables@2022-10-01' = if (isProduction) {
  parent: logAnalytics
  name: 'SecurityEvent'
  properties: {
    totalRetentionInDays: 1095 // 3 years
    plan: 'Analytics'
  }
}

// ============================================================================
// Application Insights - Backend
// ============================================================================

resource backendAppInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-backend-${environment}'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ============================================================================
// Application Insights - Functions
// ============================================================================

resource functionsAppInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-functions-${environment}'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ============================================================================
// Application Insights - Frontend
// ============================================================================

resource frontendAppInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-frontend-${environment}'
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// ============================================================================
// Outputs
// ============================================================================

output logAnalyticsWorkspaceId string = logAnalytics.id
output logAnalyticsWorkspaceName string = logAnalytics.name
output backendAppInsightsId string = backendAppInsights.id
output backendAppInsightsConnectionString string = backendAppInsights.properties.ConnectionString
output functionsAppInsightsConnectionString string = functionsAppInsights.properties.ConnectionString
output frontendAppInsightsConnectionString string = frontendAppInsights.properties.ConnectionString
