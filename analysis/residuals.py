"""Residual and country effect analysis for HappiScope.

Pure functions with NO streamlit imports and NO @st.cache_data.
Analyzes persistent country intercepts and idiosyncratic residuals from the two-way fixed effects specification.
"""
from typing import Dict, Any
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from linearmodels.panel import PanelOLS

from common import FACTOR_COLS, TARGET, complete_cases


def analyze_residuals(df: pd.DataFrame) -> Dict[str, Any]:
    """Computes country fixed effects, regional ANOVA, regional CIs, lag-1 persistence,

    and top 15 over- and under-performing nations.
    """
    d = complete_cases(df).copy()
    
    # 1. Fit Two-Way Fixed Effects model
    p_data = d.set_index(["Country name", "year"])
    m_fe = PanelOLS(
        p_data[TARGET],
        p_data[FACTOR_COLS],
        entity_effects=True,
        time_effects=True,
    ).fit(cov_type="clustered", cluster_entity=True)
    
    # Extract country fixed effects (unobserved baseline well-being)
    d["country_effect"] = m_fe.estimated_effects.values
    d["resid_within"] = m_fe.resids.values
    
    # Per-country summary
    country_summary = d.groupby("Country name").agg({
        "country_effect": "mean",
        "region": "first",
        TARGET: "count",
    }).rename(columns={TARGET: "obs_count"}).sort_values("country_effect", ascending=False)
    
    top_15_over = country_summary.head(15).copy()
    top_15_under = country_summary.tail(15).sort_values("country_effect").copy()
    
    # 2. Regional Systematicity (ANOVA of country effects across continental regions)
    anova_m = ols("country_effect ~ C(region)", data=country_summary).fit()
    anova_tab = sm.stats.anova_lm(anova_m, typ=2)
    anova_f = float(anova_tab.loc["C(region)", "F"])
    anova_p = float(anova_tab.loc["C(region)", "PR(>F)"])
    
    # Regional Means with 95% Confidence Intervals
    reg_means = country_summary.groupby("region")["country_effect"].agg(["mean", "std", "count"])
    reg_means["ci95_margin"] = 1.96 * reg_means["std"] / np.sqrt(reg_means["count"])
    reg_means["ci_lower"] = reg_means["mean"] - reg_means["ci95_margin"]
    reg_means["ci_upper"] = reg_means["mean"] + reg_means["ci95_margin"]
    reg_means = reg_means[["mean", "ci95_margin", "ci_lower", "ci_upper", "count"]].reset_index()
    
    # 3. Persistence over time: Lag-1 Autocorrelation of residuals within country
    d_sorted = d.sort_values(["Country name", "year"])
    d_sorted["lag_resid"] = d_sorted.groupby("Country name")["resid_within"].shift(1)
    valid_pairs = d_sorted.dropna(subset=["resid_within", "lag_resid"])
    persistence_corr = float(np.corrcoef(valid_pairs["resid_within"], valid_pairs["lag_resid"])[0, 1])
    
    return {
        "top_15_overperformers": top_15_over,
        "top_15_underperformers": top_15_under,
        "regional_anova_f": anova_f,
        "regional_anova_p": anova_p,
        "regional_table": reg_means,
        "persistence_autocorr": persistence_corr,
        "n_countries": len(country_summary),
        "n_obs": len(d),
    }
