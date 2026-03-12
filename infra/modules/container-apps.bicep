// ============================================================================
// Container Apps Module - Gotenberg PDF Conversion Service
// ============================================================================

@description('Environment name')
param environment string

@description('Azure region')
param location string

@description('Project name prefix')
param projectName string

@description('Resource tags')
param tags object

@description('Container Apps subnet ID')
param subnetId string

@description('Log Analytics workspace ID')
param logAnalyticsWorkspaceId string

// ============================================================================
// Container Apps Environment
// ============================================================================

resource containerAppsEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-${projectName}-${environment}'
  location: location
  tags: tags
  properties: {
    vnetConfiguration: {
      infrastructureSubnetId: subnetId
      internal: true
    }
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: reference(logAnalyticsWorkspaceId, '2023-09-01').customerId
        sharedKey: listKeys(logAnalyticsWorkspaceId, '2023-09-01').primarySharedKey
      }
    }
  }
}

// ============================================================================
// Gotenberg Container App
// ============================================================================

resource gotenberg 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-gotenberg-${environment}'
  location: location
  tags: tags
  properties: {
    managedEnvironmentId: containerAppsEnv.id
    configuration: {
      ingress: {
        targetPort: 3000
        external: false
        transport: 'http'
      }
    }
    template: {
      containers: [
        {
          name: 'gotenberg'
          image: 'gotenberg/gotenberg:8'
          resources: {
            cpu: json('1.0')
            memory: '2Gi'
          }
          command: [
            'gotenberg'
            '--api-timeout=120s'
            '--libreoffice-restart-after=10'
            '--log-level=info'
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 5
        rules: [
          {
            name: 'http-scaler'
            http: {
              metadata: {
                concurrentRequests: '5'
              }
            }
          }
        ]
      }
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================

output containerAppsEnvId string = containerAppsEnv.id
output gotenbergFqdn string = gotenberg.properties.configuration.ingress.fqdn
