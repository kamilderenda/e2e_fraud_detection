param name string
param location string
param environmentId string
param acrLoginServer string
param acrUsername string
@secure()
param acrPassword string
param dbHost string
param dbName string
param dbUser string
@secure()
param dbPassword string
param mlflowUri string
param modelName string

resource api 'Microsoft.App/containerApps@2024-03-01' = {
  name: name
  location: location
  properties: {
    managedEnvironmentId: environmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        allowInsecure: false
        targetPort: 8000
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
        { name: 'db-password',  value: dbPassword }
      ]
    }
    template: {
      containers: [
        {
          name: name
          image: '${acrLoginServer}/fraud-api:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'MLFLOW_TRACKING_URI', value: mlflowUri }
            { name: 'DB_HOST',             value: dbHost }
            { name: 'DB_PORT',             value: '5432' }
            { name: 'DB_NAME',             value: dbName }
            { name: 'DB_USER',             value: dbUser }
            { name: 'DB_PASSWORD',         secretRef: 'db-password' }
            { name: 'MODEL_NAME',          value: modelName }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 10
      }
    }
  }
}

output fqdn string = api.properties.configuration.ingress.fqdn
