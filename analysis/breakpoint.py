"""Multivariate piecewise regression and block bootstrap diagnostics for HappiScope.

Pure functions with NO streamlit imports and NO @st.cache_data.
"""
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

from common import FACTOR_COLS, TARGET, complete_cases


def multivariate_piecewise(
    df: pd.DataFrame, tau_grid_points: int = 80, custom_tau: float = None
) -> Dict[str, Any]:
    """Fit multivariate continuous piecewise regression on Log GDP per capita

    controlling for the other five WHR drivers, with country-clustered standard errors.
    If custom_tau is provided, fits directly at custom_tau rather than searching.
    """
    d = complete_cases(df)
    controls = [c for c in FACTOR_COLS if c != "Log GDP per capita"]
    gdp_vals = d["Log GDP per capita"].values
    y_vals = d[TARGET].values
    
    if custom_tau is not None:
        best_tau = float(custom_tau)
    else:
        # 1. Grid search for optimal tau minimizing AIC
        q10, q90 = np.percentile(gdp_vals, 10), np.percentile(gdp_vals, 90)
        candidates = np.linspace(q10, q90, tau_grid_points)
        best_tau = float(candidates[0])
        best_aic = float("inf")
        
        for tau in candidates:
            hinge = np.maximum(0, gdp_vals - tau)
            X_mat = np.column_stack([np.ones_like(gdp_vals), gdp_vals, hinge, d[controls].values])
            m = sm.OLS(y_vals, X_mat).fit()
            if m.aic < best_aic:
                best_aic = float(m.aic)
                best_tau = float(tau)
            
    # 2. Fit final specification with country-clustered standard errors
    hinge_opt = np.maximum(0, gdp_vals - best_tau)
    X_final = pd.DataFrame({
        "const": 1.0,
        "Log GDP per capita": gdp_vals,
        "hinge": hinge_opt,
    }, index=d.index)
    for c in controls:
        X_final[c] = d[c].values
        
    m_cluster = sm.OLS(d[TARGET], X_final).fit(
        cov_type="cluster", cov_kwds={"groups": d["Country name"]}
    )
    
    b1 = float(m_cluster.params["Log GDP per capita"])
    b2 = float(m_cluster.params["hinge"])
    slope_above = b1 + b2
    
    cov_mat = m_cluster.cov_params()
    var_b1 = float(cov_mat.loc["Log GDP per capita", "Log GDP per capita"])
    var_b2 = float(cov_mat.loc["hinge", "hinge"])
    cov_b1_b2 = float(cov_mat.loc["Log GDP per capita", "hinge"])
    
    var_above = var_b1 + var_b2 + 2.0 * cov_b1_b2
    se_above = float(np.sqrt(max(0.0, var_above)))
    z_above = slope_above / se_above if se_above > 0 else 0.0
    p_above = float(2.0 * (1.0 - norm.cdf(abs(z_above))))
    
    n_below = int(np.sum(gdp_vals < best_tau))
    n_above = int(np.sum(gdp_vals >= best_tau))
    
    return {
        "model": m_cluster,
        "tau": best_tau,
        "n_below": n_below,
        "pct_below": float(n_below / len(d) * 100),
        "n_above": n_above,
        "pct_above": float(n_above / len(d) * 100),
        "aic": float(m_cluster.aic),
        "bic": float(m_cluster.bic),
        "rsquared": float(m_cluster.rsquared),
        "slope_below": b1,
        "se_below": float(np.sqrt(var_b1)),
        "p_below": float(m_cluster.pvalues["Log GDP per capita"]),
        "slope_change": b2,
        "se_change": float(np.sqrt(var_b2)),
        "p_change": float(m_cluster.pvalues["hinge"]),
        "slope_above": slope_above,
        "se_above": se_above,
        "p_above": p_above,
        "n_obs": len(d),
        "n_countries": int(d["Country name"].nunique()),
    }


def piecewise_threshold_sensitivity(
    df: pd.DataFrame, taus: list = None
) -> pd.DataFrame:
    """Fits multivariate continuous piecewise models across multiple candidate taus

    and returns a side-by-side comparison table.
    """
    if taus is None:
        taus = [7.648, 9.405]
        
    records = []
    for t in taus:
        fit_t = multivariate_piecewise(df, custom_tau=t)
        role = "Sample AIC Global Minimum" if abs(t - 7.648) < 0.01 else "Substantively Preferred (Bootstrap Median)"
        records.append({
            "Specification": f"Piecewise tau = {t:.3f}",
            "Role": role,
            "tau": fit_t["tau"],
            "N_below": fit_t["n_below"],
            "pct_below": fit_t["pct_below"],
            "N_above": fit_t["n_above"],
            "pct_above": fit_t["pct_above"],
            "slope_below_b1": fit_t["slope_below"],
            "se_below": fit_t["se_below"],
            "p_below": fit_t["p_below"],
            "slope_change_b2": fit_t["slope_change"],
            "se_change": fit_t["se_change"],
            "p_change": fit_t["p_change"],
            "slope_above": fit_t["slope_above"],
            "se_above": fit_t["se_above"],
            "p_above": fit_t["p_above"],
            "R2": fit_t["rsquared"],
            "AIC": fit_t["aic"],
            "BIC": fit_t["bic"],
        })
    return pd.DataFrame(records)


def block_bootstrap_tau(
    df: pd.DataFrame, n_reps: int = 1000, seed: int = 42, grid_points: int = 40
) -> Dict[str, Any]:
    """Resample WHOLE COUNTRIES with replacement to construct block bootstrap CI for tau."""
    d = complete_cases(df)
    controls = [c for c in FACTOR_COLS if c != "Log GDP per capita"]
    countries = np.array(sorted(d["Country name"].unique()))
    n_c = len(countries)
    
    rng = np.random.default_rng(seed)
    tau_samples = []
    
    country_groups = {c: group for c, group in d.groupby("Country name")}
    
    for _ in range(n_reps):
        sampled_c = rng.choice(countries, size=n_c, replace=True)
        boot_df = pd.concat([country_groups[c] for c in sampled_c], ignore_index=True)
        
        x = boot_df["Log GDP per capita"].values
        y = boot_df[TARGET].values
        q10, q90 = np.percentile(x, 10), np.percentile(x, 90)
        candidates = np.linspace(q10, q90, grid_points)
        
        b_tau = float(candidates[0])
        b_aic = float("inf")
        for tau in candidates:
            hinge = np.maximum(0, x - tau)
            X_mat = np.column_stack([np.ones_like(x), x, hinge, boot_df[controls].values])
            m = sm.OLS(y, X_mat).fit()
            if m.aic < b_aic:
                b_aic = float(m.aic)
                b_tau = float(tau)
        tau_samples.append(b_tau)
        
    tau_arr = np.array(tau_samples)
    ci_lower = float(np.percentile(tau_arr, 2.5))
    ci_median = float(np.percentile(tau_arr, 50.0))
    ci_upper = float(np.percentile(tau_arr, 97.5))
    
    return {
        "n_reps": n_reps,
        "tau_median": ci_median,
        "ci_lower_95": ci_lower,
        "ci_upper_95": ci_upper,
        "all_taus": tau_arr,
    }


def yearly_piecewise_significance(df: pd.DataFrame) -> Tuple[pd.DataFrame, int, int]:
    """Fit piecewise regressions separately for each year 2006-2023.

    Returns (yearly_df, n_significant, total_years).
    """
    d = complete_cases(df)
    records = []
    
    for yr in range(2006, 2024):
        d_yr = d[d["year"] == yr]
        if len(d_yr) < 30:
            continue
        x = d_yr["Log GDP per capita"].values
        y = d_yr[TARGET].values
        q10, q90 = np.percentile(x, 10), np.percentile(x, 90)
        candidates = np.linspace(q10, q90, 50)
        best_tau = float(candidates[0])
        best_aic = float("inf")
        
        for tau in candidates:
            hinge = np.maximum(0, x - tau)
            X_mat = np.column_stack([np.ones_like(x), x, hinge])
            m = sm.OLS(y, X_mat).fit()
            if m.aic < best_aic:
                best_aic = float(m.aic)
                best_tau = float(tau)
                
        hinge_opt = np.maximum(0, x - best_tau)
        X_mat = np.column_stack([np.ones_like(x), x, hinge_opt])
        m_fit = sm.OLS(y, X_mat).fit()
        
        p_b2 = float(m_fit.pvalues[2])
        is_sig = p_b2 < 0.05
        records.append({
            "year": int(yr),
            "N": len(d_yr),
            "tau": best_tau,
            "slope_change_beta2": float(m_fit.params[2]),
            "p_value_beta2": p_b2,
            "significant_at_05": is_sig,
        })
        
    res_df = pd.DataFrame(records)
    n_sig = int(res_df["significant_at_05"].sum())
    total_yrs = len(res_df)
    
    return res_df, n_sig, total_yrs

