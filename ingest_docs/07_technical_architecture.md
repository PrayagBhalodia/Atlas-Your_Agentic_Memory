# Nebula — Technical Architecture Decision Record
**Date:** January 20, 2026 (updated June 28, 2026)  
**Status:** ACCEPTED  
**Author:** Raj (CTO)

---

## Context

Building an API observability platform that correlates requests across microservices in real-time. Must handle high-cardinality data (request IDs, user IDs, trace IDs) at scale, with sub-second query latency for live debugging.

---

## Decisions

### ADR-001: ClickHouse for Analytics Storage
**Decision:** Use ClickHouse (self-hosted initially, ClickHouse Cloud for SaaS) as primary datastore for request/span/event data.
**Alternatives Considered:**
- TimescaleDB: PostgreSQL-compatible, but 10x storage cost at our cardinality
- Elasticsearch: Full-text optimized, not analytical; expensive at scale
- Custom on Parquet/S3: Too much engineering for v1
**Consequences:**
- + Columnar compression handles high cardinality efficiently
- + SQL interface familiar to team
- + Materialized views enable pre-aggregation
- - Operational complexity (merged into ClickHouse Cloud for SaaS)
- - Not transactional (use PostgreSQL for metadata)

### ADR-002: Go for Ingestion Pipeline
**Decision:** Write ingestion pipeline (receiver → parser → correlator → writer) in Go.
**Alternatives Considered:**
- Rust: Better memory safety, but slower team velocity
- Python: Fast prototyping, but GC pauses at 100k req/s
- Java: Heavy, team lacks expertise
**Consequences:**
- + Native concurrency (goroutines) matches ingestion model
- + Fast compilation, easy deployment (static binary)
- + Team already proficient
- - No generics (pre-1.18) — upgraded to Go 1.22

### ADR-003: Auto-Correlation via Request ID Propagation
**Decision:** Correlate requests by extracting/tracing `X-Request-ID` (and variants) across service boundaries. No mandatory instrumentation.
**Alternatives Considered:**
- OpenTelemetry mandatory: Higher adoption barrier
- eBPF kernel tracing: Too invasive for self-hosted
- Service mesh integration: Only works if mesh present
**Consequences:**
- + Zero-instrumentation onboarding
- + Works with any framework/language
- - Misses correlations if headers stripped
- - Cannot correlate async/message queue hops reliably

### ADR-004: Self-Hosted First, Cloud Second
**Decision:** Build self-hosted (Docker/Helm) as primary distribution. Cloud as managed wrapper.
**Alternatives Considered:**
- Cloud-only: Faster iteration, but excludes enterprise
- Hybrid from day 1: Split focus, delayed both
**Consequences:**
- + Enterprise trust (data never leaves VPC)
- + Product Hunt / HN community prefers self-hosted
- - Cloud architecture retrofitted (multi-tenancy added later)
- - Support burden: customer infra issues

### ADR-005: ClickHouse Cloud for Nebula Cloud (Multi-Tenant)
**Decision:** Use ClickHouse Cloud (managed) with schema-per-customer isolation for SaaS.
**Alternatives Considered:**
- Self-managed ClickHouse on K8s: Full control, but ops burden
- Single database + row-level security: Simpler, but compliance risk
- TimescaleDB Cloud: Cheaper, but cardinality limits
**Consequences:**
- + Zero database ops for team
- + Hard isolation satisfies enterprise security reviews
- + Automatic scaling per customer
- - Cost per customer higher (~$200/mo base)
- - Vendor dependency

### ADR-006: Fly.io for Compute (Nebula Cloud)
**Decision:** Run Cloud API/worker containers on Fly.io (global Anycast, per-customer machines).
**Alternatives Considered:**
- AWS ECS/Fargate: Standard, but complex networking for multi-tenant
- Kubernetes (EKS/GKE): Full control, but team has no K8s expertise
- Render/Railway: Simpler, but less networking control
**Consequences:**
- + `fly deploy` = 3 minutes
- + Private networking per customer (6PN)
- + Global Anycast for low-latency ingestion
- - Smaller ecosystem, fewer integrations
- - Pricing less predictable at scale

### ADR-007: Kubernetes Operator for Self-Hosted Distribution
**Decision:** Build Nebula K8s Operator (Custom Resource Definitions) for self-hosted installs.
**Alternatives Considered:**
- Helm only: Simpler, but no lifecycle management
- ArgoCD/Flux: Adds dependency, not self-contained
- Raw manifests: No updates/rollback
**Consequences:**
- + `kubectl apply -f nebula.yaml` → full lifecycle
- + Automatic upgrades, backup/restore, scaling
- + Fits GitOps workflows enterprises use
- - Operator SDK learning curve
- - CRD cluster-scoped permissions needed

---

## Architecture Diagram (Text)

```
┌─────────────────────────────────────────────────────────────────┐
│                        NEBULA CLOUD                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Fly.io      │  │  Fly.io      │  │  ClickHouse Cloud    │  │
│  │  (API GW)    │──│  (Workers)   │──│  (Per-Customer DB)   │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│         │                │                    │                 │
│         └────────────────┴────────────────────┘                 │
│                          │                                       │
│              ┌───────────▼───────────┐                           │
│              │   PostgreSQL (Meta)   │  ← Billing, Users, Org  │
│              └───────────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌─────────┐    ┌─────────┐      ┌─────────┐
        │Customer │    │Customer │      │Customer │
        │   A     │    │   B     │      │   C     │
        │(Fly App)│    │(Fly App)│      │(Fly App)│
        └────┬────┘    └────┬────┘      └────┬────┘
             │              │               │
             └──────────────┼───────────────┘
                            ▼
                   ┌─────────────────┐
                   │  ClickHouse     │
                   │  (Customer DB)  │
                   └─────────────────┘
```

---

## Self-Hosted Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    CUSTOMER VPC                             │
│  ┌──────────┐   ┌──────────────┐   ┌────────────────────┐  │
│  │  K8s     │   │  ClickHouse  │   │  PostgreSQL        │  │
│  │  Operator│──▶│  (3-node)    │   │  (Metadata)        │  │
│  └──────────┘   └──────────────┘   └────────────────────┘  │
│       │                                      │              │
│       ▼                                      ▼              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Nebula Pods (Deployment)                 │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │  │
│  │  │ Ingest  │ │Correlate│ │  Query  │ │  Web UI │    │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

## Open Questions (as of June 28)

1. **Async correlation:** How to correlate across message queues (Kafka, RabbitMQ)?
2. **Cost optimization:** ClickHouse Cloud cost at 100 customers? Model says ~$18k/mo.
3. **Disaster recovery:** Cross-region replication for Cloud customers?
4. **AI context window:** Root cause agent needs full trace — token cost at scale?