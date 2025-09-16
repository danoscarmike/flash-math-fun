#!/bin/bash

# Flash Math Fun - Google Cloud Run Deployment Script
# Usage: ./deploy.sh [PROJECT_ID] [REGION]

set -e

# Default values
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-west2"}
SERVICE_NAME="flash-math-fun"

echo "🚀 Deploying Flash Math Fun to Google Cloud Run"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated with gcloud. Please run:"
    echo "   gcloud auth login"
    exit 1
fi

# Set the project
echo "📋 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy using Cloud Build
echo "🏗️  Building and deploying with Cloud Build..."
gcloud builds submit --config cloudbuild.yaml --substitutions=_SERVICE_NAME=$SERVICE_NAME

# Get the service URL
echo "🌐 Getting service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo ""
echo "✅ Deployment complete!"
echo "🌐 Service URL: $SERVICE_URL"
echo "🏥 Health check: $SERVICE_URL/health"
echo ""
echo "📊 To view logs:"
echo "   gcloud run services logs tail $SERVICE_NAME --region=$REGION"
echo ""
echo "🛠️  To update the service:"
echo "   ./deploy.sh $PROJECT_ID $REGION"
