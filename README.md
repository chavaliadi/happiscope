# HappiScope

Interactive World Happiness Report explorer (Science of Happiness midsem project).

## Run it on your laptop (optional check)
```
pip install -r requirements.txt
streamlit run app.py
```

## Put it online (free, gives a shareable link)
1. Create a new GitHub repo and upload **everything in this folder** (keep the folders; `app.py` must be at the top level).
2. Go to https://share.streamlit.io, sign in with GitHub, click **New app**.
3. Pick your repo, set **Main file path** to `app.py`, click **Deploy**.

## How teammates add their page (Day 5)
1. Create `views/your_page.py` with a `render()` function (see `views/factor_breakdown.py` for an example).
2. In `app.py`, replace the placeholder line for your page with `your_page.render`.
3. Load data with `from common import load_data` so everyone uses the same dataset and column names.

## Files
- `app.py` - navigation + page list
- `common.py` - shared data loading and model helpers
- `views/` - one file per page
- `data/happiscope_master.csv` - WHR panel (165 countries, 2005-2023), UTF-8
- `data/country_region.csv` - continent + ISO code per country
- `data/importance_comparison.csv` - standardized OLS vs Random Forest permutation importance
