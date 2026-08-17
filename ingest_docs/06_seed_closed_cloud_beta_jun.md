# Nebula — Seed Closed, Cloud Beta Launched, Team Growing
**Date:** June 28, 2026  
**Attendees:** Maya (CEO), Raj (CTO), Priya (Founding Engineer), Alex (DevRel), Sam (AE), **New hires:** Jordan (Senior Engineer), Casey (Senior Engineer), Taylor (AE)  
**Location:** Nebula HQ (new office, SoMa)

---

## Major Milestones

✅ **Seed Round CLOSED:** $2.5M at $15M post (Sequoia lead, 8 angels) — wired June 15  
✅ **Nebula Cloud Beta LAUNCHED:** 15 companies onboarded, 2.3B requests ingested week 1  
✅ **Team DOUBLED:** 5 → 8 people in 6 weeks  
✅ **ARR:** $127k (Acme expanded to $72k, CloudNine $18k, 3 new Cloud beta converts at $3k/mo each)

---

## Decisions Made

### 1. Cloud GA Date: September 15 (12 weeks from beta)
**Decision:** General Availability September 15. Beta feedback → hardening → launch.
**Cause:** Beta metrics strong: 99.9% uptime, p99 latency <200ms, zero data loss incidents.
**Trigger:** 3 beta customers asked for contracts. "When can we sign?"
**Tension:** More beta time = more polish vs. revenue now.
**Recorded by:** Raj

### 2. Pricing Update: Cloud Pro at $49/dev + $0.30/M req (simplified)
**Decision:** Simplify Cloud pricing to $49/dev/month (includes 10M req) + $0.30/M overage. SSO + audit logs included.
**Cause:** Beta users confused by hybrid model. "$49/dev, simple overage" tested better in sales calls.
**Trigger:** Sam: "Every call I explain pricing for 10 minutes. Just make it simple."
**Tension:** Heavy users pay less vs. sales velocity.
**Recorded by:** Maya

### 3. Self-Hosted "Community Edition" Free Forever
**Decision:** Self-hosted version free for unlimited seats. Cloud features (SSO, audit, RBAC) stay Cloud-only.
**Cause:** Compete with SigNoz/Grafana on adoption. Free self-hosted = distribution engine for Cloud.
**Trigger:** Alex: "Every HN comment asks 'why not just use SigNoz free?'"
**Tension:** Cannibalizes self-hosted Pro ($49) vs. drives Cloud funnel.
**Recorded by:** Raj

### 4. Integration Roadmap: Datadog + PagerDuty + Slack (Q3)
**Decision:** Build native integrations for Datadog (metrics export), PagerDuty (alert routing), Slack (incident collaboration).
**Cause:** Enterprise buyers expect these. "Does it integrate with our stack?" is question #1.
**Trigger:** Acme expansion blocked on "Datadog integration for executive dashboards."
**Tension:** Integration maintenance burden vs. enterprise checkbox requirements.
**Recorded by:** Priya

### 5. Second Product: "Nebula AI" — Root Cause Analysis Agent
**Decision:** Start R&D on AI-powered root cause analysis. Target: alpha Q4, beta Q1 2027.
**Cause:** Differentiation. Every observability tool has dashboards. None *explain* the outage.
**Trigger:** Raj's spike: Gemini 1.5 Pro + our correlated context = 78% accuracy on root cause.
**Tension:** Focus risk vs. massive moat if it works.
**Recorded by:** Raj

### 6. Board Formation: Add Sequoia Partner + Independent
**Decision:** Formal board: Maya, Raj, Sequoia Partner (observer), 1 independent (target: devtools founder).
**Cause:** Governance hygiene post-seed. Independent brings scaling experience.
**Trigger:** Sequoia term sheet required board seat (observer).
**Tension:** Formality vs. early-stage agility.
**Recorded by:** Maya

---

## Team Updates

| Role | Person | Start Date | Focus |
|------|--------|------------|-------|
| Senior Engineer | Jordan | June 10 | Cloud platform (billing, quotas, multi-tenancy) |
| Senior Engineer | Casey | June 17 | Integrations (Datadog, PagerDuty, Slack) |
| AE | Taylor | June 24 | Enterprise sales (East Coast territory) |

---

## Metrics Dashboard (June 28)

| Metric | Value | Trend |
|--------|-------|-------|
| ARR | $127k | +202% MoM |
| Cloud Beta Customers | 15 | +150% WoW |
| Self-Hosted Clusters | 847 | +40% MoM |
| GitHub Stars | 1,240 | +220% MoM |
| Team Size | 8 | +60% MoM |
| Runway | 22 months | (post-seed) |

---

## Action Items

- [ ] Maya: Recruit independent board member (target: July 31)
- [ ] Raj: Cloud GA hardening — SLA, disaster recovery, SOC2 Type 1 prep (target: Sep 1)
- [ ] Priya: Datadog integration alpha (target: July 31)
- [ ] Casey: PagerDuty + Slack integrations (target: Aug 15)
- [ ] Sam + Taylor: Close $500k pipeline by Q3 end (target: Sep 30)
- [ ] Alex: Launch "Nebula AI" waitlist + technical blog (target: July 15)
- [ ] Jordan: Implement usage-based billing + metering (target: Aug 1)

---

## The 6-Month Arc

**January:** 3 founders, idea, $0 revenue, apartment  
**February:** 3 design partners, GraphQL pivot, SSO commitment  
**March:** Public launch, 642 PH upvotes, 156 trials, DevRel hired  
**April:** 2/3 design partners converted, AE hired, Cloud decision  
**May:** $2.5M Seed closed, Cloud architecture locked, 3 hires started  
**June:** Cloud Beta live, $127k ARR, team of 8, AI R&D started

---

**Next Meeting:** July 12 — Q2 Board Meeting + Cloud GA Readiness Review