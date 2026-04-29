# Multi-Region Failover (Route53 + Health Checks)

This document describes how the OAAS MVP achieves high availability using AWS Route53 failover routing.

## Architecture

```
Client
  -> Route53 (Failover Policy)
       -> Primary Region (ECS + ALB)
       -> Secondary Region (ECS + ALB)
```

## Key Components

### 1. Route53 Health Checks

- HTTPS health checks to `/health`
- Runs every 30 seconds
- Fails after 3 consecutive failures

### 2. Failover Routing Policy

- PRIMARY record routes to primary region
- SECONDARY record is standby
- Traffic automatically shifts when primary fails

### 3. Application Requirement

API must expose:

```
GET /health
```

Response:

```json
{ "status": "ok" }
```

## Failover Flow

1. Route53 checks primary endpoint
2. If unhealthy → Route53 marks primary DOWN
3. Traffic shifts to secondary region
4. System continues serving requests

## Terraform Usage

```
module "route53_failover" {
  source = "./modules/route53-failover"

  project_name        = "oaas-mvp"
  domain_name         = "api.example.com"
  hosted_zone_id      = "ZXXXXXXXX"

  primary_dns_name    = aws_lb.primary.dns_name
  secondary_dns_name  = aws_lb.secondary.dns_name
}
```

## Notes

- TTL is set low (60s) for fast failover
- Secondary region must be fully deployed and ready
- Data layer (if added later) must also support multi-region

## Next Step

- Add global data replication (DynamoDB Global Tables)
- Add region-aware routing
