# Build Runbook

...

## Step 35 — CI/CD Pipeline (GitHub Actions → ECR → ECS)

Commit:

ci(deploy): add GitHub Actions ECS deployment workflow  
docs: add CI/CD pipeline documentation  

Files changed:

- .github/workflows/deploy-ecs.yml  
- docs/cicd.md  

Purpose:

Automate build and deployment pipeline from GitHub to AWS ECS.

### Flow

Git push
  -> GitHub Actions
  -> Build Docker images
  -> Push to ECR
  -> Update ECS services

### Features

- OIDC-based AWS auth (no static keys)
- SHA-based image tagging
- Rolling ECS deployment
- Separate API and worker services

### Result

- Fully automated deployment pipeline
- Faster iteration and release cycle
- Reduced manual errors

### Next Step

next: secrets management (AWS Secrets Manager + rotation)
