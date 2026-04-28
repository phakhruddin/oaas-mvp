# AWS Deployment Guide (ECS + SQS + API Gateway)

## Architecture

```
Client → API Gateway → ECS (FastAPI)
                       ↓
                     SQS
                       ↓
                ECS Worker (poller)
                       ↓
              CloudWatch + Slack
```

## Steps

### 1. Build Docker Images

```bash
docker build -t oaas-api .
docker build -t oaas-worker .
```

### 2. Push to ECR

```bash
aws ecr create-repository --repository-name oaas-api
aws ecr create-repository --repository-name oaas-worker
```

### 3. Deploy Infra

```bash
cd infra/terraform
terraform init
terraform apply
```

### 4. Configure Env

API container:

```text
SQS_QUEUE_URL
ENABLE_OTEL=true
```

Worker container:

```text
SQS_QUEUE_URL
SQS_DLQ_URL
ENABLE_OTEL=true
ENABLE_CLOUDWATCH_METRICS=true
```

### 5. Validate

- Hit API Gateway endpoint
- Check CloudWatch logs
- Verify SQS queue depth

## Notes

- Use Fargate for simplicity
- Attach IAM roles for SQS + CloudWatch
- Add ALB if not using direct API Gateway integration
