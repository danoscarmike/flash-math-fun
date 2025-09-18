# Deployment Guide

This document explains how to set up conditional deployments for dev and prod environments using Google Cloud Build.

## Overview

The project now supports separate staging and prod deployments based on GitHub branches:
- **dev branch** → deploys to `flash-math-fun-staging` service
- **main branch** → deploys to `flash-math-fun-prod` service

## Files

- `cloudbuild.yaml` - Template configuration (not used directly)
- `cloudbuild-staging.yaml` - Staging environment configuration
- `cloudbuild-prod.yaml` - Production environment configuration

## Environment Differences

### Staging (dev branch)
- Service name: `flash-math-fun-staging`
- Memory: 512Mi
- CPU: 1
- Min instances: 0
- Max instances: 5
- Environment variable: `ENVIRONMENT=staging`

### Production (main branch)
- Service name: `flash-math-fun-prod`
- Memory: 1Gi
- CPU: 2
- Min instances: 1
- Max instances: 20
- Environment variable: `ENVIRONMENT=prod`

## Setting Up Cloud Build Triggers

### 1. Create Staging Trigger
```bash
gcloud builds triggers create github \
  --repo-name=flash_math_fun \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern="^dev$" \
  --build-config=cloudbuild-staging.yaml
```

### 2. Create Prod Trigger
```bash
gcloud builds triggers create github \
  --repo-name=flash_math_fun \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild-prod.yaml
```

## Manual Deployment

### Deploy to Staging
```bash
gcloud builds submit --config=cloudbuild-staging.yaml
```

### Deploy to Prod
```bash
gcloud builds submit --config=cloudbuild-prod.yaml
```

## Service URLs

After deployment, your services will be available at:
- **Staging**: `https://flash-math-fun-staging-XXXXX-uc.a.run.app`
- **Prod**: `https://flash-math-fun-prod-XXXXX-uc.a.run.app`

## Health Checks

Both environments include a health endpoint:
- `/health` - Returns service status and environment info

## Environment Variables

The `ENVIRONMENT` variable is automatically set based on the deployment:
- Staging deployments: `ENVIRONMENT=staging`
- Prod deployments: `ENVIRONMENT=prod`

You can access this in your application code to implement environment-specific behavior.