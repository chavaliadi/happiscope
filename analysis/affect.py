"""Affect models evaluating evaluative vs emotional well-being (Kahneman & Deaton, 2010).

Pure functions with NO streamlit imports and NO @st.cache_data.
Implements fully-standardized regressions (both outcome and predictors z-scored)
for Life Ladder, Positive affect, and Negative affect.
"""
from typing import Dict, Any
import pandas as pd
import statsmodels.api as sm

from common import FACTOR_COLS


def run_affect_models(df: pd.DataFrame) -> Dict[str, Any]:
    """Fits fully standardized regressions of Life Ladder, Positive affect, and Negative affect

    on the six WHR factors, reporting raw SDs, rescaled betas, SEs, p-values, and R-squared.
    """
    outcomes = ["Life Ladder", "Positive affect", "Negative affect"]
    records = []
    models_dict = {}
    
    for target in outcomes:
        cols = FACTOR_COLS + [target]
        d = df[cols].dropna().copy()
        
        raw_mean = float(d[target].mean())
        raw_sd = float(d[target].std(ddof=0))
        
        # Standardize both target and all six factors
        z = pd.DataFrame(index=d.index)
        z[target] = (d[target] - raw_mean) / raw_sd
        for c in FACTOR_COLS:
            z[c] = (d[c] - d[c].mean()) / d[c].std(ddof=0)
            
        m = sm.OLS(z[target], sm.add_constant(z[FACTOR_COLS])).fit()
        models_dict[target] = m
        
        gdp_beta = float(m.params["Log GDP per capita"])
        gdp_se = float(m.bse["Log GDP per capita"])
        gdp_p = float(m.pvalues["Log GDP per capita"])
        
        records.append({
            "Outcome": target,
            "Raw Mean": raw_mean,
            "Raw SD": raw_sd,
            "N": len(d),
            "Fully_Standardized_Log_GDP_Beta": gdp_beta,
            "SE": gdp_se,
            "p_value": gdp_p,
            "R_squared": float(m.rsquared),
        })
        
    summary_df = pd.DataFrame(records)
    return {
        "summary_table": summary_df,
        "models": models_dict,
    }

