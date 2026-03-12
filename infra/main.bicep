targetScope = 'subscription'

// ============================================================================
// AssuranceNet Document Management - Main Orchestrator
// Replaces Oracle UCM with Azure-native document architecture
// ============================================================================

@description('Environment name (dev, staging, prod)')
@allowed(['dev', 'staging', 'prod'])
param environment string

@description('Primary Azure region')
param location string = 'eastus'

@description('Project name prefix for resource naming')
param projectName string = 'assurancenet'

@description('Tags applied to all resources')
param tags object = {
  Project: 'AssuranceNet'
  ManagedBy: 'bicep'
  Application: 'UCM-Migration'
}

@description('Entra ID admin object ID for SQL Server')
param sqlAdminObjectId string

@description('Entra ID admin login name for SQL Server')
param sqlAdminLogin string

@description('Entra ID admin principal type for SQL Server')
@allowed(['User', 'Group', 'Application'])
param sqlAdminPrincipalType string = 'User'

@description('Contact email for budget alerts and notifications')
param contactEmail string

@description('Deploy Functions and Event Grid (requires compute quota)')
param deployFunctions bool = true

// Computed names
var envTags = union(tags, { Environment: environment })
var rgNames = {
  network: 'rg-${projectName}-network-${environment}'
  app: 'rg-${projectName}-app-${environment}'
  data: 'rg-${projectName}-data-${environment}'
  security: 'rg-${projectName}-security-${environment}'
  monitoring: 'rg-${projectName}-monitoring-${environment}'
}

// ============================================================================
// Resource Groups
// ============================================================================

module rgNetwork 'modules/resource-group.bicep' = {
  name: 'deploy-rg-network'
  params: {
    name: rgNames.network
    location: location
    tags: envTags
  }
}

module rgApp 'modules/resource-group.bicep' = {
  name: 'deploy-rg-app'
  params: {
    name: rgNames.app
    location: location
    tags: envTags
  }
}

module rgData 'modules/resource-group.bicep' = {
  name: 'deploy-rg-data'
  params: {
    name: rgNames.data
    location: location
    tags: envTags
  }
}

module rgSecurity 'modules/resource-group.bicep' = {
  name: 'deploy-rg-security'
  params: {
    name: rgNames.security
    location: location
    tags: envTags
  }
}

module rgMonitoring 'modules/resource-group.bicep' = {
  name: 'deploy-rg-monitoring'
  params: {
    name: rgNames.monitoring
    location: location
    tags: envTags
  }
}

// ============================================================================
// Monitoring (deployed early - other resources send diagnostics here)
// ============================================================================

module monitoring 'modules/monitoring.bicep' = {
  name: 'deploy-monitoring'
  scope: resourceGroup(rgNames.monitoring)
  params: {
    environment: environment
    location: location
    projectName: projectName
    tags: envTags
  }
  dependsOn: [rgMonitoring]
}

// ============================================================================
// Networking
// ============================================================================

module networking 'modules/networking.bicep' = {
  name: 'deploy-networking'
  scope: resourceGroup(rgNames.network)
  params: {
    environment: environment
    location: location
    projectName: projectName
    tags: envTags
  }
  dependsOn: [rgNetwork]
}

// ============================================================================
// Security - Key Vault & Managed Identities
// ============================================================================

module keyVault 'modules/key-vault.bicep' = {
  name: 'deploy-key-vault'
  scope: resourceGroup(rgNames.security)
  params: {
    environment: environment
    location: location
    projectName: projectName
    tags: envTags
    subnetId: networking.outputs.privateEndpointSubnetId
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
  }
  dependsOn: [rgSecurity]
}

module managedIdentity 'modules/managed-identity.bicep' = {
  name: 'deploy-managed-identity'
  scope: resourceGroup(rgNames.security)
  params: {
    environment: environment
    location: location
    projectName: projectName
    tags: envTags
  }
  dependsOn: [rgSecurity]
}

// ============================================================================
// Data Tier - Storage & SQL
// ============================================================================

module storage 'modules/storage.bicep' = {
  name: 'deploy-storage'
  scope: resourceGroup(rgNames.data)
  params: {
    environment: environment
    location: location
    projectName: projectName
    tags: envTags
    subnetId: networking.outputs.privateEndpointSubnetId
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
    appManagedIdentityPrincipalId: managedIdentity.outputs.appManagedIdentityPrincipalId
    funcManagedIdentityPrincipalId: managedIdentity.outputs.funcManagedIdentityPrincipalId
  }
  dependsOn: [rgData]
}

module sqlDatabase 'modules/sql-database.bicep' = {
  name: 'deploy-sql-database'
  scope: resourceGroup(rgNames.data)
  params: {
    environment: environment
    location: location
    privateEndpointLocation: location
    projectName: projectName
    tags: envTags
    subnetId: networking.outputs.privateEndpointSubnetId
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
    entraAdminObjectId: sqlAdminObjectId
    entraAdminLogin: sqlAdminLogin
    entraAdminPrincipalType: sqlAdminPrincipalType
  }
  dependsOn: [rgData]
}

// ============================================================================
// Application Tier (Sprint 2+)
// ============================================================================

module appService 'modules/app-service.bicep' = {
  name: 'deploy-app-service'
  scope: resourceGroup(rgNames.app)
  params: {
    environment: environment
    location: location
    projectName: projectName
    tags: envTags
    subnetId: networking.outputs.backendSubnetId
    managedIdentityId: managedIdentity.outputs.appManagedIdentityId
    managedIdentityClientId: managedIdentity.outputs.appManagedIdentityClientId
    appInsightsConnectionString: monitoring.outputs.backendAppInsightsConnectionString
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
    storageAccountName: storage.outputs.storageAccountName
    sqlServerFqdn: sqlDatabase.outputs.sqlServerFqdn
    sqlDatabaseName: sqlDatabase.outputs.sqlDatabaseName
    keyVaultUri: keyVault.outputs.keyVaultUri
  }
  dependsOn: [rgApp]
}

module staticWebApp 'modules/static-web-app.bicep' = {
  name: 'deploy-static-web-app'
  scope: resourceGroup(rgNames.app)
  params: {
    environment: environment
    location: location
    projectName: projectName
    tags: envTags
  }
  dependsOn: [rgApp]
}

// ============================================================================
// Processing Tier (Sprint 3+)
// ============================================================================

module functions 'modules/functions.bicep' = if (deployFunctions) {
  name: 'deploy-functions'
  scope: resourceGroup(rgNames.app)
  params: {
    environment: environment
    location: location
    projectName: projectName
    tags: envTags
    subnetId: networking.outputs.functionsSubnetId
    managedIdentityId: managedIdentity.outputs.funcManagedIdentityId
    managedIdentityClientId: managedIdentity.outputs.funcManagedIdentityClientId
    appInsightsConnectionString: monitoring.outputs.functionsAppInsightsConnectionString
    storageAccountName: storage.outputs.storageAccountName
    storageAccountId: storage.outputs.storageAccountId
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
  }
  dependsOn: [rgApp]
}

module containerApps 'modules/container-apps.bicep' = {
  name: 'deploy-container-apps'
  scope: resourceGroup(rgNames.app)
  params: {
    environment: environment
    location: location
    projectName: projectName
    tags: envTags
    subnetId: networking.outputs.containerAppsSubnetId
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
  }
  dependsOn: [rgApp]
}

module eventGrid 'modules/event-grid.bicep' = if (deployFunctions) {
  name: 'deploy-event-grid'
  scope: resourceGroup(rgNames.data)
  params: {
    environment: environment
    projectName: projectName
    tags: envTags
    storageAccountId: storage.outputs.storageAccountId
    storageAccountName: storage.outputs.storageAccountName
    functionAppId: deployFunctions ? functions.outputs.functionAppId : ''
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
  }
}

// ============================================================================
// Networking - Front Door (Sprint 2+)
// ============================================================================

module frontDoor 'modules/front-door.bicep' = {
  name: 'deploy-front-door'
  scope: resourceGroup(rgNames.network)
  params: {
    environment: environment
    projectName: projectName
    tags: envTags
    backendAppServiceHostname: appService.outputs.appServiceHostname
    staticWebAppHostname: staticWebApp.outputs.staticWebAppHostname
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
  }
}

// ============================================================================
// Compliance & Security (Sprint 4+)
// ============================================================================

module eventHub 'modules/event-hub.bicep' = {
  name: 'deploy-event-hub'
  scope: resourceGroup(rgNames.monitoring)
  params: {
    environment: environment
    location: location
    projectName: projectName
    tags: envTags
    subnetId: networking.outputs.privateEndpointSubnetId
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
  }
}

module dashboard 'modules/dashboard.bicep' = {
  name: 'deploy-dashboard'
  scope: resourceGroup(rgNames.monitoring)
  params: {
    environment: environment
    location: location
    projectName: projectName
    tags: envTags
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
    backendAppInsightsId: monitoring.outputs.backendAppInsightsId
  }
}

module policy 'modules/policy.bicep' = {
  name: 'deploy-policy'
  params: {
    environment: environment
    projectName: projectName
  }
}

module defender 'modules/defender.bicep' = {
  name: 'deploy-defender'
}

module budgets 'modules/budgets.bicep' = {
  name: 'deploy-budgets'
  scope: resourceGroup(rgNames.monitoring)
  params: {
    environment: environment
    projectName: projectName
    tags: envTags
    contactEmail: contactEmail
  }
  dependsOn: [rgMonitoring]
}

// ============================================================================
// Outputs
// ============================================================================

output resourceGroupNames object = rgNames
output storageAccountName string = storage.outputs.storageAccountName
output sqlServerFqdn string = sqlDatabase.outputs.sqlServerFqdn
output appServiceHostname string = appService.outputs.appServiceHostname
output staticWebAppHostname string = staticWebApp.outputs.staticWebAppHostname
output keyVaultUri string = keyVault.outputs.keyVaultUri
output logAnalyticsWorkspaceId string = monitoring.outputs.logAnalyticsWorkspaceId
