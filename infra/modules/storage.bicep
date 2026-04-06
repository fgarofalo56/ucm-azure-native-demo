// ============================================================================
// Storage Module - Azure Blob Storage with versioning & lifecycle
// ============================================================================

@description('Environment name')
param environment string

@description('Azure region')
param location string

@description('Project name prefix')
param projectName string

@description('Resource tags')
param tags object

@description('Subnet ID for private endpoint')
param subnetId string

@description('Log Analytics workspace ID for diagnostics')
param logAnalyticsWorkspaceId string

@description('App Managed Identity principal ID for role assignment')
param appManagedIdentityPrincipalId string

@description('Function Managed Identity principal ID for role assignment')
param funcManagedIdentityPrincipalId string

@description('Enable malware scanning staging container and Defender integration')
param enableMalwareScanning bool = false

// Storage account name (lowercase, no hyphens, max 24 chars)
var storageAccountName = 'st${replace(projectName, '-', '')}${environment}'
var containerName = 'assurancenet-documents'
var stagingContainerName = 'assurancenet-staging'
var isProduction = environment == 'prod'
var isDev = environment == 'dev'

// ============================================================================
// Storage Account
// ============================================================================

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: {
    name: isProduction ? 'Standard_GRS' : 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: isDev
    networkAcls: {
      defaultAction: isDev ? 'Allow' : 'Deny'
      bypass: 'AzureServices'
    }
    isHnsEnabled: false
  }
}

// ============================================================================
// Blob Services - Versioning, Soft Delete, Change Feed
// ============================================================================

resource blobServices 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    isVersioningEnabled: true
    changeFeed: {
      enabled: true
      retentionInDays: 90
    }
    deleteRetentionPolicy: {
      enabled: true
      days: 30
    }
    containerDeleteRetentionPolicy: {
      enabled: true
      days: 30
    }
  }
}

// ============================================================================
// Document Container
// ============================================================================

resource documentsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobServices
  name: containerName
  properties: {
    publicAccess: 'None'
  }
}

// Staging container for two-phase upload (malware scanning)
resource stagingContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = if (enableMalwareScanning) {
  parent: blobServices
  name: stagingContainerName
  properties: {
    publicAccess: 'None'
  }
}

// Dead letter container for Event Grid failures
resource deadLetterContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobServices
  name: 'dead-letter'
  properties: {
    publicAccess: 'None'
  }
}

// ============================================================================
// Lifecycle Management
// ============================================================================

resource lifecyclePolicy 'Microsoft.Storage/storageAccounts/managementPolicies@2023-05-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    policy: {
      rules: [
        {
          name: 'move-old-versions-to-cool'
          enabled: true
          type: 'Lifecycle'
          definition: {
            actions: {
              version: {
                tierToCool: {
                  daysAfterCreationGreaterThan: 90
                }
                tierToArchive: {
                  daysAfterCreationGreaterThan: 365
                }
              }
            }
            filters: {
              blobTypes: ['blockBlob']
              prefixMatch: ['assurancenet-documents/']
            }
          }
        }
        {
          name: 'delete-old-soft-deleted'
          enabled: true
          type: 'Lifecycle'
          definition: {
            actions: {
              version: {
                delete: {
                  daysAfterCreationGreaterThan: 730
                }
              }
            }
            filters: {
              blobTypes: ['blockBlob']
            }
          }
        }
      ]
    }
  }
}

// ============================================================================
// Private Endpoint
// ============================================================================

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: 'pe-blob-${environment}'
  location: location
  tags: tags
  properties: {
    subnet: {
      id: subnetId
    }
    privateLinkServiceConnections: [
      {
        name: 'pe-blob-${environment}'
        properties: {
          privateLinkServiceId: storageAccount.id
          groupIds: ['blob']
        }
      }
    ]
  }
}

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.blob.core.windows.net'
  location: 'global'
  tags: tags
}

resource privateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-11-01' = {
  parent: privateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-blob'
        properties: {
          privateDnsZoneId: privateDnsZone.id
        }
      }
    ]
  }
}

// ============================================================================
// RBAC - Storage Blob Data Contributor for Managed Identities
// ============================================================================

// Storage Blob Data Contributor role ID
var storageBlobDataContributorRoleId = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'

resource appBlobRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, appManagedIdentityPrincipalId, storageBlobDataContributorRoleId)
  scope: storageAccount
  properties: {
    principalId: appManagedIdentityPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
    principalType: 'ServicePrincipal'
  }
}

resource funcBlobRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, funcManagedIdentityPrincipalId, storageBlobDataContributorRoleId)
  scope: storageAccount
  properties: {
    principalId: funcManagedIdentityPrincipalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
    principalType: 'ServicePrincipal'
  }
}

// ============================================================================
// Diagnostic Settings
// ============================================================================

resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'diag-storage-${environment}'
  scope: blobServices
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      { categoryGroup: 'allLogs', enabled: true }
    ]
    metrics: [
      { category: 'Transaction', enabled: true }
      { category: 'Capacity', enabled: true }
    ]
  }
}

// ============================================================================
// Outputs
// ============================================================================

output storageAccountId string = storageAccount.id
output storageAccountName string = storageAccount.name
output documentsContainerName string = containerName
output stagingContainerName string = stagingContainerName
output blobEndpoint string = storageAccount.properties.primaryEndpoints.blob
