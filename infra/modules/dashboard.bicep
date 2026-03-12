// ============================================================================
// Dashboard Module - Azure Operational Dashboard
// ============================================================================

@description('Environment name')
param environment string

@description('Azure region')
param location string

@description('Project name prefix')
param projectName string

@description('Resource tags')
param tags object

@description('Log Analytics workspace ID')
param logAnalyticsWorkspaceId string

@description('Backend App Insights ID')
param backendAppInsightsId string

// ============================================================================
// Operational Dashboard
// ============================================================================

resource dashboard 'Microsoft.Portal/dashboards@2020-09-01-preview' = {
  name: 'dash-${projectName}-ops-${environment}'
  location: location
  tags: union(tags, { 'hidden-title': 'AssuranceNet Operations - ${environment}' })
  properties: {
    lenses: [
      {
        order: 0
        parts: [
          {
            position: { x: 0, y: 0, colSpan: 6, rowSpan: 4 }
            metadata: {
              type: 'Extension/Microsoft_OperationsManagementSuite_Workspace/PartType/LogsDashboardPart'
              inputs: [
                { name: 'resourceTypeMode', value: 'workspace' }
                { name: 'ComponentId', value: logAnalyticsWorkspaceId }
                {
                  name: 'Query'
                  value: 'AppRequests | where TimeGenerated > ago(24h) | summarize count() by bin(TimeGenerated, 1h) | render timechart'
                }
                { name: 'PartTitle', value: 'API Requests (24h)' }
              ]
            }
          }
          {
            position: { x: 6, y: 0, colSpan: 6, rowSpan: 4 }
            metadata: {
              type: 'Extension/Microsoft_OperationsManagementSuite_Workspace/PartType/LogsDashboardPart'
              inputs: [
                { name: 'resourceTypeMode', value: 'workspace' }
                { name: 'ComponentId', value: logAnalyticsWorkspaceId }
                {
                  name: 'Query'
                  value: 'AppRequests | where TimeGenerated > ago(24h) | summarize percentile(DurationMs, 50), percentile(DurationMs, 95), percentile(DurationMs, 99) by bin(TimeGenerated, 5m) | render timechart'
                }
                { name: 'PartTitle', value: 'API Latency Percentiles (24h)' }
              ]
            }
          }
          {
            position: { x: 0, y: 4, colSpan: 6, rowSpan: 4 }
            metadata: {
              type: 'Extension/Microsoft_OperationsManagementSuite_Workspace/PartType/LogsDashboardPart'
              inputs: [
                { name: 'resourceTypeMode', value: 'workspace' }
                { name: 'ComponentId', value: logAnalyticsWorkspaceId }
                {
                  name: 'Query'
                  value: 'AppExceptions | where TimeGenerated > ago(24h) | summarize count() by bin(TimeGenerated, 1h), ProblemId | render barchart'
                }
                { name: 'PartTitle', value: 'Errors by Type (24h)' }
              ]
            }
          }
          {
            position: { x: 6, y: 4, colSpan: 6, rowSpan: 4 }
            metadata: {
              type: 'Extension/HubsExtension/PartType/MonitorChartPart'
              inputs: [
                { name: 'resourceId', value: backendAppInsightsId }
              ]
            }
          }
        ]
      }
    ]
  }
}

// ============================================================================
// Outputs
// ============================================================================

output dashboardId string = dashboard.id
