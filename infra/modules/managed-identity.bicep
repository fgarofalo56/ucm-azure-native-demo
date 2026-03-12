// ============================================================================
// Managed Identity Module - User-assigned MIs for App & Functions
// ============================================================================

@description('Environment name')
param environment string

@description('Azure region')
param location string

@description('Project name prefix')
param projectName string

@description('Resource tags')
param tags object

// ============================================================================
// App Service Managed Identity
// ============================================================================

resource appManagedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'mi-app-${projectName}-${environment}'
  location: location
  tags: tags
}

// ============================================================================
// Functions Managed Identity
// ============================================================================

resource funcManagedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'mi-func-${projectName}-${environment}'
  location: location
  tags: tags
}

// ============================================================================
// Outputs
// ============================================================================

output appManagedIdentityId string = appManagedIdentity.id
output appManagedIdentityPrincipalId string = appManagedIdentity.properties.principalId
output appManagedIdentityClientId string = appManagedIdentity.properties.clientId
output funcManagedIdentityId string = funcManagedIdentity.id
output funcManagedIdentityPrincipalId string = funcManagedIdentity.properties.principalId
output funcManagedIdentityClientId string = funcManagedIdentity.properties.clientId
