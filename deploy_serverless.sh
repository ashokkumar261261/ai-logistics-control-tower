#!/bin/bash

# Configuration
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
FUNCTION_NAME="logistics-agent-func"
GATEWAY_ID="logistics-gateway"
CONFIG_ID="logistics-v1"

echo "🚀 Starting Serverless Deployment for $PROJECT_ID..."

# 1. Deploy Cloud Function
echo "📦 Deploying Cloud Function..."
gcloud functions deploy $FUNCTION_NAME \
    --gen2 \
    --runtime=python39 \
    --region=$REGION \
    --source=./backend \
    --entry-point=process_query \
    --trigger-http \
    --allow-unauthenticated \
    --set-env-vars "DATABASE_URL=bigquery://$PROJECT_ID/logistics_control_tower"

# Get Function URL
FUNCTION_URL=$(gcloud functions describe $FUNCTION_NAME --region=$REGION --gen2 --format='value(serviceConfig.uri)')
echo "✅ Function deployed at: $FUNCTION_URL"

# 2. Prepare API Gateway
echo "🛰️ Preparing API Gateway..."

# Ensure the API resource exists
gcloud api-gateway apis create $GATEWAY_ID --project=$PROJECT_ID || echo "API resource already exists"

cp backend/openapi.yaml backend/openapi_deploy.yaml
# Use sed to replace the placeholder
sed -i "s|FUNCTION_URL|$FUNCTION_URL|g" backend/openapi_deploy.yaml

# Create/Update API Config
gcloud api-gateway api-configs create $CONFIG_ID \
    --api=$GATEWAY_ID --openapi-spec=backend/openapi_deploy.yaml \
    --project=$PROJECT_ID || \
gcloud api-gateway api-configs create ${CONFIG_ID}-$(date +%s) \
    --api=$GATEWAY_ID --openapi-spec=backend/openapi_deploy.yaml \
    --project=$PROJECT_ID

# Create/Update Gateway
gcloud api-gateway gateways create $GATEWAY_ID \
    --api=$GATEWAY_ID --api-config=$CONFIG_ID \
    --location=$REGION --project=$PROJECT_ID || \
gcloud api-gateway gateways update $GATEWAY_ID \
    --api=$GATEWAY_ID --api-config=$CONFIG_ID \
    --location=$REGION --project=$PROJECT_ID

GATEWAY_URL=$(gcloud api-gateway gateways describe $GATEWAY_ID --location=$REGION --format='value(defaultHostname)')
echo "✅ Gateway live at: https://$GATEWAY_URL"

# 3. Deploy App Engine (Frontend)
echo "🌐 Deploying Streamlit to App Engine..."
# Update app.yaml with Gateway URL
sed -i "s|GATEWAY_URL|$GATEWAY_URL|g" app.yaml

gcloud app deploy --quiet

echo "🎊 ALL DONE!"
echo "Your AI Logistics Control Tower is live at: https://$PROJECT_ID.appspot.com"
