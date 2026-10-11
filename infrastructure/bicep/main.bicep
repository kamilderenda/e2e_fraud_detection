targetScope = 'subscription'
param location string = 'polandcentral'
param resourceGroupName string = 'e2e_fraud'

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

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
}

//ACR
module acr 'modules/acr.bicep' = {
  scope: rg
  name: 'acr'
  params: {
    name: acrName
    location: location
  }
}

//STRG
module storage 'modules/storage.bicep' = {
  scope: rg
  name: 'storage'
  params: {
    name: storageName
    location: location
  }
}

//LOGs
module logAnalytics 'modules/loganalytics.bicep' = {
  scope: rg
  name: 'logAnalytics'
  params: {
    name: logAnalyticsName
    location: location
  }
}

//PostgreSQL
module postgres 'modules/postgres.bicep' = {
  scope: rg
  name: 'postgres'
  params: {
    name: postgresName
    location: location
    adminPassword: postgresAdminPassword
    clientIp: postgresClientIp
  }
}

//Container Env
module environment 'modules/environment.bicep' = {
  scope: rg
  name: 'containerAppsEnvironment'
  params: {
    name: containerAppsEnvironmentName
    location: location
    logAnalyticsCustomerId: logAnalytics.outputs.customerId
    logAnalyticsSharedKey: logAnalytics.outputs.sharedKey
  }
}

//mlflow container
module mlflow 'modules/mlflow.bicep' = {
  scope: rg
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

//Api container
module api 'modules/api.bicep' = {
  scope: rg
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

//Experiment job (container)
module job 'modules/job.bicep' = {
  scope: rg
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


output acrLoginServer string = acr.outputs.loginServer
output postgresFqdn string = postgres.outputs.fqdn
output mlflowUrl string = 'https://${mlflow.outputs.fqdn}'
output apiUrl string = 'https://${api.outputs.fqdn}'
