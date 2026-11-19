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


def analyze_residuals(df: pd.DataFrame, min_obs: int = 8) -> Dict[str, Any]:
    """Computes country fixed effects, re-centers them to mean zero across countries,

    filters out countries with fewer than min_obs observations (dropping unstable estimates),
    performs regional ANOVA, regional 95% CIs, lag-1 residual persistence,
    and returns top 15 over- and under-performing nations.
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
    
    # Extract raw country fixed effects
    raw_effects = m_fe.estimated_effects["estimated_effects"].groupby("Country name").first()
    obs_counts = d["Country name"].value_counts()
    reg_map = d.groupby("Country name")["region"].first()
    
    country_df = pd.DataFrame({
        "raw_country_effect": raw_effects,
        "obs_count": obs_counts,
        "region": reg_map,
    })
    
    total_countries = len(country_df)
    # Filter out countries with < min_obs
    filtered_df = country_df[country_df["obs_count"] >= min_obs].copy()
    excluded_countries = country_df[country_df["obs_count"] < min_obs].index.tolist()
    n_excluded = len(excluded_countries)
    
    # Re-center country effects to mean zero across remaining countries
    mean_raw = filtered_df["raw_country_effect"].mean()
    filtered_df["country_effect"] = filtered_df["raw_country_effect"] - mean_raw
    
    # Sort and pick top 15 over- and under-performers
    top_15_over = filtered_df.sort_values("country_effect", ascending=False).head(15).copy()
    top_15_under = filtered_df.sort_values("country_effect", ascending=True).head(15).copy()
    
    # 2. Regional Systematicity (ANOVA of country effects across continental regions)
    # Compare ANOVA on raw vs centered
    anova_raw = ols("raw_country_effect ~ C(region)", data=filtered_df).fit()
    tab_raw = sm.stats.anova_lm(anova_raw, typ=2)
    f_raw = float(tab_raw.loc["C(region)", "F"])
    p_raw = float(tab_raw.loc["C(region)", "PR(>F)"])
    
    anova_cent = ols("country_effect ~ C(region)", data=filtered_df).fit()
    tab_cent = sm.stats.anova_lm(anova_cent, typ=2)
    anova_f = float(tab_cent.loc["C(region)", "F"])
    anova_p = float(tab_cent.loc["C(region)", "PR(>F)"])
    
    # Regional Means with 95% Confidence Intervals
    reg_means = filtered_df.groupby("region")["country_effect"].agg(["mean", "std", "count"])
    reg_means["ci95_margin"] = 1.96 * reg_means["std"] / np.sqrt(reg_means["count"])
    reg_means["ci_lower"] = reg_means["mean"] - reg_means["ci95_margin"]
    reg_means["ci_upper"] = reg_means["mean"] + reg_means["ci95_margin"]
    reg_means = reg_means[["mean", "ci95_margin", "ci_lower", "ci_upper", "count"]].reset_index()
    
    # 3. Persistence over time: Lag-1 Autocorrelation of residuals within country
    d["resid_within"] = m_fe.resids.values
    d_sorted = d.sort_values(["Country name", "year"])
    d_sorted["lag_resid"] = d_sorted.groupby("Country name")["resid_within"].shift(1)
    valid_pairs = d_sorted.dropna(subset=["resid_within", "lag_resid"])
    persistence_corr = float(np.corrcoef(valid_pairs["resid_within"], valid_pairs["lag_resid"])[0, 1])
    
    return {
        "top_15_overperformers": top_15_over,
        "top_15_underperformers": top_15_under,
        "regional_anova_f": anova_f,
        "regional_anova_p": anova_p,
        "regional_anova_f_raw": f_raw,
        "regional_anova_p_raw": p_raw,
        "regional_table": reg_means,
        "persistence_autocorr": persistence_corr,
        "total_countries": total_countries,
        "n_countries": len(filtered_df),
        "n_excluded_countries": n_excluded,
        "excluded_countries": sorted(excluded_countries),
        "n_obs": len(d),
    }
