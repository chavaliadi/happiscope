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
    """Evaluates OLS, RandomForest, and Naive Prior-Year baseline under leak-free protocols."""
    d = complete_cases(df).sort_values(["Country name", "year"]).copy()
    
    # Construct naive previous-year prediction (lag-1 within country)
    d["naive_pred"] = d.groupby("Country name")[TARGET].shift(1)
    
    # ------------------------------------------------------------- 1. Forward-Chaining Temporal Split
    train_mask = d["year"] <= 2018
    test_mask = d["year"] >= 2019
    
    d_train = d[train_mask].copy()
    d_test = d[test_mask].copy()
    
    # Models fit on historical data
    ols_temp = LinearRegression().fit(d_train[FACTOR_COLS], d_train[TARGET])
    rf_temp = RandomForestRegressor(n_estimators=200, random_state=seed).fit(d_train[FACTOR_COLS], d_train[TARGET])
    
    # Full test set predictions
    p_ols_test = ols_temp.predict(d_test[FACTOR_COLS])
    p_rf_test = rf_temp.predict(d_test[FACTOR_COLS])
    
    # Naive baseline evaluation on available observations
    test_valid_naive = d_test.dropna(subset=["naive_pred"])
    p_ols_matched = ols_temp.predict(test_valid_naive[FACTOR_COLS])
    p_rf_matched = rf_temp.predict(test_valid_naive[FACTOR_COLS])
    
    temporal_summary = pd.DataFrame([
        {
            "Protocol": "Temporal Split (2019-2023)",
            "Model": "Linear OLS",
            "R2": float(r2_score(d_test[TARGET], p_ols_test)),
            "RMSE": float(np.sqrt(mean_squared_error(d_test[TARGET], p_ols_test))),
            "MAE": float(mean_absolute_error(d_test[TARGET], p_ols_test)),
            "Test_N": len(d_test),
        },
        {
            "Protocol": "Temporal Split (2019-2023)",
            "Model": "Random Forest",
            "R2": float(r2_score(d_test[TARGET], p_rf_test)),
            "RMSE": float(np.sqrt(mean_squared_error(d_test[TARGET], p_rf_test))),
            "MAE": float(mean_absolute_error(d_test[TARGET], p_rf_test)),
            "Test_N": len(d_test),
        },
        {
            "Protocol": "Temporal Split (Matched N)",
            "Model": "Naive Prior-Year Baseline",
            "R2": float(r2_score(test_valid_naive[TARGET], test_valid_naive["naive_pred"])),
            "RMSE": float(np.sqrt(mean_squared_error(test_valid_naive[TARGET], test_valid_naive["naive_pred"]))),
            "MAE": float(mean_absolute_error(test_valid_naive[TARGET], test_valid_naive["naive_pred"])),
            "Test_N": len(test_valid_naive),
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
            "R2": float(np.mean(ols_r2s)),
            "RMSE": float(np.mean(ols_rmses)),
            "MAE": float(np.mean(ols_maes)),
            "Test_N": len(d),
        },
        {
            "Protocol": f"GroupKFold ({n_splits}-fold Country)",
            "Model": "Random Forest",
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
        "temporal_rf_r2": float(r2_score(d_test[TARGET], p_rf_test)),
        "temporal_naive_r2": float(r2_score(test_valid_naive[TARGET], test_valid_naive["naive_pred"])),
        "groupkfold_rf_r2": float(np.mean(rf_r2s)),
        "groupkfold_ols_r2": float(np.mean(ols_r2s)),
    }

