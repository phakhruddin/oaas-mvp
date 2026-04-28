# CI/CD Pipeline (GitHub Actions → ECR → ECS)

## Overview

This pipeline automates build, push, and deployment of OAAS services.

## Flow

```
Git push → GitHub Actions
  -> Build Docker images
  -> Push to ECR
  -> Trigger ECS deployment
```

## Requirements

### GitHub Variables

- AWS_REGION
- API_ECR_REPOSITORY
- WORKER_ECR_REPOSITORY
- ECS_CLUSTER
- API_ECS_SERVICE
- WORKER_ECS_SERVICE

### GitHub Secrets

- AWS_DEPLOY_ROLE_ARN

## Deployment Strategy

- Image tagged with commit SHA
- ECS service uses rolling deployment
- No downtime deployment

## Validation

- Check ECS service events
- Verify new task revision is running
- Check CloudWatch logs

## Future Enhancements

- Blue/green deployment (CodeDeploy)
- Canary releases
- Rollback automation
