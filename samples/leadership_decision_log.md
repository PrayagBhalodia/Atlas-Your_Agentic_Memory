# Leadership Sync — Decision Log (Q2 2026)

Notes compiled by the Chief of Staff. Each entry captures what was decided and why.

---

## 2026-03-15 — Product & Platform review

We discussed the aging v1 public API. Maintenance is eating roughly a fifth of the
platform team's time, and telemetry shows under 5% of traffic still hits v1. After some
debate we **decided to sunset the v1 API by the end of Q3 2026**. The main hesitation was
that three enterprise customers are still integrated against v1, so we're committing to a
white-glove migration for them before the shutoff.

## 2026-04-02 — Finance & runway review

Burn came in higher than plan for March. To protect runway, we **decided to move the bulk
of our cloud workloads onto one-year reserved instances**, which finance estimates cuts
infrastructure spend by about 20%. The trade-off we accepted is reduced flexibility if we
need to change instance types mid-year. This was triggered by the March burn review.

## 2026-05-10 — Strategy offsite

Strong inbound interest from European prospects over the last quarter pushed a bigger
question: do we expand internationally now or stay focused? We **decided to enter the EU
market in H2 2026**, starting with a small go-to-market team of two. The tension here was
real — spreading focus versus capturing obvious demand — but the pipeline signal won out.

## 2026-06-01 — Pricing working session

Revisited the pricing model again. Top-of-funnel has been weak, and sales feels the entry
price is scaring off smaller teams. We **decided to introduce a free tier** to drive
signups, betting that enough of them convert upward. The clear risk we're taking on is
cannibalizing some existing paid conversions, which we'll watch closely for two quarters.

## 2026-06-20 — Security & compliance

We lost a promising enterprise deal in early June purely on compliance — they required a
SOC 2 report we don't have. So we **decided to pursue SOC 2 Type II certification**, with a
target of starting the audit window in Q4. Because the auditors will expect dedicated
security ownership, we also **decided to hire a security engineer**, reopening headcount we
had otherwise been holding tight after the bridge round.
