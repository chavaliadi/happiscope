"""Affect models evaluating evaluative vs emotional well-being (Kahneman & Deaton, 2010).

Pure functions with NO streamlit imports and NO @st.cache_data.
Implements fully-standardized regressions (both outcome and predictors z-scored)
for Life Ladder, Positive affect, and Negative affect in both bivariate (unconditional)
and multivariate (conditional on the other five WHR drivers) specifications.
"""
from typing import Dict, Any
import pandas as pd
import statsmodels.api as sm

from common import FACTOR_COLS


def run_affect_models(df: pd.DataFrame) -> Dict[str, Any]:
    """Fits standardized regressions of Life Ladder, Positive affect, and Negative affect

    on Log GDP per capita both unconditionally (bivariate) and conditionally (multivariate,
    controlling for social support, health, freedom, generosity, and corruption).
    """
    outcomes = ["Life Ladder", "Positive affect", "Negative affect"]
    records = []
    models_dict = {}
    
    for target in outcomes:
        cols = FACTOR_COLS + [target]
        d = df[cols].dropna().copy()
        
        raw_mean = float(d[target].mean())
        raw_sd = float(d[target].std(ddof=0))
        
        # Standardize both target and all six factors on the complete-case estimation sample
        z = pd.DataFrame(index=d.index)
        z[target] = (d[target] - raw_mean) / raw_sd
        for c in FACTOR_COLS:
            z[c] = (d[c] - d[c].mean()) / d[c].std(ddof=0)
            
        # Multivariate conditional model
        m_cond = sm.OLS(z[target], sm.add_constant(z[FACTOR_COLS])).fit()
        models_dict[f"{target}_conditional"] = m_cond
        
        # Bivariate model on same estimation sample
        m_bi = sm.OLS(z[target], sm.add_constant(z["Log GDP per capita"])).fit()
        models_dict[f"{target}_bivariate"] = m_bi
        
        # Also pairwise bivariate on all available rows for target + Log GDP
        d_pair = df[["Log GDP per capita", target]].dropna()
        z_pair = pd.DataFrame(index=d_pair.index)
        z_pair[target] = (d_pair[target] - d_pair[target].mean()) / d_pair[target].std(ddof=0)
        z_pair["Log GDP per capita"] = (d_pair["Log GDP per capita"] - d_pair["Log GDP per capita"].mean()) / d_pair["Log GDP per capita"].std(ddof=0)
        m_bi_pair = sm.OLS(z_pair[target], sm.add_constant(z_pair["Log GDP per capita"])).fit()
        
        records.append({
            "Outcome": target,
            "Raw Mean": raw_mean,
            "Raw SD": raw_sd,
            "N_Pairwise": len(d_pair),
            "Bivariate_Beta_Pairwise": float(m_bi_pair.params["Log GDP per capita"]),
            "Bivariate_SE_Pairwise": float(m_bi_pair.bse["Log GDP per capita"]),
            "Bivariate_p_Pairwise": float(m_bi_pair.pvalues["Log GDP per capita"]),
            "Bivariate_R2_Pairwise": float(m_bi_pair.rsquared),
            "N": len(d),
            "Bivariate_Beta": float(m_bi.params["Log GDP per capita"]),
            "Bivariate_SE": float(m_bi.bse["Log GDP per capita"]),
            "Bivariate_p": float(m_bi.pvalues["Log GDP per capita"]),
            "Bivariate_R2": float(m_bi.rsquared),
            "Fully_Standardized_Log_GDP_Beta": float(m_cond.params["Log GDP per capita"]),
            "SE": float(m_cond.bse["Log GDP per capita"]),
            "p_value": float(m_cond.pvalues["Log GDP per capita"]),
            "R_squared": float(m_cond.rsquared),
        })
        
    summary_df = pd.DataFrame(records)
    return {
        "summary_table": summary_df,
        "models": models_dict,
    }


