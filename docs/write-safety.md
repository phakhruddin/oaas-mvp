# Write Fencing & Idempotency

This document explains how OAAS ensures **safe writes in a distributed, multi-region system**.

## Problem

In distributed systems:

- Retries can duplicate work
- Cross-region writes can overwrite data

## Solution Overview

1. Write fencing (prevent stale writes)
2. Idempotency (prevent duplicate execution)

---

## Write Fencing

### Concept

Each write carries a **monotonic token**.

- Newer token → accepted
- Older token → rejected

### Flow

```
Client → request write
   → obtain fence token
   → send write with token
   → system validates token
```

### Result

- Prevents stale writes
- Ensures ordering

---

## Idempotency

### Concept

Same request should not execute twice.

### Strategy

- Generate idempotency key
- Store result
- Replay returns same result

### Example

```
POST /analyze
Idempotency-Key: abc123
```

---

## Combined Flow

```
request
 → idempotency check
 → fence validation
 → execute write
 → store result
```

---

## Production Notes

- Store fence tokens in DynamoDB (conditional write)
- Store idempotency keys with TTL
- Use request headers for idempotency key

---

## Next Step

- integrate with API layer
- persist state in DynamoDB
