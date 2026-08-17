# Nebula — Q2 2026 Board Deck Summary
**Date:** July 12, 2026  
**Prepared by:** Maya (CEO) for Board Meeting  
**Attendees:** Maya, Raj, Sequoia Partner (observer), Independent Board Member (TBD)

---

## Executive Summary

**Nebula is the API observability platform that correlates requests across services automatically — zero instrumentation required.**

| Metric | Jan 2026 | Jun 2026 | Change |
|--------|----------|----------|--------|
| Team | 3 | 8 | +167% |
| ARR | $0 | $127k | ∞ |
| Self-Hosted Clusters | 0 | 847 | ∞ |
| Cloud Beta Customers | 0 | 15 | ∞ |
| GitHub Stars | 0 | 1,240 | ∞ |
| Runway | 14 mo | 22 mo | +57% |

**Key Insight:** Self-hosted adoption drives Cloud pipeline. 60% of Cloud beta signups came from self-hosted users.

---

## Product: Two Products, One Engine

### Nebula Self-Hosted (Community Edition — FREE)
- **Distribution engine:** 847 clusters, growing 40% MoM
- **K8s Operator:** 50+ stars, 12 production clusters
- **Integrations:** GitHub Actions, GitLab CI, Prometheus export
- **Revenue:** $0 (intentionally free — drives Cloud funnel)

### Nebula Cloud (Managed SaaS — $49/dev + usage)
- **Beta:** 15 customers, 2.3B req/week, 99.9% uptime
- **GA Target:** September 15, 2026
- **Pipeline:** $400k ARR (12 qualified opportunities)
- **Key Differentiator:** Hard multi-tenancy (schema-per-customer) + global Anycast ingestion

---

## Go-to-Market: Bottom-Up → Top-Down

### Funnel (June 2026)
```
Self-Hosted Trials (156) → Cloud Beta Signups (47) → Qualified Opps (12) → Closed Won (3)
        │                        │                        │                    │
      100%                      30%                      25%                 25%
```

### Sales Motion
- **DevRel (Alex):** Content, community, self-hosted adoption
- **AE Sam (West):** Enterprise expansion (Acme 50→500 seats)
- **AE Taylor (East):** New logo hunting, inbound qualification
- **Maya:** Strategic deals (>$100k), fundraising, hiring

### Marketing Channels (Validated)
1. **Technical Content:** "How we correlate 1M req/s with ClickHouse" — 45k views
2. **Product Hunt / HN:** Launch spikes, then long tail
3. **K8s Operator:** Organic GitHub → cluster installs → Cloud inquiry
4. **Enterprise Inbound:** 23 leads from launch, 12 qualified

---

## Competition

| Competitor | Position | Our Win Rate | Why We Win |
|------------|----------|--------------|------------|
| Datadog APM | Incumbent, $$$ | 60% | Self-hosted, zero-instrument, 10x cheaper |
| Grafana Cloud | Open source suite | 70% | Purpose-built for API debugging, not metrics |
| SigNoz | Open source APM | 80% | Better correlation, Cloud option, team support |
| Highlight.io | Session replay + errors | 50% | We're backend-focused, they're frontend |

**Moat Building:**
1. **Correlation Engine** — Core IP, open-sourced for trust, hard to replicate
2. **Self-Hosted → Cloud Funnel** — Unique distribution model
3. **Hard Multi-Tenancy** — Enterprise requirement, architectural commitment
4. **Nebula AI (R&D)** — Root cause analysis = category creation

---

## Financials

### Revenue (ARR)
| Segment | Jan | Feb | Mar | Apr | May | Jun |
|---------|-----|-----|-----|-----|-----|-----|
| Self-Hosted Pro | $0 | $0 | $0 | $0 | $0 | $0 |
| Cloud Beta | $0 | $0 | $0 | $0 | $9k | $18k |
| Enterprise (Self-Hosted) | $0 | $0 | $18k | $42k | $42k | $109k |
| **Total** | **$0** | **$0** | **$18k** | **$42k** | **$51k** | **$127k** |

### Burn & Runway
| Month | Headcount | Monthly Burn | Cash Balance | Runway |
|-------|-----------|--------------|--------------|--------|
| Jan | 3 | $45k | $650k | 14 mo |
| Mar | 4 | $65k | $520k | 8 mo |
| May | 5 | $85k | $350k | 4 mo |
| Jun (post-seed) | 8 | $140k | $2.7M | 22 mo |

**Seed Round:** $2.5M at $15M post (Sequoia lead) — Closed June 15

### Unit Economics (Cloud)
- **LTV/CAC:** 8.2x (early, small n)
- **Payback Period:** 3.2 months
- **Gross Margin:** 78% (ClickHouse Cloud + Fly.io variable cost)
- **Expansion Revenue:** 140% NRR (Acme 50→500 seats)

---

## Hiring Plan (H2 2026)

| Role | Target Start | Status | Budget |
|------|--------------|--------|--------|
| Senior Engineer (Platform) | July 15 | Offer out | $180k |
| Senior Engineer (AI/ML) | Aug 1 | Sourcing | $200k |
| AE (Enterprise) | Aug 15 | Interviewing | $160k OTE |
| Customer Success | Sep 1 | Planned | $140k |
| Security/Compliance | Oct 1 | Planned | $170k |

**Total H2 Burn Increase:** ~$85k/mo (fully loaded)

---

## Strategic Priorities Q3 2026

### 1. Cloud GA (September 15) — P0
- [ ] SOC2 Type 1 audit complete
- [ ] SLA (99.9%) + credits policy
- [ ] Billing v2 (usage metering, invoices, Stripe)
- [ ] Disaster recovery tested (RPO <1hr, RTO <4hr)
- [ ] 10 referenceable Cloud customers

### 2. Enterprise Motion — P0
- [ ] Close $500k new ARR (Sam + Taylor)
- [ ] Acme expansion to 1000 seats ($144k ARR)
- [ ] Security questionnaire library (answer once, reuse)
- [ ] Procurement process documented

### 3. Nebula AI Alpha — P1
- [ ] Root cause agent: 85% accuracy on benchmark
- [ ] Technical blog: "How we built an SRE agent"
- [ ] Waitlist: 100+ signups
- [ ] Design partners: 3 enterprise teams

### 4. Integrations — P1
- [ ] Datadog metrics export (GA)
- [ ] PagerDuty alert routing (GA)
- [ ] Slack incident collaboration (Beta)
- [ ] Terraform provider (Community)

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Cloud cost overrun at scale | Medium | High | Per-customer quotas, usage alerts, reserved ClickHouse capacity |
| Competitor launches free Cloud tier | High | Medium | Self-hosted free forever = distribution moat; AI differentiation |
| Key engineer burnout | Medium | High | 4-day work week trial (Jul-Sep), mandatory PTO |
| Enterprise sales cycle longer than planned | High | Medium | Pipeline 3x target, self-serve Cloud for SMB |
| ClickHouse Cloud vendor risk | Low | High | Self-managed ClickHouse runbooks ready, multi-cloud eval Q4 |

---

## Asks for Board

1. **Approve** H2 hiring plan (5 roles, $85k/mo burn increase)
2. **Introduce** 2 potential independent board members (devtools founders)
3. **Connect** to 3 enterprise buyers in network (fintech, healthtech, SaaS)
4. **Review** Nebula AI investment thesis (separate deep-dive next meeting)

---

## Appendix: 6-Month Decision Log

| Date | Decision | Category | Owner |
|------|----------|----------|-------|
| Jan 15 | REST-only MVP, self-hosted, free tier, Go+ClickHouse, bootstrap | Strategy | All |
| Feb 8 | Add GraphQL, installer, SSO, Team pricing tier | Product | All |
| Mar 1 | PH/HN launch, OSS core, DevRel hire, pricing freeze, audit logs | GTM | All |
| Apr 12 | Accept ByteBank churn, hire AE, build Cloud, K8s operator, Cloud pricing | Strategy | All |
| May 10 | Fly.io + ClickHouse Cloud, schema-per-tenant, $2.5M Seed, 3 hires, OSS boundary | Infra/Finance | All |
| Jun 28 | Cloud GA Sep 15, simplified pricing, free self-hosted, integrations, AI R&D, board | Strategy | All |

---

*End of Board Deck Summary*