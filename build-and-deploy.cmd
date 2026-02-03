@echo off
REM Build and Deploy Commands for Azure Web App

REM Set your Azure resources
set ACR_NAME=your-acr-name
set RESOURCE_GROUP=your-resource-group
set APP_NAME=smoke-test-bot-app

echo Building Docker image...
docker build -t smoke-test-bot:latest .

echo Tagging image for ACR...
docker tag smoke-test-bot:latest %ACR_NAME%.azurecr.io/smoke-test-bot:latest

echo Logging into Azure Container Registry...
az acr login --name %ACR_NAME%

echo Pushing image to ACR...
docker push %ACR_NAME%.azurecr.io/smoke-test-bot:latest

echo Updating Azure Web App...
az webapp config container set ^
  --name %APP_NAME% ^
  --resource-group %RESOURCE_GROUP% ^
  --docker-custom-image-name %ACR_NAME%.azurecr.io/smoke-test-bot:latest

echo Restarting Web App...
az webapp restart --name %APP_NAME% --resource-group %RESOURCE_GROUP%

echo Deployment completed!
echo FastAPI: https://%APP_NAME%.azurewebsites.net
echo Streamlit: https://%APP_NAME%.azurewebsites.net:8501