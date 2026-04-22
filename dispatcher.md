# dispatcher.md — Offline Artisan Lead Workflow
**Made in Rwanda Recommender · S2.T1.3**

---

## The Problem
A leatherworker in Nyamirambo has no smartphone, no internet, and no way to
know that 47 people searched "leather boots" on the platform this week.
Without a delivery mechanism, the recommender only helps online buyers —
not the artisan who needs the lead.

---

## Weekly Lead Workflow

### Actors

| Actor | Role |
|---|---|
| Recommender engine | Logs every query → matched local SKU |
| Cooperative agent | 1 agent per 20 artisans, has a smartphone |
| Artisan | Receives leads by SMS or voice call |

### Step-by-Step Flow

```
Monday–Sunday
    ↓
Recommender logs: query → SKU → artisan_id → district
    ↓
Every Friday 5PM — automated digest script runs:
    aggregate_leads.py
    → counts queries per artisan_id for the week
    → formats SMS per artisan
    ↓
Cooperative agent receives digest on WhatsApp
    ↓
Agent sends SMS to each artisan (or voice call if illiterate)
    ↓
Artisan prepares stock for the following week
```

### SMS Digest Format (English)

```
MADE IN RWANDA LEADS - Week 17
Artisan: Jean (ART-12)
Product: Leather Boots

Searches this week: 47
Top locations: Kigali (31), Musanze (16)

Prepare 5-8 pairs for pickup Friday.
Reply READY to confirm.
INKOMOKO: +250 788 123 456
```

**Word choice justification:**
- **"Searches this week: 47"** — concrete number motivates action; artisan sees real demand
- **"Prepare 5-8 pairs"** — tells artisan exactly what to do, no ambiguity
- **"Reply READY"** — single action, works on any phone, no smartphone needed
- **SMS not WhatsApp** — reaches non-smartphone users (feature phones, ~60% of Rwanda)

### SMS Digest Format (Kinyarwanda)

```
MADE IN RWANDA - Icyumweru 17
Umuhanzi: Jean (ART-12)
Igicuruzwa: Inkweto z'uruhu

Inzira z'iki cyumweru: 47
Tegura kopi 5-8 kuwa Gatanu.
Subiza GUTEGURA kugirango ubyemeze.
Telefoni: +250 788 123 456
```

---

## Pilot: 20 Artisans over 3 Months

### Setup

| Item | Detail |
|---|---|
| Artisans | 20 (4 per category: leather, basketry, apparel, jewellery, home-decor) |
| Districts | Kigali (8), Musanze (4), Huye (4), Bugesera (4) |
| Agent | 1 cooperative agent, part-time (10 hrs/week) |
| Platform | Existing recommender + weekly digest script |
| SMS Gateway | Africa's Talking API (~4 RWF per SMS) |

### Unit Economics

**Monthly costs:**

| Item | Cost (RWF) | Cost (USD) |
|---|---|---|
| SMS (20 artisans × 4 weeks × 4 RWF) | 320 | ~0.22 |
| Agent time (10 hrs/week × 4 weeks × 2,000 RWF/hr) | 80,000 | ~55 |
| Server (free tier Render/Railway) | 0 | 0 |
| **Total monthly cost** | **80,320** | **~55** |

**Per lead cost:**
- Estimated leads delivered per month: 480 (20 artisans × ~24 queries/week × 4 weeks)
- Cost per lead: 80,320 ÷ 480 = **~167 RWF (~$0.12)**

**Per artisan onboarding cost:**
- One-time: agent visit + photo catalog entry + SMS registration
- Estimated: **5,000 RWF (~$3.50)** per artisan
- 20 artisans total: **100,000 RWF (~$70)** one-time

**Break-even GMV:**

| Assumption | Value |
|---|---|
| Query → purchase conversion rate | 5% |
| Average order value | 25,000 RWF (~$17) |
| Platform fee | 10% |
| Monthly GMV needed to break even | 803,200 RWF (~$550) |
| Sales needed per month (all artisans) | ~32 sales |
| Sales needed per artisan per month | **~2 sales** |

> Break-even requires just 2 sales per artisan per month — a realistic and low bar.

---

## Handling Non-Smartphone / Illiterate Artisans

| Challenge | Solution |
|---|---|
| No smartphone | SMS to feature phone (works on any GSM device) |
| Illiterate | Agent reads SMS aloud on weekly visit or voice call |
| No reply capability | Agent confirms on artisan's behalf via WhatsApp |
| Power outages | SMS delivered when phone powers back on, no data needed |
| Multiple languages | SMS sent in Kinyarwanda for non-French/English speakers |
| No bank account | Cash payment on pickup via cooperative agent |

---

## 3-Month Pilot Timeline

| Month | Milestone | Success Metric |
|---|---|---|
| Month 1 | Onboard 20 artisans, run digest manually, collect baseline | 20 artisans registered, weekly SMS sent |
| Month 2 | Automate weekly SMS via Africa's Talking API, measure conversion | >20% of leads result in stock preparation |
| Month 3 | Measure GMV, refine fairness cap, present results to cooperative | Break-even GMV reached, 2+ sales/artisan |

---

## Key Numbers Summary

| Metric | Value |
|---|---|
| Queries aggregated per week | ~200 across platform |
| Leads delivered per artisan per week | ~10 |
| SMS cost per artisan per week | ~16 RWF (~$0.01) |
| Cost per lead | ~167 RWF (~$0.12) |
| Onboarding cost per artisan | 5,000 RWF (~$3.50) |
| Break-even sales per artisan | ~2 per month |
| Pilot duration | 3 months |
| Pilot artisans | 20 |

---

## Technical Appendix: aggregate_leads.py

```python
import pandas as pd
from datetime import datetime, timedelta

def generate_weekly_digest(click_log_path='click_log.csv', catalog_path='catalog.csv'):
    clicks = pd.read_csv(click_log_path)
    catalog = pd.read_csv(catalog_path)

    # Filter last 7 days
    clicks['timestamp'] = pd.to_datetime(clicks['timestamp'])
    last_week = datetime.now() - timedelta(days=7)
    weekly = clicks[clicks['timestamp'] >= last_week]

    # Count clicks per SKU
    sku_counts = weekly.groupby('sku').size().reset_index(name='searches')

    # Join with catalog to get artisan_id
    merged = sku_counts.merge(catalog[['sku', 'title', 'artisan_id', 'origin_district']], on='sku')

    # Group by artisan
    digest = merged.groupby(['artisan_id', 'origin_district']).agg(
        top_product=('title', 'first'),
        total_searches=('searches', 'sum')
    ).reset_index()

    # Format SMS per artisan
    week_num = datetime.now().isocalendar()[1]
    for _, row in digest.iterrows():
        sms = f"""MADE IN RWANDA LEADS - Week {week_num}
Artisan: {row['artisan_id']}
Product: {row['top_product']}
Searches this week: {row['total_searches']}
Prepare stock for pickup Friday.
Reply READY to confirm."""
        print(f"\n--- SMS for {row['artisan_id']} ({row['origin_district']}) ---")
        print(sms)

if __name__ == "__main__":
    generate_weekly_digest()
```
