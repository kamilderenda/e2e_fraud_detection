param name string
param location string
param environmentId string
param acrLoginServer string
param acrUsername string
@secure()
param acrPassword string
param storageAccountName string
@secure()
param storageAccountKey string
param postgresHost string
param postgresUser string
param postgresDatabase string
@secure()
param postgresPassword string

var mlflowDbUri = 'postgresql://${postgresUser}:${uriComponent(postgresPassword)}@${postgresHost}:5432/${postgresDatabase}'
var storageConnectionString = 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageAccountKey};EndpointSuffix=core.windows.net'

resource mlflow 'Microsoft.App/containerApps@2024-03-01' = {
  name: name
  location: location
  properties: {
    managedEnvironmentId: environmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        allowInsecure: false
        targetPort: 5000
        transport: 'Auto'
      }
      registries: [
        {
          server: acrLoginServer
          username: acrUsername
          passwordSecretRef: 'acr-password'
        }
      ]
      secrets: [
        { name: 'acr-password', value: acrPassword }
        { name: 'mlflow-db-uri', value: mlflowDbUri }
        { name: 'azure-storage-connection-string', value: storageConnectionString }
      ]
    }
    template: {
      containers: [
        {
          name: name
          image: '${acrLoginServer}/fraud-mlflow:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'MLFLOW_BACKEND_STORE_URI', secretRef: 'mlflow-db-uri' }
            { name: 'AZURE_STORAGE_CONNECTION_STRING', secretRef: 'azure-storage-connection-string' }
            { name: 'MLFLOW_ARTIFACT_ROOT', value: 'wasbs://mlflow@${storageAccountName}.blob.core.windows.net/' }
          ]
          probes: [
            {
              type: 'Liveness'
              tcpSocket: { port: 5000 }
              periodSeconds: 10
              failureThreshold: 3
              timeoutSeconds: 5
              initialDelaySeconds: 0
            }
            {
              type: 'Readiness'
              tcpSocket: { port: 5000 }
              periodSeconds: 5
              failureThreshold: 48
              timeoutSeconds: 5
              initialDelaySeconds: 0
            }
            {
              type: 'Startup'
              tcpSocket: { port: 5000 }
              periodSeconds: 1
              failureThreshold: 240
              timeoutSeconds: 3
              initialDelaySeconds: 1
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
      }
    }
  }
}

output fqdn string = mlflow.properties.configuration.ingress.fqdn
