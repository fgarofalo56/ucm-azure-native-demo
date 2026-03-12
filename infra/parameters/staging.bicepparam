using '../main.bicep'

param environment = 'staging'
param location = 'eastus'
param projectName = 'assurancenet'
param tags = {
  Project: 'AssuranceNet'
  ManagedBy: 'bicep'
  Application: 'UCM-Migration'
  CostCenter: 'FSIS-IT'
}
param sqlAdminObjectId = '866a2e12-0fee-4c99-923c-7cdfd61e08cd'
param sqlAdminLogin = 'fgarofalo@limitlessdata.ai'
param sqlAdminPrincipalType = 'User'
param contactEmail = 'fgarofalo@limitlessdata.ai'
