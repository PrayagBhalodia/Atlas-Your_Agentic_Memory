# Nebula — Pre-Launch Strategy & GTM Decision
**Date:** March 1, 2026  
**Attendees:** Maya (CEO), Raj (CTO), Priya (Founding Engineer)  
**Location:** Offsite, Oakland

---

## Launch Timeline

**Target Public Launch: March 29, 2026 (4 weeks)**

### Current Status
- ✅ REST + GraphQL ingestion working
- ✅ Auto-correlation engine at 96% accuracy
- ✅ `nebulactl install` + Helm chart shipping
- ✅ SAML/OIDC SSO implemented (Okta, Azure AD, Google)
- ✅ 3 design partners: Acme (converting), ByteBank (converting), CloudNine (signed $18k/yr)

---

## Decisions Made

### 1. Launch Channels: Product Hunt + Hacker News + DevRel content
**Decision:** No paid ads. Launch on Product Hunt (Tuesday), HN (same week), publish 3 technical blog posts.
**Cause:** Our buyers are developers. They discover tools on PH/HN/blogs, not Google Ads.
**Trigger:** Competitor (Highlight.io) got 3000 signups from PH launch alone.
**Tension:** Organic is unpredictable vs. paid is measurable but wrong audience.
**Recorded by:** Maya

### 2. Open Source Core: Release `nebulactl` + correlation engine as OSS (MIT)
**Decision:** Open source the CLI and core correlation library. Keep UI, SSO, team features proprietary.
**Cause:** Builds trust with developers. "We can read the code" matters for self-hosted tools.
**Trigger:** ByteBank CTO: "We adopted because we could audit the correlation logic."
**Tension:** Competitors could copy vs. community contributions/distribution.
**Recorded by:** Raj

### 3. First Hire: Developer Advocate (not engineer)
**Decision:** Hire a DevRel as employee #4 before a 4th engineer.
**Cause:** Launch success depends on content/community. We have enough eng capacity for now.
**Trigger:** Maya's advisor: "You have product, you need distribution. DevRel > eng right now."
**Tension:** Technical credibility vs. marketing reach.
**Recorded by:** Maya

### 4. Pricing Freeze: Lock current tiers for 6 months
**Decision:** No pricing changes until September 2026. Free / Team ($29) / Pro ($49) / Enterprise (custom).
**Cause:** Early customers need predictability. Changing prices breaks trust.
**Trigger:** CloudNine legal asked for price lock in contract.
**Tension:** May leave revenue on table vs. customer trust.
**Recorded by:** Maya

### 5. Enterprise Features: Audit logs + RBAC in v1.1 (April)
**Decision:** Commit to audit logs and role-based access control in v1.1 (4 weeks post-launch).
**Cause:** Acme and ByteBank both need these for security reviews. Blockers for expansion.
**Trigger:** Acme security questionnaire: "No audit logs = no org-wide rollout."
**Tension:** Scope creep vs. enterprise revenue.
**Recorded by:** Priya

---

## Metrics Targets for Launch Week

| Metric | Target |
|--------|--------|
| Product Hunt upvotes | 500+ |
| GitHub stars (nebulactl) | 200+ |
| Signups (self-hosted trials) | 100+ |
| Design partner conversions | 3/3 paid |
| Inbound enterprise leads | 10+ |

---

## Risks

1. **ClickHouse operational burden** — Priya is sole expert. Bus factor = 1.
2. **SSO edge cases** — Okta/Azure AD/Google cover 90%, but custom SAML will break.
3. **Support load** — Self-hosted means customers hit infra issues we can't see.

---

## Action Items

- [ ] Maya: Draft PH launch post + 3 blog posts (target: Mar 15)
- [ ] Raj: Open source `nebulactl` repo prep (license, README, CI) (target: Mar 20)
- [ ] Priya: Document ClickHouse runbooks + backup/restore (target: Mar 15)
- [ ] Maya: Post DevRel job (target: Mar 5)
- [ ] All: Dry-run launch day runbook (target: Mar 26)

---

**Next Meeting:** Mar 15 — Launch dry run + content review