# Nebula — Design Partner Feedback Sync
**Date:** February 8, 2026  
**Attendees:** Maya (CEO), Raj (CTO), Priya (Founding Engineer)  
**Location:** Zoom (design partners async feedback collected)

---

## Design Partner Status

| Partner | Company | Stage | Key Feedback |
|---------|---------|-------|--------------|
| Acme Corp | B2B SaaS, 200 eng | Active POC | "Correlation works but we need GraphQL support" |
| ByteBank | Fintech, 50 eng | Active POC | "Self-hosted install took 4 hours — too long" |
| CloudNine | DevTools, 30 eng | Signed LOI | "Pricing is great, but we need SSO for our audit" |

---

## Decisions Made

### 1. GraphQL Support: Add to MVP scope
**Decision:** Add GraphQL parsing to v1. Ship alongside REST.
**Cause:** Acme (largest design partner) made it a blocker for paid conversion. They have 40+ GraphQL services.
**Trigger:** Acme's VP Eng said "we can't adopt without GraphQL — 60% of our traffic."
**Tension:** Adds 3 weeks to launch vs. losing biggest design partner.
**Recorded by:** Raj

### 2. Installation: One-line Docker Compose + Helm chart
**Decision:** Invest 2 weeks in a `curl | bash` installer and Helm chart for K8s.
**Cause:** ByteBank's 4-hour install was "embarrassing" per Maya. Self-hosted must feel like SaaS.
**Trigger:** ByteBank CTO: "If install takes >30 min, my team won't champion this."
**Tension:** Engineering time on installer vs. core product features.
**Recorded by:** Priya

### 3. SSO/SAML: Add to v1 (not post-launch)
**Decision:** Implement SAML/OIDC SSO before public launch. Required for CloudNine and enterprise.
**Cause:** CloudNine's security review requires SSO. Enterprise deals stall without it.
**Trigger:** CloudNine legal: "No SSO = no contract. We're not the only one."
**Tension:** Auth is a rabbit hole. Scope strictly to SAML/OIDC, no custom providers.
**Recorded by:** Maya

### 4. Pricing Adjustment: Add "Team" tier at $29/dev
**Decision:** Insert a $29/dev/month tier (10 seats max) between Free and Pro ($49).
**Cause:** CloudNine has 12 developers — too big for Free, too small for Pro at $49.
**Trigger:** CloudNine asked for "something between free and $49."
**Tension:** More pricing complexity vs. capturing mid-market.
**Recorded by:** Maya

---

## Technical Updates

- **ClickHouse cluster:** Running on 3x r6g.xlarge (AWS). Ingesting 50M req/day from Acme POC.
- **Correlation engine:** 94% accuracy on Acme's trace data. GraphQL parser 60% done.
- **Installer:** `nebulactl install` draft working locally. Helm chart WIP.

---

## Action Items

- [ ] Raj: Finish GraphQL parser (target: Feb 28)
- [ ] Priya: Build `nebulactl install` + Helm chart (target: Mar 7)
- [ ] Maya: Negotiate CloudNine contract with SSO requirement (target: Feb 20)
- [ ] Raj: Spike SAML library options (target: Feb 14)

---

**Next Meeting:** Feb 22 — Pre-launch readiness review