## About

This project is a content-based product recommender built for the AIMS KTT Hackathon 
(S2.T1.3 — 'Made in Rwanda' Content Recommender).

Local Rwandan artisans lose sales to global e-commerce algorithms that favour 
high-volume international sellers. This recommender flips that dynamic — it ranks 
local 'Made in Rwanda' products first, handles multilingual queries (English, French, 
Kinyarwanda), corrects misspellings, and delivers weekly lead summaries to artisans 
who have no smartphone via SMS.

### Key Features
- Hybrid TF-IDF index (word + character n-grams) for typo robustness
- FR/Kinyarwanda → English query translation
- Local-boost: all Rwandan products scored higher, niche districts get an extra 10%
- Fairness cap: no single artisan occupies more than 15% of top recommendations
- Fallback curation when no strong local match exists
- CLI interface: `python Recommender.py --q "leather boots"`
- Offline artisan workflow: weekly SMS digest delivered via cooperative agent

### Performance
| Metric | Score |
|---|---|
| NDCG@5 | 0.93 |
| % queries with target in top 5 | 100% |
| Avg rank of target product | 1.3 |
| Query languages supported | English, French, Kinyarwanda |

### Quick Start
```bash
git clone https://github.com/gabrielntwari/AIMS-KTT-Hackathon-Made-in-Rwanda-Content-Recommender
cd made-in-rwanda-recommender
pip install -r requirements.txt
python generator.py
python Recommender.py --q "leather boots"
python Recommender.py --q "inkweto"
```