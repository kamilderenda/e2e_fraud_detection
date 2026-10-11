param location string = 'polandcentral'

param acrName string = 'e2efraudacr'
param storageName string = 'e2efraudstorage'
param logAnalyticsName string = 'e2efraud-logs'
param postgresName string = 'fraudpostgres'
param containerAppsEnvironmentName string = 'e2e-fraud-env'
param apiContainerAppName string = 'fraud-api'
param mlflowContainerAppName string = 'fraud-mlflow'
param experimentJobName string = 'fraud-experiment-job'
param modelName string = 'Fraud_Detection_Model'

param postgresClientIp string

@secure()
param postgresAdminPassword string

// ── ACR ──────────────────────────────────────────────────────────────────────
module acr 'modules/acr.bicep' = {
  name: 'acr'
  params: {
    name: acrName
    location: location
  }
}

// ── Storage ───────────────────────────────────────────────────────────────────
module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    name: storageName
    location: location
  }
}

// ── Log Analytics ─────────────────────────────────────────────────────────────
module logAnalytics 'modules/loganalytics.bicep' = {
  name: 'logAnalytics'
  params: {
    name: logAnalyticsName
    location: location
  }
}

// ── PostgreSQL ────────────────────────────────────────────────────────────────
module postgres 'modules/postgres.bicep' = {
  name: 'postgres'
  params: {
    name: postgresName
    location: location
    adminPassword: postgresAdminPassword
    clientIp: postgresClientIp
  }
}

// ── Container Apps Environment ────────────────────────────────────────────────
module environment 'modules/environment.bicep' = {
  name: 'containerAppsEnvironment'
  params: {
    name: containerAppsEnvironmentName
    location: location
    logAnalyticsCustomerId: logAnalytics.outputs.customerId
    logAnalyticsSharedKey: logAnalytics.outputs.sharedKey
  }
}

// ── MLflow Container App ──────────────────────────────────────────────────────
module mlflow 'modules/mlflow.bicep' = {
  name: 'mlflowContainerApp'
  params: {
    name: mlflowContainerAppName
    location: location
    environmentId: environment.outputs.id
    acrLoginServer: acr.outputs.loginServer
    acrUsername: acr.outputs.username
    acrPassword: acr.outputs.password
    storageAccountName: storage.outputs.name
    storageAccountKey: storage.outputs.key
    postgresHost: postgres.outputs.fqdn
    postgresUser: 'postgres'
    postgresDatabase: 'fraud_db'
    postgresPassword: postgresAdminPassword
  }
}

// ── API Container App ─────────────────────────────────────────────────────────
module api 'modules/api.bicep' = {
  name: 'apiContainerApp'
  params: {
    name: apiContainerAppName
    location: location
    environmentId: environment.outputs.id
    acrLoginServer: acr.outputs.loginServer
    acrUsername: acr.outputs.username
    acrPassword: acr.outputs.password
    dbHost: postgres.outputs.fqdn
    dbName: 'fraud_db'
    dbUser: 'postgres'
    dbPassword: postgresAdminPassword
    mlflowUri: 'https://${mlflow.outputs.fqdn}'
    modelName: modelName
  }
}

// ── Experiment Job ────────────────────────────────────────────────────────────
module job 'modules/job.bicep' = {
  name: 'experimentJob'
  params: {
    name: experimentJobName
    location: location
    environmentId: environment.outputs.id
    acrLoginServer: acr.outputs.loginServer
    acrUsername: acr.outputs.username
    acrPassword: acr.outputs.password
    dbHost: postgres.outputs.fqdn
    dbName: 'fraud_db'
    dbUser: 'postgres'
    dbPassword: postgresAdminPassword
    mlflowUri: 'https://${mlflow.outputs.fqdn}'
    modelName: modelName
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
output acrLoginServer string = acr.outputs.loginServer
output postgresFqdn string = postgres.outputs.fqdn
output mlflowUrl string = 'https://${mlflow.outputs.fqdn}'
output apiUrl string = 'https://${api.outputs.fqdn}'
