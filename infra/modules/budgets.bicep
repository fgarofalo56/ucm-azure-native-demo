// ============================================================================
// Budgets Module - Cost management & budget alerts
// ============================================================================

@description('Environment name')
param environment string

@description('Project name prefix')
param projectName string

@description('Resource tags')
param tags object

@description('Contact email for budget alerts')
param contactEmail string

var monthlyBudget = environment == 'prod' ? 5000 : (environment == 'staging' ? 1500 : 500)

// ============================================================================
// Monthly Budget
// ============================================================================

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-${projectName}-${environment}'
  properties: {
    category: 'Cost'
    amount: monthlyBudget
    timeGrain: 'Monthly'
    timePeriod: {
      startDate: '2026-03-01'
      endDate: '2027-12-31'
    }
    notifications: {
      atEightyPercent: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 80
        contactEmails: [contactEmail]
        thresholdType: 'Actual'
      }
      atOneHundredPercent: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 100
        contactEmails: [contactEmail]
        thresholdType: 'Actual'
      }
      forecastOneHundredPercent: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 100
        contactEmails: [contactEmail]
        thresholdType: 'Forecasted'
      }
    }
  }
}

// ============================================================================
// Outputs
// ============================================================================

output budgetName string = budget.name
output budgetAmount int = monthlyBudget
