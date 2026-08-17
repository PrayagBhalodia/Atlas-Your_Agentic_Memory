# Nebula — Founder Kickoff Meeting
**Date:** January 15, 2026  
**Attendees:** Maya (CEO), Raj (CTO), Priya (Founding Engineer)  
**Location:** Maya's apartment, SF

---

## The Vision

We're building **Nebula** — an API observability platform that actually helps developers debug production issues in minutes, not hours. The problem is simple: every team has logging, metrics, and tracing, but when something breaks at 2am, you're still grepping logs and correlating timestamps by hand.

**Core insight:** The data exists. The *context* doesn't. We auto-correlate requests across services, surface the "why" behind errors, and suggest fixes — all without requiring instrumentation changes.

---

## Decisions Made

### 1. Product Scope: Start with REST APIs only
**Decision:** Nebula v1 supports REST/JSON APIs only. GraphQL, gRPC, WebSockets are explicitly out of scope for MVP.
**Cause:** 80% of teams we talked to use REST. Adding protocol support multiplies complexity.
**Trigger:** Priya's spike showed GraphQL parsing would add 3+ weeks.
**Tension:** Broader market vs. shipping in 8 weeks.
**Recorded by:** Raj

### 2. Deployment Model: Self-hosted only for now
**Decision:** Nebula runs in the customer's VPC. No SaaS offering at launch.
**Cause:** Enterprise prospects (our ICP) require data residency and SOC2. SaaS adds 6+ months of compliance work.
**Trigger:** Three design partners said "we can't send request payloads to a third party."
**Tension:** SaaS is easier to sell/onboard vs. enterprise requirements.
**Recorded by:** Maya

### 3. Pricing: Free for teams up to 5 developers
**Decision:** Free tier up to 5 seats, then $49/dev/month. No usage-based pricing initially.
**Cause:** Bottom-up adoption needs zero friction. Seat-based is predictable for buyers.
**Trigger:** Competitor (Datadog APM) charges $31/host — we're per-dev, simpler mental model.
**Tension:** Leaving money on the table vs. adoption speed.
**Recorded by:** Maya

### 4. Tech Stack: Go + React + ClickHouse
**Decision:** Backend in Go, frontend React/TypeScript, ClickHouse for analytics storage.
**Cause:** Go for performance/concurrency. ClickHouse handles high-cardinality observability data cheaply.
**Trigger:** Raj's benchmark: ClickHouse 10x cheaper than TimescaleDB at our write volume.
**Tension:** Team knows Postgres best; ClickHouse is new operational burden.
**Recorded by:** Raj

### 5. Funding: Bootstrap to $1M ARR, then raise
**Decision:** No pre-seed. Pay ourselves $0, live off savings, raise Seed at $1M ARR.
**Cause:** We want control. Maya's last startup raised too early and lost product focus.
**Trigger:** Raj has 18 months runway personally; Maya has 24.
**Tension:** Slower growth vs. ownership/control.
**Recorded by:** Maya

---

## Action Items

- [ ] Raj: Set up ClickHouse cluster on AWS (target: Jan 22)
- [ ] Priya: Build request ingestion API + auto-correlation engine (target: Feb 15)
- [ ] Maya: Close 3 design partners with LOIs (target: Feb 1)
- [ ] All: Incorporate as Nebula Labs Inc. (Delaware C-corp) — DONE Jan 10

---

**Next Meeting:** Jan 29 — Design partner feedback + technical spike results