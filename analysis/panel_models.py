"""Panel econometric models for HappiScope.

Pure functions with NO streamlit imports and NO @st.cache_data.
Provides pooled OLS, between estimator, two-way within fixed effects,
and the Mundlak specification.
"""
from typing import Dict, Tuple, Any
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.stattools import durbin_watson
from linearmodels.panel import PanelOLS

from common import FACTOR_COLS, TARGET, complete_cases


def pooled_ols(df: pd.DataFrame) -> Dict[str, Any]:
    """Current pooled OLS specification (unchanged)."""
    d = complete_cases(df)
    X = sm.add_constant(d[FACTOR_COLS])
    model = sm.OLS(d[TARGET], X).fit()
    dw = float(durbin_watson(model.resid))
    return {
        "model": model,
        "params": model.params,
        "bse": model.bse,
        "pvalues": model.pvalues,
        "rsquared": float(model.rsquared),
        "durbin_watson": dw,
        "n_obs": len(d),
        "n_countries": int(d["Country name"].nunique()) if "Country name" in d.columns else None,
    }


def between_estimator(df: pd.DataFrame) -> Dict[str, Any]:
    """Between estimator: country means of Y regressed on country means of X."""
    d = complete_cases(df)
    c_means = d.groupby("Country name")[[TARGET] + FACTOR_COLS].mean()
    X = sm.add_constant(c_means[FACTOR_COLS])
    model = sm.OLS(c_means[TARGET], X).fit()
    dw = float(durbin_watson(model.resid))
    return {
        "model": model,
        "params": model.params,
        "bse": model.bse,
        "pvalues": model.pvalues,
        "rsquared": float(model.rsquared),
        "durbin_watson": dw,
        "n_obs": len(c_means),
        "n_countries": len(c_means),
    }


def within_fe(df: pd.DataFrame) -> Dict[str, Any]:
    """Two-way fixed effects (Country + Year) using linearmodels.PanelOLS with country-clustered SEs."""
    d = complete_cases(df)
    p_data = d.set_index(["Country name", "year"])
    model = PanelOLS(
        p_data[TARGET],
        p_data[FACTOR_COLS],
        entity_effects=True,
        time_effects=True,
    ).fit(cov_type="clustered", cluster_entity=True)
    
    dw = float(durbin_watson(model.resids.values))
    return {
        "model": model,
        "params": model.params,
        "std_errors": model.std_errors,
        "pvalues": model.pvalues,
        "rsquared_within": float(model.rsquared_within),
        "durbin_watson": dw,
        "n_obs": int(model.nobs),
        "n_countries": int(model.entity_info.total),
    }


def mundlak(df: pd.DataFrame) -> Dict[str, Any]:
    """Mundlak specification: pooled model containing both within-country deviations

    (X_it - Xbar_i) and country means (Xbar_i) with a Wald test of equality.
    """
    d = complete_cases(df)
    means_df = d.groupby("Country name")[FACTOR_COLS].transform("mean")
    devs_df = d[FACTOR_COLS] - means_df
    
    mundlak_df = pd.DataFrame(index=d.index)
    for f in FACTOR_COLS:
        mundlak_df[f"{f}_within"] = devs_df[f]
        mundlak_df[f"{f}_between"] = means_df[f]
        
    X = sm.add_constant(mundlak_df)
    model = sm.OLS(d[TARGET], X).fit(cov_type="cluster", cov_kwds={"groups": d["Country name"]})
    
    # Wald test for equality: beta_within - beta_between == 0 across all 6 factors
    r_matrix = np.zeros((len(FACTOR_COLS), len(model.params)))
    param_names = list(model.params.index)
    for idx, f in enumerate(FACTOR_COLS):
        i_w = param_names.index(f"{f}_within")
        i_b = param_names.index(f"{f}_between")
        r_matrix[idx, i_w] = 1.0
        r_matrix[idx, i_b] = -1.0
        
    wald = model.wald_test(r_matrix)
    
    return {
        "model": model,
        "wald_statistic": float(wald.statistic.item() if hasattr(wald.statistic, "item") else wald.statistic),
        "wald_pvalue": float(wald.pvalue),
        "n_obs": len(d),
        "n_countries": int(d["Country name"].nunique()),
    }


def comparison_table(df: pd.DataFrame) -> Tuple[pd.DataFrame, float, Dict[str, float]]:
    """Side-by-side comparison table for each of the six drivers:

    pooled beta | between beta | within beta | clustered SE | p | N | n_countries
    Also returns (table, gdp_ratio, dw_dict).
    """
    pool_res = pooled_ols(df)
    betw_res = between_estimator(df)
    with_res = within_fe(df)
    
    rows = []
    for f in FACTOR_COLS:
        rows.append({
            "Driver": f,
            "pooled beta": float(pool_res["params"][f]),
            "between beta": float(betw_res["params"][f]),
            "within beta": float(with_res["params"][f]),
            "clustered SE": float(with_res["std_errors"][f]),
            "p": float(with_res["pvalues"][f]),
            "N": with_res["n_obs"],
            "n_countries": with_res["n_countries"],
        })
        
    comp_df = pd.DataFrame(rows)
    
    b_between_gdp = float(betw_res["params"]["Log GDP per capita"])
    b_within_gdp = float(with_res["params"]["Log GDP per capita"])
    gdp_ratio = b_between_gdp / b_within_gdp
    
    dw_dict = {
        "Pooled OLS": pool_res["durbin_watson"],
        "Between Estimator": betw_res["durbin_watson"],
        "Within FE": with_res["durbin_watson"],
    }
    
    return comp_df, gdp_ratio, dw_dict

