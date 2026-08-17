# Nebula — Launch Retrospective & Post-Launch Decisions
**Date:** April 12, 2026  
**Attendees:** Maya (CEO), Raj (CTO), Priya (Founding Engineer), Alex (DevRel — started Apr 1)  
**Location:** Nebula HQ (sublet office, Mission District)

---

## Launch Results (March 29 - April 12)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Product Hunt upvotes | 500+ | 642 | ✅ |
| GitHub stars | 200+ | 387 | ✅ |
| Self-hosted trial signups | 100+ | 156 | ✅ |
| Design partner conversions | 3/3 | 2/3 | ⚠️ |
| Enterprise inbound leads | 10+ | 23 | ✅ |

**Note:** ByteBank didn't convert — their infra team blocked on "another tool to maintain."

---

## Decisions Made

### 1. ByteBank Churn: Accept and learn
**Decision:** Don't discount or extend trial for ByteBank. Close the POC, capture learnings.
**Cause:** Their blocker is organizational (infra team veto), not product. Discounting sets bad precedent.
**Trigger:** ByteBank CTO: "We love the product but infra won't approve another self-hosted tool."
**Tension:** Losing a design partner vs. holding pricing integrity.
**Recorded by:** Maya

### 2. Enterprise Sales Motion: Hire founding AE
**Decision:** Hire an Account Executive (AE) as employee #5. Target: close 5 enterprise deals by Q3.
**Cause:** 23 inbound enterprise leads but Maya is bottleneck. Need dedicated sales motion.
**Trigger:** Acme expanding from 50 to 500 seats — needs negotiation Maya doesn't have time for.
**Tension:** Early sales hire before product-market fit vs. leaving enterprise revenue on table.
**Recorded by:** Maya

### 3. Cloud-Hosted Option: Build "Nebula Cloud" (SaaS) for Q3
**Decision:** Start building a managed SaaS offering. Target beta: July, GA: September.
**Cause:** 40% of inbound leads asked "do you have a cloud version?" Self-hosted is a blocker for SMBs.
**Trigger:** 3 inbound leads from 10-20 person startups: "We don't have Kubernetes expertise."
**Tension:** Splits engineering focus vs. unlocks massive SMB market.
**Recorded by:** Raj

### 4. Integration Priority: Kubernetes + CI/CD first
**Decision:** Build native K8s operator + GitHub Actions/GitLab CI integration before other integrations.
**Cause:** 80% of self-hosted users run on K8s. CI integration = "install in pipeline" = viral adoption.
**Trigger:** Alex (DevRel) feedback: "Every demo request asks 'how do I install in my cluster?'"
**Tension:** Operator is complex vs. high-leverage distribution channel.
**Recorded by:** Priya

### 5. Pricing for Cloud: Usage-based + seat hybrid
**Decision:** Nebula Cloud pricing: $0.50/million requests + $19/dev/month (includes SSO, audit logs).
**Cause:** Self-hosted is seat-only. Cloud has real marginal cost (ingest/storage). Hybrid aligns value.
**Trigger:** Finance model: at 1B req/mo, pure seat pricing loses money on heavy users.
**Tension:** Complexity vs. fairness. Keep simple: 2 metrics only.
**Recorded by:** Maya

---

## Product Updates

- **v1.1 shipped:** Audit logs + RBAC (on schedule)
- **K8s operator:** Alpha working, 3 design partners testing
- **Cloud infrastructure:** Raj + Priya spiking ECS Fargate + ClickHouse Cloud

---

## Action Items

- [ ] Maya: Post AE job, target start date May 15 (target: Apr 20)
- [ ] Raj: Finalize Cloud architecture decision (ECS vs K8s vs Fly.io) (target: Apr 25)
- [ ] Priya: K8s operator beta release (target: May 15)
- [ ] Alex: Launch "Nebula in 5 min" video series (target: May 1)
- [ ] Maya: Negotiate Acme expansion (50→500 seats) (target: Apr 30)

---

**Next Meeting:** Apr 26 — Cloud architecture decision + AE interviews