# DynamoDB Global Tables (Multi-Region Data Replication)

This document explains how OAAS achieves **multi-region data consistency** using DynamoDB Global Tables.

## Architecture

```
Primary Region (us-east-1)
    ↔ (replication)
Secondary Region (us-west-2)
```

## Key Features

- Active-active replication
- Low-latency local reads
- Automatic cross-region sync
- No manual failover required

## Table Design

Partition key:

```
pk (tenant_id)
```

Sort key:

```
sk (entity type, e.g., job_id)
```

## Terraform Usage

```
module "dynamodb_global" {
  source = "./modules/dynamodb-global"

  project_name    = "oaas-mvp"
  table_name      = "oaas-global"
  replica_regions = ["us-west-2"]
}
```

## Use Cases

- Tenant metadata
- Job state tracking
- Processing checkpoints

## Failure Behavior

If primary region fails:

1. Route53 redirects traffic
2. Secondary region serves API
3. DynamoDB already contains replicated data
4. System continues without data loss

## Notes

- DynamoDB Global Tables use eventual consistency
- Conflict resolution is last-writer-wins
- Use idempotent writes for safety

## Next Step

- Add region-aware routing
- Add write conflict handling
