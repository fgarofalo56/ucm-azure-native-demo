// ============================================================================
// Event Grid Module - Storage blob events to Function App
// ============================================================================

@description('Environment name')
param environment string

@description('Project name prefix')
param projectName string

@description('Resource tags')
param tags object

@description('Storage account ID')
param storageAccountId string

@description('Storage account name')
param storageAccountName string

@description('Function App ID for event subscription endpoint')
param functionAppId string

@description('Log Analytics workspace ID')
param logAnalyticsWorkspaceId string

// ============================================================================
// System Topic (Blob Storage events)
// ============================================================================

resource systemTopic 'Microsoft.EventGrid/systemTopics@2024-06-01-preview' = {
  name: 'evgt-storage-${environment}'
  location: resourceGroup().location
  tags: tags
  properties: {
    source: storageAccountId
    topicType: 'Microsoft.Storage.StorageAccounts'
  }
}

// ============================================================================
// Event Subscription - PDF Conversion trigger
// ============================================================================

resource eventSubscription 'Microsoft.EventGrid/systemTopics/eventSubscriptions@2024-06-01-preview' = {
  parent: systemTopic
  name: 'evgs-pdf-convert'
  properties: {
    destination: {
      endpointType: 'AzureFunction'
      properties: {
        resourceId: '${functionAppId}/functions/pdf_converter'
        maxEventsPerBatch: 1
        preferredBatchSizeInKilobytes: 64
      }
    }
    filter: {
      includedEventTypes: [
        'Microsoft.Storage.BlobCreated'
      ]
      subjectBeginsWith: '/blobServices/default/containers/assurancenet-documents'
      advancedFilters: [
        {
          operatorType: 'StringContains'
          key: 'subject'
          values: ['/blob/']
        }
        {
          operatorType: 'StringNotEndsWith'
          key: 'subject'
          values: ['.pdf']
        }
      ]
    }
    deadLetterDestination: {
      endpointType: 'StorageBlob'
      properties: {
        resourceId: storageAccountId
        blobContainerName: 'dead-letter'
      }
    }
    retryPolicy: {
      maxDeliveryAttempts: 3
      eventTimeToLiveInMinutes: 1440
    }
  }
}

// ============================================================================
// Diagnostic Settings
// ============================================================================

resource diagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'diag-evgt-${environment}'
  scope: systemTopic
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      { category: 'DeliveryFailures', enabled: true }
      { category: 'PublishFailures', enabled: true }
    ]
    metrics: [
      { category: 'AllMetrics', enabled: true }
    ]
  }
}

// ============================================================================
// Outputs
// ============================================================================

output systemTopicId string = systemTopic.id
output systemTopicName string = systemTopic.name
