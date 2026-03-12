// ============================================================================
// Event Hub Module - Splunk SIEM Integration
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

@description('Log Analytics workspace ID')
param logAnalyticsWorkspaceId string

var namespaceName = 'evhns-${projectName}-splunk-${environment}'

// ============================================================================
// Event Hub Namespace
// ============================================================================

resource eventHubNamespace 'Microsoft.EventHub/namespaces@2024-01-01' = {
  name: namespaceName
  location: location
  tags: tags
  sku: {
    name: 'Standard'
    tier: 'Standard'
    capacity: 2
  }
  properties: {
    isAutoInflateEnabled: true
    maximumThroughputUnits: 10
    minimumTlsVersion: '1.2'
    publicNetworkAccess: 'Disabled'
  }
}

// ============================================================================
// Event Hubs
// ============================================================================

resource auditHub 'Microsoft.EventHub/namespaces/eventhubs@2024-01-01' = {
  parent: eventHubNamespace
  name: 'evh-audit-logs'
  properties: {
    partitionCount: 4
    messageRetentionInDays: 7
  }
}

resource diagnosticHub 'Microsoft.EventHub/namespaces/eventhubs@2024-01-01' = {
  parent: eventHubNamespace
  name: 'evh-diagnostic-logs'
  properties: {
    partitionCount: 4
    messageRetentionInDays: 3
  }
}

// Consumer group for Splunk
resource splunkConsumerGroup 'Microsoft.EventHub/namespaces/eventhubs/consumergroups@2024-01-01' = {
  parent: auditHub
  name: 'splunk'
  properties: {
    userMetadata: 'Splunk Add-on for Microsoft Cloud Services'
  }
}

// ============================================================================
// Private Endpoint
// ============================================================================

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: 'pe-eh-${environment}'
  location: location
  tags: tags
  properties: {
    subnet: { id: subnetId }
    privateLinkServiceConnections: [
      {
        name: 'pe-eh-${environment}'
        properties: {
          privateLinkServiceId: eventHubNamespace.id
          groupIds: ['namespace']
        }
      }
    ]
  }
}

resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.servicebus.windows.net'
  location: 'global'
  tags: tags
}

resource privateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-11-01' = {
  parent: privateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      {
        name: 'privatelink-eh'
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
  name: 'diag-eh-${environment}'
  scope: eventHubNamespace
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      { category: 'ArchiveLogs', enabled: true }
      { category: 'OperationalLogs', enabled: true }
    ]
    metrics: [
      { category: 'AllMetrics', enabled: true }
    ]
  }
}

// ============================================================================
// Outputs
// ============================================================================

output eventHubNamespaceId string = eventHubNamespace.id
output eventHubNamespaceName string = eventHubNamespace.name
output auditHubName string = auditHub.name
output diagnosticHubName string = diagnosticHub.name
