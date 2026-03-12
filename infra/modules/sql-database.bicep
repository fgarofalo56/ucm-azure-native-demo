// ============================================================================
// SQL Database Module - Azure SQL Server + Database
// ============================================================================

@description('Environment name')
param environment string

@description('Azure region for SQL Server')
param location string

@description('Azure region for private endpoint (must match VNet region)')
param privateEndpointLocation string = location

@description('Project name prefix')
param projectName string

@description('Resource tags')
param tags object

@description('Subnet ID for private endpoint')
param subnetId string

@description('Log Analytics workspace ID for diagnostics')
param logAnalyticsWorkspaceId string

@description('Entra ID admin object ID')
param entraAdminObjectId string

@description('Entra ID admin login name')
param entraAdminLogin string

@description('Entra ID admin principal type (User, Group, or Application)')
@allowed(['User', 'Group', 'Application'])
param entraAdminPrincipalType string = 'User'

var sqlServerName = 'sql-${projectName}-${environment}'
var sqlDatabaseName = 'sqldb-${projectName}-${environment}'
var isProduction = environment == 'prod'

// ============================================================================
// SQL Server (Entra ID auth only)
// ============================================================================

resource sqlServer 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: sqlServerName
  location: location
  tags: tags
  properties: {
    minimalTlsVersion: '1.2'
    publicNetworkAccess: isProduction ? 'Disabled' : 'Enabled'
    administrators: {
      administratorType: 'ActiveDirectory'
      azureADOnlyAuthentication: true
      login: entraAdminLogin
      sid: entraAdminObjectId
      principalType: entraAdminPrincipalType
      tenantId: subscription().tenantId
    }
  }
}

// ============================================================================
// SQL Database
// ============================================================================

resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location
  tags: tags
  sku: isProduction
    ? {
        name: 'GP_Gen5'
        tier: 'GeneralPurpose'
        family: 'Gen5'
        capacity: 4
      }
    : {
        name: 'GP_S_Gen5'
        tier: 'GeneralPurpose'
        family: 'Gen5'
        capacity: 1
      }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: isProduction ? 107374182400 : 34359738368 // 100GB prod, 32GB dev
    autoPauseDelay: isProduction ? -1 : 60 // Serverless auto-pause for dev
    minCapacity: isProduction ? json('0') : json('0.5')
    zoneRedundant: isProduction
    requestedBackupStorageRedundancy: isProduction ? 'Geo' : 'Local'
  }
}

// ============================================================================
// Firewall Rules (dev/staging only - allow Azure services + external access)
// ============================================================================

resource allowAzureServices 'Microsoft.Sql/servers/firewallRules@2023-08-01-preview' = if (!isProduction) {
  parent: sqlServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource allowAllForDev 'Microsoft.Sql/servers/firewallRules@2023-08-01-preview' = if (environment == 'dev') {
  parent: sqlServer
  name: 'AllowAllForDev'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '255.255.255.255'
  }
}

// ============================================================================
// Transparent Data Encryption
// ============================================================================

resource tde 'Microsoft.Sql/servers/databases/transparentDataEncryption@2023-08-01-preview' = {
  parent: sqlDatabase
  name: 'current'
  properties: {
    state: 'Enabled'
  }
}

// ============================================================================
// Auditing
// ============================================================================

resource sqlAudit 'Microsoft.Sql/servers/auditingSettings@2023-08-01-preview' = {
  parent: sqlServer
  name: 'default'
  properties: {
    state: 'Enabled'
    isAzureMonitorTargetEnabled: true
  }
}

// ============================================================================
// Security Alert Policy
// ============================================================================

resource securityAlert 'Microsoft.Sql/servers/securityAlertPolicies@2023-08-01-preview' = {
  parent: sqlServer
  name: 'default'
  properties: {
    state: 'Enabled'
  }
}

// ============================================================================
// Private Endpoint
// ============================================================================

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: 'pe-sql-${environment}'
  location: privateEndpointLocation
  tags: tags
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'pe-sql-${environment}'
        properties: {
          privateLinkServiceId: sqlServer.id
          groupIds: ['sqlServer']
        }
      }
    ]
  }
}

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.database.windows.net'
  location: 'global'
  tags: tags
}

resource privateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-11-01' = {
  parent: privateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-sql'
        properties: {
          privateDnsZoneId: privateDnsZone.id
        }
      }
    ]
  }
}

// ============================================================================
// Diagnostic Settings
// ============================================================================

resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'diag-sql-${environment}'
  scope: sqlDatabase
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      { category: 'SQLSecurityAuditEvents', enabled: true }
      { category: 'QueryStoreRuntimeStatistics', enabled: true }
    ]
    metrics: [
      { category: 'Basic', enabled: true }
      { category: 'InstanceAndAppAdvanced', enabled: true }
    ]
  }
}

// ============================================================================
// Outputs
// ============================================================================

output sqlServerId string = sqlServer.id
output sqlServerName string = sqlServer.name
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
output sqlDatabaseName string = sqlDatabase.name
output sqlDatabaseId string = sqlDatabase.id
