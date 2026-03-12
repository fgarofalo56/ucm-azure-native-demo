// ============================================================================
// Policy Module - Azure Policy assignments (NIST 800-53 Rev 5)
// ============================================================================

targetScope = 'subscription'

@description('Environment name')
param environment string

@description('Project name prefix')
param projectName string

// NIST SP 800-53 Rev 5 built-in initiative definition ID
var nist80053r5InitiativeId = '/providers/Microsoft.Authorization/policySetDefinitions/179d1daa-458f-4e47-8086-2a68d0d6c38f'

// ============================================================================
// NIST 800-53 Rev 5 Initiative Assignment
// ============================================================================

resource nistAssignment 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'nist-80053r5-${projectName}-${environment}'
  location: 'eastus'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    displayName: 'NIST SP 800-53 Rev 5 - ${projectName} ${environment}'
    description: 'Assigns the NIST SP 800-53 Rev 5 regulatory compliance initiative for AssuranceNet ${environment}'
    policyDefinitionId: nist80053r5InitiativeId
    enforcementMode: environment == 'prod' ? 'Default' : 'DoNotEnforce'
    parameters: {}
  }
}

// ============================================================================
// Custom Policy - Deny Storage without HTTPS
// ============================================================================

resource denyStorageWithoutHttps 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'deny-storage-no-https-${environment}'
  properties: {
    displayName: 'Deny Storage accounts without HTTPS - ${environment}'
    policyDefinitionId: '/providers/Microsoft.Authorization/policyDefinitions/404c3081-a854-4457-ae30-26a93ef643f9'
    enforcementMode: 'Default'
  }
}

// ============================================================================
// Custom Policy - Require resource tags
// ============================================================================

resource requireTags 'Microsoft.Authorization/policyAssignments@2024-04-01' = {
  name: 'require-env-tag-${environment}'
  properties: {
    displayName: 'Require Environment tag - ${environment}'
    policyDefinitionId: '/providers/Microsoft.Authorization/policyDefinitions/871b6d14-10aa-478d-b590-94f262ecfa99'
    enforcementMode: environment == 'prod' ? 'Default' : 'DoNotEnforce'
    parameters: {
      tagName: { value: 'Environment' }
    }
  }
}
