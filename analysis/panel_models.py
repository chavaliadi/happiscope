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


def bivariate_panel_models(df: pd.DataFrame) -> Dict[str, Any]:
    """Bivariate panel models of Life Ladder on Log GDP per capita ONLY (no controls).

    Returns:
      1. Pooled OLS
      2. Between Estimator (country means)
      3. Within Estimator (Country fixed effects only, country-clustered SE)
      4. Within Estimator (Country + Year fixed effects, country-clustered SE)
      Easterlin Ratio: Between beta / Within (Country-FE only) beta
      Secular-Trend Ratio: Between beta / Within (Two-Way FE) beta
    """
    d = complete_cases(df)
    
    # 1. Pooled OLS
    X_pooled = sm.add_constant(d["Log GDP per capita"])
    m_pooled = sm.OLS(d[TARGET], X_pooled).fit()
    
    # 2. Between Estimator
    c_means = d.groupby("Country name")[[TARGET, "Log GDP per capita"]].mean()
    X_between = sm.add_constant(c_means["Log GDP per capita"])
    m_between = sm.OLS(c_means[TARGET], X_between).fit()
    
    # 3. Within: Country FE only
    p_data = d.set_index(["Country name", "year"])
    m_within_c = PanelOLS(
        p_data[TARGET],
        p_data[["Log GDP per capita"]],
        entity_effects=True,
        time_effects=False,
    ).fit(cov_type="clustered", cluster_entity=True)
    
    # 4. Within: Country + Year FE
    m_within_cy = PanelOLS(
        p_data[TARGET],
        p_data[["Log GDP per capita"]],
        entity_effects=True,
        time_effects=True,
    ).fit(cov_type="clustered", cluster_entity=True)
    
    beta_pooled = float(m_pooled.params["Log GDP per capita"])
    beta_between = float(m_between.params["Log GDP per capita"])
    beta_within_c = float(m_within_c.params["Log GDP per capita"])
    beta_within_cy = float(m_within_cy.params["Log GDP per capita"])
    
    easterlin_ratio = beta_between / beta_within_c
    secular_ratio = beta_between / beta_within_cy
    
    table_df = pd.DataFrame([
        {
            "Estimator": "1. Pooled OLS",
            "Specification": "Bivariate (Log GDP only)",
            "Beta": beta_pooled,
            "SE": float(m_pooled.bse["Log GDP per capita"]),
            "p_value": float(m_pooled.pvalues["Log GDP per capita"]),
            "R2": float(m_pooled.rsquared),
            "N_obs": len(d),
            "N_countries": int(d["Country name"].nunique()),
        },
        {
            "Estimator": "2. Between Estimator",
            "Specification": "Country means (cross-sectional total)",
            "Beta": beta_between,
            "SE": float(m_between.bse["Log GDP per capita"]),
            "p_value": float(m_between.pvalues["Log GDP per capita"]),
            "R2": float(m_between.rsquared),
            "N_obs": len(c_means),
            "N_countries": len(c_means),
        },
        {
            "Estimator": "3. Within FE (Country only)",
            "Specification": "Country FE, clustered SE (Easterlin test)",
            "Beta": beta_within_c,
            "SE": float(m_within_c.std_errors["Log GDP per capita"]),
            "p_value": float(m_within_c.pvalues["Log GDP per capita"]),
            "R2": float(m_within_c.rsquared_within),
            "N_obs": int(m_within_c.nobs),
            "N_countries": int(m_within_c.entity_info.total),
        },
        {
            "Estimator": "4. Within FE (Country + Year)",
            "Specification": "Two-way FE (removes secular global trend)",
            "Beta": beta_within_cy,
            "SE": float(m_within_cy.std_errors["Log GDP per capita"]),
            "p_value": float(m_within_cy.pvalues["Log GDP per capita"]),
            "R2": float(m_within_cy.rsquared_within),
            "N_obs": int(m_within_cy.nobs),
            "N_countries": int(m_within_cy.entity_info.total),
        },
    ])
    
    return {
        "summary_table": table_df,
        "beta_pooled": beta_pooled,
        "beta_between": beta_between,
        "beta_within_country_only": beta_within_c,
        "beta_within_twoway": beta_within_cy,
        "easterlin_ratio": easterlin_ratio,
        "secular_trend_ratio": secular_ratio,
        "model_pooled": m_pooled,
        "model_between": m_between,
        "model_within_country": m_within_c,
        "model_within_twoway": m_within_cy,
    }


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

