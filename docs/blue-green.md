# Blue/Green Deployment (ECS + CodeDeploy)

## Overview
Blue/green deployment enables zero-downtime releases with safe rollback.

## Flow

New version → Green environment  
→ Traffic shifts gradually  
→ Monitor health  
→ Promote green → terminate blue  

## Strategy

- Canary: 10% traffic for 5 minutes  
- Full cutover after validation  

## Rollback

- Automatic on CloudWatch alarms  
- Automatic on deployment failure  

## Benefits

- Zero downtime  
- Safe deployments  
- Fast rollback  

## Requirements

- Two target groups (blue + green)  
- ALB listeners  
- CodeDeploy IAM role