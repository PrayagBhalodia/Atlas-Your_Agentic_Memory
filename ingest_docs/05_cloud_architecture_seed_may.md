# Nebula — Cloud Architecture Decision & Seed Fundraise
**Date:** May 10, 2026  
**Attendees:** Maya (CEO), Raj (CTO), Priya (Founding Engineer), Alex (DevRel), Sam (AE — started May 5)  
**Location:** Nebula HQ

---

## Context

- **ARR:** $42k (Acme $24k, CloudNine $18k)
- **Pipeline:** $180k (5 enterprise deals in negotiation)
- **Team:** 5 people (3 eng, 1 DevRel, 1 AE)
- **Runway:** 14 months at current burn

---

## Decisions Made

### 1. Cloud Architecture: Fly.io + ClickHouse Cloud (not AWS ECS)
**Decision:** Build Nebula Cloud on Fly.io (compute) + ClickHouse Cloud (database). Not AWS ECS/K8s.
**Cause:** Fly.io gives us global Anycast, automatic scaling, and per-customer isolation without K8s ops burden. ClickHouse Cloud manages the hardest part.
**Trigger:** Raj's spike: Fly.io deploy = 3 min vs ECS = 45 min. ClickHouse Cloud = zero ops.
**Tension:** Vendor lock-in vs. speed. Fly.io is younger than AWS but fits our scale perfectly.
**Recorded by:** Raj

### 2. Multi-tenancy Model: Schema-per-customer (not row-level)
**Decision:** Each Cloud customer gets their own ClickHouse database + Fly.io app. Hard isolation.
**Cause:** Enterprise prospects (fintech, healthtech) require data isolation. Row-level security is leaky.
**Trigger:** Acme security review: "We need cryptographic proof our data isn't commingled."
**Tension:** Higher cost per customer vs. enterprise trust + compliance simplicity.
**Recorded by:** Priya

### 3. Seed Fundraise: Raise $2.5M now (not wait for $1M ARR)
**Decision:** Raise Seed round immediately. Target: $2.5M at $15M post. Use for Cloud build + 3 hires.
**Cause:** Cloud build needs 2 more engineers. Enterprise pipeline needs 2 AEs. Bootstrapping too slow.
**Trigger:** 3 VCs reached out after PH launch. Maya's advisor: "Take the money, build faster."
**Tension:** Dilution now vs. speed to market. Cloud is a race — competitors (Highlight, Grafana Cloud) moving fast.
**Recorded by:** Maya

### 4. Hiring Plan: 2 Senior Engineers + 1 AE by July
**Decision:** Hire 2 senior full-stack engineers (Cloud + Integrations) + 1 enterprise AE.
**Cause:** Cloud beta July 1 needs 2 eng. Sam (AE) at capacity with 5 deals.
**Trigger:** Sam: "I'm turning down qualified leads. Need partner by June."
**Tension:** Hiring fast risks culture vs. not hiring loses deals.
**Recorded by:** Maya

### 5. Open Source Strategy: Keep core OSS, Cloud proprietary
**Decision:** `nebulactl` + correlation engine stay MIT. Cloud UI, SSO, multi-tenancy, billing stay closed.
**Cause:** OSS drives adoption. Cloud features are enterprise value prop. Clear boundary.
**Trigger:** Competitor (SigNoz) open-sourced everything — hard to monetize.
**Tension:** Community expects more OSS vs. business needs moat.
**Recorded by:** Raj

---

## Fundraise Process

- **Target:** $2.5M at $15M post-money (14.3% dilution)
- **Lead:** Sequoia (partner Maya knows from last startup) — term sheet expected this week
- **Angels:** 5 devtool founders + 2 enterprise buyers committed
- **Timeline:** Close by May 31

---

## Product Updates

- **Cloud alpha:** Running on Fly.io, 3 design partners onboarded (internal + 2 friendly startups)
- **K8s operator:** Beta released, 50+ GitHub stars, 12 clusters running it
- **Integrations:** GitHub Action published, GitLab CI WIP

---

## Action Items

- [ ] Maya: Close Seed round (target: May 31)
- [ ] Raj: Cloud beta readiness — billing, quotas, per-customer dashboards (target: June 30)
- [ ] Priya: ClickHouse Cloud migration scripts + disaster recovery test (target: June 15)
- [ ] Sam: Close Acme expansion + 2 more enterprise deals (target: June 30)
- [ ] Alex: Cloud beta waitlist launch (target: June 1)

---

**Next Meeting:** May 24 — Fundraise close + Cloud beta plan