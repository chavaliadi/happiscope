"""Leak-free validation models and baseline comparisons for HappiScope.

Pure functions with NO streamlit imports and NO @st.cache_data.
Implements GroupKFold (grouped by Country name) and Forward-Chaining Temporal Split
(Train <= 2018, Test 2019-2023), comparing OLS, Random Forest, and a Naive Persistence Baseline.
"""
from typing import Dict, Any
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from common import FACTOR_COLS, TARGET, complete_cases


def evaluate_leak_free_models(df: pd.DataFrame, n_splits: int = 5, seed: int = 42) -> Dict[str, Any]:
    """Evaluates OLS, RandomForest, and Naive Prior-Year baseline under leak-free protocols,

    including augmented models with lagged outcome for like-for-like comparison.
    """
    d = complete_cases(df).sort_values(["Country name", "year"]).copy()
    
    # Construct naive previous-year prediction (lag-1 within country)
    d["lag_target"] = d.groupby("Country name")[TARGET].shift(1)
    
    # ------------------------------------------------------------- 1. Forward-Chaining Temporal Split
    # To ensure strict like-for-like comparison, we restrict historical train & test to observations with available lag
    d_lag = d.dropna(subset=["lag_target"]).copy()
    
    train_mask = d_lag["year"] <= 2018
    test_mask = d_lag["year"] >= 2019
    
    d_train = d_lag[train_mask].copy()
    d_test = d_lag[test_mask].copy()
    
    features_base = FACTOR_COLS
    features_aug = FACTOR_COLS + ["lag_target"]
    
    # Base models (contemporaneous drivers only)
    ols_base = LinearRegression().fit(d_train[features_base], d_train[TARGET])
    rf_base = RandomForestRegressor(n_estimators=200, random_state=seed).fit(d_train[features_base], d_train[TARGET])
    
    p_ols_base = ols_base.predict(d_test[features_base])
    p_rf_base = rf_base.predict(d_test[features_base])
    
    # Naive baseline (persistence: predicts lagged outcome)
    p_naive = d_test["lag_target"].values
    
    # Augmented models (contemporaneous + lagged outcome)
    ols_aug = LinearRegression().fit(d_train[features_aug], d_train[TARGET])
    rf_aug = RandomForestRegressor(n_estimators=200, random_state=seed).fit(d_train[features_aug], d_train[TARGET])
    
    p_ols_aug = ols_aug.predict(d_test[features_aug])
    p_rf_aug = rf_aug.predict(d_test[features_aug])
    
    temporal_summary = pd.DataFrame([
        {
            "Protocol": "Temporal Split (2019-2023)",
            "Model": "Linear OLS (contemporaneous)",
            "Features": "6 WHR Drivers",
            "R2": float(r2_score(d_test[TARGET], p_ols_base)),
            "RMSE": float(np.sqrt(mean_squared_error(d_test[TARGET], p_ols_base))),
            "MAE": float(mean_absolute_error(d_test[TARGET], p_ols_base)),
            "Test_N": len(d_test),
        },
        {
            "Protocol": "Temporal Split (2019-2023)",
            "Model": "Random Forest (contemporaneous)",
            "Features": "6 WHR Drivers",
            "R2": float(r2_score(d_test[TARGET], p_rf_base)),
            "RMSE": float(np.sqrt(mean_squared_error(d_test[TARGET], p_rf_base))),
            "MAE": float(mean_absolute_error(d_test[TARGET], p_rf_base)),
            "Test_N": len(d_test),
        },
        {
            "Protocol": "Temporal Split (2019-2023)",
            "Model": "Naive Prior-Year Baseline (has access to lagged outcome)",
            "Features": "Lagged Life Ladder (Y_{i, t-1})",
            "R2": float(r2_score(d_test[TARGET], p_naive)),
            "RMSE": float(np.sqrt(mean_squared_error(d_test[TARGET], p_naive))),
            "MAE": float(mean_absolute_error(d_test[TARGET], p_naive)),
            "Test_N": len(d_test),
        },
        {
            "Protocol": "Temporal Split (2019-2023)",
            "Model": "Linear OLS (with lagged outcome)",
            "Features": "6 WHR Drivers + Lagged Life Ladder",
            "R2": float(r2_score(d_test[TARGET], p_ols_aug)),
            "RMSE": float(np.sqrt(mean_squared_error(d_test[TARGET], p_ols_aug))),
            "MAE": float(mean_absolute_error(d_test[TARGET], p_ols_aug)),
            "Test_N": len(d_test),
        },
        {
            "Protocol": "Temporal Split (2019-2023)",
            "Model": "Random Forest (with lagged outcome)",
            "Features": "6 WHR Drivers + Lagged Life Ladder",
            "R2": float(r2_score(d_test[TARGET], p_rf_aug)),
            "RMSE": float(np.sqrt(mean_squared_error(d_test[TARGET], p_rf_aug))),
            "MAE": float(mean_absolute_error(d_test[TARGET], p_rf_aug)),
            "Test_N": len(d_test),
        },
    ])
    
    # ------------------------------------------------------------- 2. GroupKFold (Cross-Country Generalization)
    gkf = GroupKFold(n_splits=n_splits)
    ols_r2s, ols_rmses, ols_maes = [], [], []
    rf_r2s, rf_rmses, rf_maes = [], [], []
    
    for train_idx, test_idx in gkf.split(d, groups=d["Country name"]):
        tr, te = d.iloc[train_idx], d.iloc[test_idx]
        
        ols_m = LinearRegression().fit(tr[FACTOR_COLS], tr[TARGET])
        rf_m = RandomForestRegressor(n_estimators=100, random_state=seed).fit(tr[FACTOR_COLS], tr[TARGET])
        
        p_ols = ols_m.predict(te[FACTOR_COLS])
        p_rf = rf_m.predict(te[FACTOR_COLS])
        
        ols_r2s.append(r2_score(te[TARGET], p_ols))
        ols_rmses.append(np.sqrt(mean_squared_error(te[TARGET], p_ols)))
        ols_maes.append(mean_absolute_error(te[TARGET], p_ols))
        
        rf_r2s.append(r2_score(te[TARGET], p_rf))
        rf_rmses.append(np.sqrt(mean_squared_error(te[TARGET], p_rf)))
        rf_maes.append(mean_absolute_error(te[TARGET], p_rf))
        
    group_summary = pd.DataFrame([
        {
            "Protocol": f"GroupKFold ({n_splits}-fold Country)",
            "Model": "Linear OLS",
            "Features": "6 WHR Drivers",
            "R2": float(np.mean(ols_r2s)),
            "RMSE": float(np.mean(ols_rmses)),
            "MAE": float(np.mean(ols_maes)),
            "Test_N": len(d),
        },
        {
            "Protocol": f"GroupKFold ({n_splits}-fold Country)",
            "Model": "Random Forest",
            "Features": "6 WHR Drivers",
            "R2": float(np.mean(rf_r2s)),
            "RMSE": float(np.mean(rf_rmses)),
            "MAE": float(np.mean(rf_maes)),
            "Test_N": len(d),
        },
    ])
    
    comparison_summary = pd.concat([temporal_summary, group_summary], ignore_index=True)
    
    return {
        "summary_table": comparison_summary,
        "old_leaking_rf_r2": 0.8663,
        "temporal_rf_r2": float(r2_score(d_test[TARGET], p_rf_base)),
        "temporal_naive_r2": float(r2_score(d_test[TARGET], p_naive)),
        "temporal_ols_aug_r2": float(r2_score(d_test[TARGET], p_ols_aug)),
        "temporal_rf_aug_r2": float(r2_score(d_test[TARGET], p_rf_aug)),
        "groupkfold_rf_r2": float(np.mean(rf_r2s)),
        "groupkfold_ols_r2": float(np.mean(ols_r2s)),
    }

