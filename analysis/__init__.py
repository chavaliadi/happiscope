"""Analysis package for HappiScope.

Pure functions providing econometric panel modeling, leak-free machine learning validation,
multivariate piecewise regressions, affect decomposition, and social comparison tests.
"""
from analysis.panel_models import (
    bivariate_panel_models,
    bivariate_mundlak,
    year_fixed_effects_diagnostics,
    pooled_ols,
    between_estimator,
    within_fe,
    mundlak,
    comparison_table,
)
from analysis.breakpoint import (
    multivariate_piecewise,
    piecewise_threshold_sensitivity,
    block_bootstrap_tau,
    yearly_piecewise_significance,
)
from analysis.validation import (
    evaluate_leak_free_models,
    nested_lagged_model_ftest,
)
from analysis.affect import (
    run_affect_models,
)
from analysis.residuals import (
    analyze_residuals,
)
from analysis.relative_income import (
    evaluate_relative_income,
)

__all__ = [
    "bivariate_panel_models",
    "bivariate_mundlak",
    "year_fixed_effects_diagnostics",
    "pooled_ols",
    "between_estimator",
    "within_fe",
    "mundlak",
    "comparison_table",
    "multivariate_piecewise",
    "piecewise_threshold_sensitivity",
    "block_bootstrap_tau",
    "yearly_piecewise_significance",
    "evaluate_leak_free_models",
    "nested_lagged_model_ftest",
    "run_affect_models",
    "analyze_residuals",
    "evaluate_relative_income",
]

