"""Relative income and social comparison analysis for HappiScope.

Pure functions with NO streamlit imports and NO @st.cache_data.
Operationalizes Richard Easterlin's proposed social comparison mechanism by testing
own national income (X) against contemporaneous regional average income (M).
"""
from typing import Dict, Any
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from linearmodels.panel import PanelOLS

from common import FACTOR_COLS, TARGET, complete_cases


def evaluate_relative_income(df: pd.DataFrame) -> Dict[str, Any]:
    """Tests own Log GDP (X) and regional mean Log GDP (M) entered directly as separate regressors

    under both Pooled OLS (clustered SEs) and Two-Way Fixed Effects.
    """
    d = complete_cases(df).copy()
    
    # Construct M = regional mean Log GDP that year
    d["regional_mean_gdp"] = d.groupby(["region", "year"])["Log GDP per capita"].transform("mean")
    
    controls = [c for c in FACTOR_COLS if c != "Log GDP per capita"]
    regressors = ["Log GDP per capita", "regional_mean_gdp"] + controls
    
    # 1. Pooled OLS with Country-Clustered SEs
    X_mat = sm.add_constant(d[regressors])
    m_pooled = sm.OLS(d[TARGET], X_mat).fit(
        cov_type="cluster", cov_kwds={"groups": d["Country name"]}
    )
    
    # 2. VIF Check
    vif_records = []
    for i, col in enumerate(X_mat.columns):
        if col == "const":
            continue
        vif_records.append({
            "Variable": col,
            "VIF": float(variance_inflation_factor(X_mat.values, i)),
        })
    vif_df = pd.DataFrame(vif_records)
    
    # 3. Two-Way Fixed Effects (Country + Year)
    p_data = d.set_index(["Country name", "year"])
    m_fe = PanelOLS(
        p_data[TARGET],
        p_data[regressors],
        entity_effects=True,
        time_effects=True,
    ).fit(cov_type="clustered", cluster_entity=True)
    
    # Extraction of coefficients
    pooled_x_b = float(m_pooled.params["Log GDP per capita"])
    pooled_x_p = float(m_pooled.pvalues["Log GDP per capita"])
    pooled_m_b = float(m_pooled.params["regional_mean_gdp"])
    pooled_m_p = float(m_pooled.pvalues["regional_mean_gdp"])
    
    fe_x_b = float(m_fe.params["Log GDP per capita"])
    fe_x_p = float(m_fe.pvalues["Log GDP per capita"])
    fe_m_b = float(m_fe.params["regional_mean_gdp"])
    fe_m_p = float(m_fe.pvalues["regional_mean_gdp"])
    
    # Mechanism interpretation
    # Negative => social comparison; Positive => regional spillover
    pooled_mech = "Regional Spillovers (Positive)" if pooled_m_b > 0 else "Social Comparison (Negative)"
    fe_mech = "Regional Spillovers (Positive)" if fe_m_b > 0 else "Social Comparison (Negative)"
    
    summary_df = pd.DataFrame([
        {
            "Specification": "Pooled OLS (Country-Clustered SEs)",
            "Own_Log_GDP_Beta": pooled_x_b,
            "Own_Log_GDP_p": pooled_x_p,
            "Regional_Mean_GDP_Beta": pooled_m_b,
            "Regional_Mean_GDP_p": pooled_m_p,
            "Direction": pooled_mech,
            "Significant_at_05": pooled_m_p < 0.05,
        },
        {
            "Specification": "Two-Way Fixed Effects (Clustered SEs)",
            "Own_Log_GDP_Beta": fe_x_b,
            "Own_Log_GDP_p": fe_x_p,
            "Regional_Mean_GDP_Beta": fe_m_b,
            "Regional_Mean_GDP_p": fe_m_p,
            "Direction": fe_mech,
            "Significant_at_05": fe_m_p < 0.05,
        },
    ])
    
    return {
        "summary_table": summary_df,
        "vif_table": vif_df,
        "pooled_model": m_pooled,
        "fe_model": m_fe,
    }

