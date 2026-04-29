# Region-Aware Routing & Write Conflict Handling

This document describes how OAAS handles **multi-region writes and conflicts** after enabling DynamoDB Global Tables.

## Problem

With Global Tables:

- Both regions can accept writes
- Conflicts may occur

## Solution Overview

1. Region-aware routing (control WHERE writes go)
2. Conflict resolution (handle WHEN conflicts happen)

---

## Region-Aware Routing

### Strategy

- Reads → local region (low latency)
- Writes → primary writer region

### Configuration

```bash
export PRIMARY_WRITE_REGION=us-east-1
```

### Flow

```
Client → Route53
   → Region A (read/write decision)
   → RegionRouter decides target region
```

---

## Conflict Handling

### Strategy: Last Writer Wins

Each record includes:

```json
{
  "updated_at": "timestamp",
  "updated_by_region": "region"
}
```

### Resolution Logic

- Compare timestamps
- Latest update wins

---

## Best Practices

- Use idempotent writes
- Avoid cross-region simultaneous writes
- Prefer single-writer pattern per tenant

---

## Future Improvements

- CRDT-based conflict resolution
- Write fencing tokens
- Region pinning per tenant
