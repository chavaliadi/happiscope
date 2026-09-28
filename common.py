"""Shared data loading and model helpers for HappiScope.

Everyone's pages (Adithya, Ananya, Peer) should import from here so we all
use the SAME dataset and the SAME column names.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"

TARGET = "Life Ladder"  # the happiness score

# column name in the dataset -> short label we show on charts
FACTORS = {
    "Log GDP per capita": "GDP per capita (log)",
    "Social support": "Social support",
    "Healthy life expectancy at birth": "Healthy life expectancy",
    "Freedom to make life choices": "Freedom",
    "Generosity": "Generosity",
    "Perceptions of corruption": "Perceived corruption",
}
FACTOR_COLS = list(FACTORS)

MIN_COMPLETE_YEAR = 30   # a single-year regression needs at least this many complete countries
MIN_REGION_OBS = 60      # a regional regression needs at least this many country-year rows


# ---------------------------------------------------------------- data
@st.cache_data
def load_data() -> pd.DataFrame:
    """Master dataset + region + iso3 code for every country."""
    df = pd.read_csv(DATA_DIR / "happiscope_master.csv")
    reg = pd.read_csv(DATA_DIR / "country_region.csv")
    df = df.merge(reg, left_on="Country name", right_on="country", how="left").drop(columns="country")
    return df


@st.cache_data
def load_importance() -> pd.DataFrame:
    """Standardized-OLS vs Random-Forest permutation importance (from the notebook)."""
    return pd.read_csv(DATA_DIR / "importance_comparison.csv")


def complete_cases(df: pd.DataFrame) -> pd.DataFrame:
    """Rows with no missing value in the target or any of the six factors."""
    return df[FACTOR_COLS + [TARGET]].dropna()


# ---------------------------------------------------------------- models
def _ols(d: pd.DataFrame):
    return sm.OLS(d[TARGET], sm.add_constant(d[FACTOR_COLS])).fit()


def _standardize(d: pd.DataFrame) -> pd.DataFrame:
    z = d.copy()
    z[FACTOR_COLS] = (d[FACTOR_COLS] - d[FACTOR_COLS].mean()) / d[FACTOR_COLS].std(ddof=0)
    return z


def standardized_coefs(d: pd.DataFrame) -> pd.Series:
    """OLS on z-scored factors -> coefficients that can be compared fairly across factors."""
    return _ols(_standardize(d)).params[FACTOR_COLS]


@st.cache_data
def global_model(df: pd.DataFrame):
    d = complete_cases(df)
    m = _ols(d)
    table = pd.DataFrame({"coefficient": m.params, "p_value": m.pvalues})
    return table, float(m.rsquared), len(d)


@st.cache_data
def global_standardized(df: pd.DataFrame) -> pd.Series:
    return standardized_coefs(complete_cases(df))


@st.cache_data
def yearly_coefs(df: pd.DataFrame) -> pd.DataFrame:
    """One regression per year (raw coefficients). Years with too few complete rows are skipped."""
    rows = []
    for yr in sorted(df["year"].unique()):
        d = complete_cases(df[df["year"] == yr])
        if len(d) < MIN_COMPLETE_YEAR:
            continue
        m = _ols(d)
        rows.append({"year": int(yr), "n": len(d), "r_squared": m.rsquared, **m.params[FACTOR_COLS].to_dict()})
    return pd.DataFrame(rows).set_index("year")


@st.cache_data
def pooled_period(df: pd.DataFrame, start: int, end: int):
    """Pool all years in [start, end] into one regression. Returns (raw, standardized, r2, n)."""
    d = complete_cases(df[(df["year"] >= start) & (df["year"] <= end)])
    if len(d) < MIN_COMPLETE_YEAR:
        return None
    m = _ols(d)
    return m.params[FACTOR_COLS], standardized_coefs(d), float(m.rsquared), len(d)


@st.cache_data
def region_results(df: pd.DataFrame):
    """Standardized coefficients + R2 per region. Returns (table, excluded_regions)."""
    rows, excluded = [], []
    for region, g in df.groupby("region"):
        d = complete_cases(g)
        if len(d) < MIN_REGION_OBS:
            excluded.append((region, len(d)))
            continue
        m = _ols(d)
        rows.append({"region": region, "n_obs": len(d), "r_squared": m.rsquared,
                     **standardized_coefs(d).to_dict()})
    return pd.DataFrame(rows).set_index("region"), excluded
