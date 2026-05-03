# OAAS Onboarding Flow

This document defines how a new user starts using OAAS.

## Goal

Time-to-value: under 5 minutes.

## Flow

1. User signs up (marketing site)
2. System creates tenant
3. API key is issued
4. Demo tenant is provisioned
5. User calls API

## API Example

```
POST /onboarding/demo
```

Response:

```
{
  "tenant_id": "demo-123",
  "api_key": "oaas_xxx",
  "next_steps": ["connect logs", "run analyze"]
}
```

## Design

- API keys issued securely
- Demo tenant created instantly
- No AWS setup required for demo

## Next Step

- Add UI onboarding wizard
- Persist tenants in DynamoDB
