param name string
param location string

resource acr 'Microsoft.ContainerRegistry/registries@2025-04-01' = {
  name: name
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
    anonymousPullEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

output loginServer string = acr.properties.loginServer
output username string = acr.listCredentials().username
output password string = acr.listCredentials().passwords[0].value
