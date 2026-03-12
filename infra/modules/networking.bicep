// ============================================================================
// Networking Module - VNet, Subnets, NSGs
// ============================================================================

@description('Environment name')
param environment string

@description('Azure region')
param location string

@description('Project name prefix')
param projectName string

@description('Resource tags')
param tags object

// VNet address space
var vnetAddressPrefix = '10.0.0.0/16'
var subnets = {
  backend: { prefix: '10.0.1.0/24', name: 'snet-backend' }
  functions: { prefix: '10.0.2.0/24', name: 'snet-functions' }
  privateEndpoints: { prefix: '10.0.3.0/24', name: 'snet-private-endpoints' }
  containerApps: { prefix: '10.0.5.0/24', name: 'snet-container-apps' }
}

// ============================================================================
// Network Security Groups
// ============================================================================

resource nsgBackend 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: 'nsg-backend-${environment}'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowFrontDoorInbound'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: 'AzureFrontDoor.Backend'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '443'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          priority: 4096
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

resource nsgFunctions 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: 'nsg-functions-${environment}'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowEventGridInbound'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: 'AzureEventGrid'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '443'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          priority: 4096
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

resource nsgPrivateEndpoints 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: 'nsg-private-endpoints-${environment}'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowBackendSubnet'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: subnets.backend.prefix
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
      {
        name: 'AllowFunctionsSubnet'
        properties: {
          priority: 110
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: subnets.functions.prefix
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          priority: 4096
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

resource nsgContainerApps 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
  name: 'nsg-container-apps-${environment}'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'AllowFunctionsSubnet'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: subnets.functions.prefix
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '3000'
        }
      }
      {
        name: 'DenyAllInbound'
        properties: {
          priority: 4096
          direction: 'Inbound'
          access: 'Deny'
          protocol: '*'
          sourceAddressPrefix: '*'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '*'
        }
      }
    ]
  }
}

// ============================================================================
// Virtual Network
// ============================================================================

resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' = {
  name: 'vnet-${projectName}-${environment}'
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [vnetAddressPrefix]
    }
    subnets: [
      {
        name: subnets.backend.name
        properties: {
          addressPrefix: subnets.backend.prefix
          networkSecurityGroup: { id: nsgBackend.id }
          delegations: [
            {
              name: 'Microsoft.Web.serverFarms'
              properties: {
                serviceName: 'Microsoft.Web/serverFarms'
              }
            }
          ]
        }
      }
      {
        name: subnets.functions.name
        properties: {
          addressPrefix: subnets.functions.prefix
          networkSecurityGroup: { id: nsgFunctions.id }
          delegations: [
            {
              name: 'Microsoft.Web.serverFarms'
              properties: {
                serviceName: 'Microsoft.Web/serverFarms'
              }
            }
          ]
        }
      }
      {
        name: subnets.privateEndpoints.name
        properties: {
          addressPrefix: subnets.privateEndpoints.prefix
          networkSecurityGroup: { id: nsgPrivateEndpoints.id }
        }
      }
      {
        name: subnets.containerApps.name
        properties: {
          addressPrefix: subnets.containerApps.prefix
          networkSecurityGroup: { id: nsgContainerApps.id }
          delegations: [
            {
              name: 'Microsoft.App.environments'
              properties: {
                serviceName: 'Microsoft.App/environments'
              }
            }
          ]
        }
      }
    ]
  }
}

// ============================================================================
// Outputs
// ============================================================================

output vnetId string = vnet.id
output vnetName string = vnet.name
output backendSubnetId string = vnet.properties.subnets[0].id
output functionsSubnetId string = vnet.properties.subnets[1].id
output privateEndpointSubnetId string = vnet.properties.subnets[2].id
output containerAppsSubnetId string = vnet.properties.subnets[3].id
