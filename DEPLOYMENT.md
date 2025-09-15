# Flash Math Fun - Google Cloud Run Deployment

This guide explains how to deploy the Flash Match Fun app to Google Cloud Run using Google Cloud Build.

## Prerequisites

1. **Google Cloud Account**: Sign up at [Google Cloud Console](https://console.cloud.google.com/)
2. **gcloud CLI**: Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. **Docker**: Install [Docker](https://docs.docker.com/get-docker/) (for local testing)

## Quick Start

### 1. Set up your project

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create your-project-id

# Set the project
gcloud config set project your-project-id
```

### 2. Deploy to Cloud Run

```bash
# Make the script executable (if not already)
chmod +x deploy.sh

# Deploy the app
./deploy.sh your-project-id us-central1
```

### 3. Access your app

After deployment, you'll get a URL like:
```
https://flash-math-fun-xxxxx-uc.a.run.app
```

## Manual Deployment

If you prefer to deploy manually:

### 1. Build the container

```bash
# Build the Docker image
docker build -t gcr.io/your-project-id/flash-math-fun .

# Push to Google Container Registry
docker push gcr.io/your-project-id/flash-math-fun
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy flash-math-fun \
  --image gcr.io/your-project-id/flash-card-magic \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1
```

## Configuration

### Environment Variables

The app uses these environment variables:

- `PORT`: Port number (default: 8080, set automatically by Cloud Run)

### Resource Limits

- **Memory**: 512Mi (adjustable in `cloudbuild.yaml`)
- **CPU**: 1 vCPU (adjustable in `cloudbuild.yaml`)
- **Timeout**: 300 seconds
- **Min Instances**: 0 (scales to zero when not in use)
- **Max Instances**: 10

### Custom Domain (Optional)

To use a custom domain:

1. **Map your domain**:
   ```bash
   gcloud run domain-mappings create \
     --service flash-card-magic \
     --domain your-domain.com \
     --region us-central1
   ```

2. **Update DNS**: Add the CNAME record provided by Google Cloud

## Monitoring

### View Logs

```bash
# View recent logs
gcloud run services logs read flash-math-fun --region us-central1

# Follow logs in real-time
gcloud run services logs tail flash-math-fun --region us-central1
```

### Health Check

The app includes a health check endpoint:
```
GET https://your-app-url/health
```

Response:
```json
{
  "status": "healthy",
  "service": "flash-math-fun"
}
```

## Troubleshooting

### Common Issues

1. **Build fails**: Check that all dependencies are in `requirements.txt`
2. **App won't start**: Verify the PORT environment variable is being used
3. **Memory issues**: Increase memory allocation in `cloudbuild.yaml`
4. **Timeout errors**: Increase timeout in Cloud Run settings

### Debug Locally

```bash
# Build and run locally
docker build -t flash-math-fun .
docker run -p 8080:8080 flash-math-fun

# Test health endpoint
curl http://localhost:8080/health
```

## Cost Optimization

- **Min instances = 0**: App scales to zero when not in use
- **Memory allocation**: Start with 512Mi, adjust based on usage
- **CPU allocation**: Start with 1 vCPU, scale up if needed
- **Region selection**: Choose a region close to your users

## Security

- **HTTPS**: Automatically enabled by Cloud Run
- **Authentication**: Currently set to allow unauthenticated access
- **Network**: Runs in Google's secure infrastructure

## Updates

To update your deployment:

```bash
# Simply run the deploy script again
./deploy.sh your-project-id us-central1
```

The script will:
1. Build a new container image
2. Push it to Container Registry
3. Deploy the new version to Cloud Run
4. Provide the updated service URL

## Support

For issues with:
- **Google Cloud Run**: [Cloud Run Documentation](https://cloud.google.com/run/docs)
- **Google Cloud Build**: [Cloud Build Documentation](https://cloud.google.com/build/docs)
- **This app**: Check the main README.md file
