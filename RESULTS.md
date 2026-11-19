# RESULTS.md — Numbers Register

This document serves as the authoritative Numbers Register for HappiScope. Every statistic, parameter estimate, test statistic, and performance metric cited in project reports and publications traces directly to an entry in this register.

---

## 1. Panel Econometric Models

| Claim / Metric | Value | Model / Specification | Producing Function | Source File / Output Artifact |
|---|---|---|---|---|
| Pooled OLS Log GDP Beta | `+0.3566` | Pooled OLS (Complete Cases, N=2,103) | `analysis.panel_models:pooled_ols` | `outputs/panel_models_comparison.csv` |
| Pooled OLS Social Support Beta | `+2.6272` | Pooled OLS (Complete Cases, N=2,103) | `analysis.panel_models:pooled_ols` | `outputs/panel_models_comparison.csv` |
| Pooled OLS Healthy Life Exp Beta | `+0.0258` | Pooled OLS (Complete Cases, N=2,103) | `analysis.panel_models:pooled_ols` | `outputs/panel_models_comparison.csv` |
| Pooled OLS Freedom Beta | `+1.2308` | Pooled OLS (Complete Cases, N=2,103) | `analysis.panel_models:pooled_ols` | `outputs/panel_models_comparison.csv` |
| Pooled OLS Generosity Beta | `+0.5174` | Pooled OLS (Complete Cases, N=2,103) | `analysis.panel_models:pooled_ols` | `outputs/panel_models_comparison.csv` |
| Pooled OLS Corruption Beta | `-0.7417` | Pooled OLS (Complete Cases, N=2,103) | `analysis.panel_models:pooled_ols` | `outputs/panel_models_comparison.csv` |
| Pooled OLS Durbin-Watson | `0.5650` | Pooled OLS (Severe Residual Autocorrelation) | `analysis.panel_models:pooled_ols` | `outputs/mundlak_specification.csv` |
| Between Estimator Log GDP Beta | `+0.3106` | Between Estimator (Country Means, N=155) | `analysis.panel_models:between_estimator` | `outputs/panel_models_comparison.csv` |
| Between Estimator Social Support Beta | `+2.4157` | Between Estimator (Country Means, N=155) | `analysis.panel_models:between_estimator` | `outputs/panel_models_comparison.csv` |
| Between Estimator Healthy Life Exp Beta | `+0.0305` | Between Estimator (Country Means, N=155) | `analysis.panel_models:between_estimator` | `outputs/panel_models_comparison.csv` |
| Between Estimator Freedom Beta | `+1.6438` | Between Estimator (Country Means, N=155) | `analysis.panel_models:between_estimator` | `outputs/panel_models_comparison.csv` |
| Between Estimator Generosity Beta | `+0.4410` | Between Estimator (Country Means, N=155) | `analysis.panel_models:between_estimator` | `outputs/panel_models_comparison.csv` |
| Between Estimator Corruption Beta | `-0.6163` | Between Estimator (Country Means, N=155) | `analysis.panel_models:between_estimator` | `outputs/panel_models_comparison.csv` |
| Between Estimator Durbin-Watson | `2.0096` | Between Estimator (Cross-Sectional Zero Autocorr) | `analysis.panel_models:between_estimator` | `outputs/mundlak_specification.csv` |
| Within FE Log GDP Beta | `+0.5626` | Two-Way Fixed Effects (Country + Year, Clustered SE) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Log GDP Clustered SE | `0.1098` | Two-Way Fixed Effects (Entity-Clustered) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Log GDP p-value | `3.28e-07` | Two-Way Fixed Effects ($t = 5.12$) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Social Support Beta | `+2.4137` | Two-Way Fixed Effects (Entity-Clustered) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Healthy Life Exp Beta | `-0.0101` | Two-Way Fixed Effects (Statistically Null, p=0.259) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Freedom Beta | `+0.8543` | Two-Way Fixed Effects (Entity-Clustered) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Generosity Beta | `+0.6206` | Two-Way Fixed Effects (Entity-Clustered) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Corruption Beta | `-0.8282` | Two-Way Fixed Effects (Entity-Clustered) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Durbin-Watson | `1.1723` | Two-Way Fixed Effects Residual Autocorrelation | `analysis.panel_models:within_fe` | `outputs/mundlak_specification.csv` |
| Log GDP Between-to-Within Ratio | `0.5521` | Ratio of Between Beta to Within Beta (0.3106 / 0.5626) | `analysis.panel_models:comparison_table` | `outputs/mundlak_specification.csv` |
| Mundlak Joint Wald Statistic | `16.7814` | Wald Chi-Square Test ($df=6$) | `analysis.panel_models:mundlak` | `outputs/mundlak_specification.csv` |
| Mundlak Joint Wald p-value | `0.0101` | Rejection of Within == Between Equality | `analysis.panel_models:mundlak` | `outputs/mundlak_specification.csv` |

---

## 2. Multivariate Piecewise Regression & Threshold Stability

| Claim / Metric | Value | Model / Specification | Producing Function | Source File / Output Artifact |
|---|---|---|---|---|
| Multivariate Piecewise Breakpoint $\tau^*$ | `7.6480` | AIC Minimum Grid Search with Controls ($\approx \$2,096$) | `analysis.breakpoint:multivariate_piecewise` | `outputs/multivariate_piecewise.csv` |
| Slope Below Breakpoint ($\beta_1$) | `-0.2811` | Multivariate Continuous Piecewise (Clustered SE) | `analysis.breakpoint:multivariate_piecewise` | `outputs/multivariate_piecewise.csv` |
| Slope Below Standard Error | `0.1495` | Clustered SE ($p = 0.0600$, Null / Marginal) | `analysis.breakpoint:multivariate_piecewise` | `outputs/multivariate_piecewise.csv` |
| Slope Change ($\beta_2$) | `+0.7026` | Multivariate Continuous Piecewise (Clustered SE) | `analysis.breakpoint:multivariate_piecewise` | `outputs/multivariate_piecewise.csv` |
| Slope Change Standard Error | `0.1717` | Clustered SE ($p = 4.26 \times 10^{-5}$) | `analysis.breakpoint:multivariate_piecewise` | `outputs/multivariate_piecewise.csv` |
| Combined Slope Above ($\beta_1 + \beta_2$) | `+0.4215` | Linear Combination with $\text{Cov}(\hat{\beta}_1, \hat{\beta}_2)$ | `analysis.breakpoint:multivariate_piecewise` | `outputs/multivariate_piecewise.csv` |
| Combined Slope Above SE | `0.0710` | $\sqrt{\text{Var}(b_1) + \text{Var}(b_2) + 2\text{Cov}(b_1, b_2)}$ | `analysis.breakpoint:multivariate_piecewise` | `outputs/multivariate_piecewise.csv` |
| Combined Slope Above p-value | `2.96e-09` | Asymptotic Normal Two-Tailed Test | `analysis.breakpoint:multivariate_piecewise` | `outputs/multivariate_piecewise.csv` |
| Block Bootstrap Median $\tau$ | `9.4050` | 1,000 Block Resamples by Whole Country | `analysis.breakpoint:block_bootstrap_tau` | `outputs/breakpoint_block_bootstrap_summary.csv` |
| Block Bootstrap 95% CI Lower | `7.5319` | 2.5th Percentile ($\approx \$1,867$) | `analysis.breakpoint:block_bootstrap_tau` | `outputs/breakpoint_block_bootstrap_summary.csv` |
| Block Bootstrap 95% CI Upper | `10.8600` | 97.5th Percentile ($\approx \$52,052$) | `analysis.breakpoint:block_bootstrap_tau` | `outputs/breakpoint_block_bootstrap_summary.csv` |
| Significant Yearly Breakpoints ($p < 0.05$) | `14 / 18` | Annual Single-Year Regressions 2006–2023 ($77.8\%$) | `analysis.breakpoint:yearly_piecewise_significance` | `outputs/yearly_piecewise_stability.csv` |
| 2023 Cross-Sectional Breakpoint p-value | `0.1050` | Complete-Case 2023 Piecewise Regression ($N=120$) | `analysis.breakpoint:yearly_piecewise_significance` | `outputs/yearly_piecewise_stability.csv` |
| 2022 Cross-Sectional Breakpoint p-value | `0.0686` | Complete-Case 2022 Piecewise Regression ($N=127$) | `analysis.breakpoint:yearly_piecewise_significance` | `outputs/yearly_piecewise_stability.csv` |

---

## 3. Leak-Free Model Validation Benchmarks

| Claim / Metric | Value | Model / Specification | Producing Function | Source File / Output Artifact |
|---|---|---|---|---|
| Old Leaking Random Split RF $R^2$ | `0.8663` | Random Row 80/20 Split (Information Leakage) | `happiscope.ipynb` (Historical Baseline) | `data/importance_comparison.csv` |
| Temporal Split Test OLS $R^2$ | `0.7580` | Forward-Chaining Temporal Split (Test 2019–2023) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Test OLS RMSE | `0.5495` | Forward-Chaining Temporal Split (N=595) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Test RF $R^2$ | `0.7779` | Forward-Chaining Temporal Split (Test 2019–2023) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Test RF RMSE | `0.5265` | Forward-Chaining Temporal Split (N=595) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Naive Baseline $R^2$ | `0.8671` | Country Prior-Year Value Persistence ($Y_{i, t-1}$) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Naive Baseline RMSE | `0.4072` | Country Prior-Year Persistence (N=595) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Naive Baseline MAE | `0.2876` | Country Prior-Year Persistence (N=595) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| GroupKFold OLS Mean $R^2$ | `0.7065` | 5-Fold Cross-Validation Grouped by Country | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| GroupKFold OLS Mean RMSE | `0.5850` | 5-Fold Cross-Validation Grouped by Country | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| GroupKFold RF Mean $R^2$ | `0.6940` | 5-Fold Cross-Validation Grouped by Country | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| GroupKFold RF Mean RMSE | `0.6068` | 5-Fold Cross-Validation Grouped by Country | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |

---

## 4. Evaluative vs. Emotional Affect Models (Kahneman & Deaton, 2010)

| Claim / Metric | Value | Model / Specification | Producing Function | Source File / Output Artifact |
|---|---|---|---|---|
| Life Ladder Raw SD | `1.1357` | Complete Cases (N=2,103, Mean=5.465) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Life Ladder Fully-Standardized GDP Beta | `+0.3623` | Both Outcome and Predictors z-scored ($SE=0.0226$) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Life Ladder Model $R^2$ | `0.7532` | Scale-Free Explained Variance | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Positive Affect Raw SD | `0.1074` | Complete Cases (N=2,098, Mean=0.6538) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Positive Affect Fully-Standardized GDP Beta | `-0.1523` | Both Outcome and Predictors z-scored ($SE=0.0344, p=1.02e-05$) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Positive Affect Model $R^2$ | `0.4274` | Scale-Free Explained Variance | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Negative Affect Raw SD | `0.0854` | Complete Cases (N=2,102, Mean=0.2747) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Negative Affect Fully-Standardized GDP Beta | `-0.0527` | Both Outcome and Predictors z-scored ($SE=0.0383, p=0.1683$) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Negative Affect Model $R^2$ | `0.2906` | Scale-Free Explained Variance | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |

---

## 5. Relative Income & Social Comparison (Easterlin Mechanism)

| Claim / Metric | Value | Model / Specification | Producing Function | Source File / Output Artifact |
|---|---|---|---|---|
| Pooled Own Log GDP Beta ($X$) | `+0.3321` | Pooled OLS with Clustered SE ($p = 8.10 \times 10^{-7}$) | `analysis.relative_income:evaluate_relative_income` | `outputs/relative_income_social_comparison.csv` |
| Pooled Regional Mean Log GDP Beta ($M$) | `+0.0892` | Pooled OLS with Clustered SE ($p = 0.1706$, Not Sig) | `analysis.relative_income:evaluate_relative_income` | `outputs/relative_income_social_comparison.csv` |
| Within FE Own Log GDP Beta ($X$) | `+0.5543` | Two-Way Fixed Effects ($p < 0.0001$) | `analysis.relative_income:evaluate_relative_income` | `outputs/relative_income_social_comparison.csv` |
| Within FE Regional Mean Log GDP Beta ($M$) | `+0.1235` | Two-Way Fixed Effects ($p = 0.1568$, Not Sig) | `analysis.relative_income:evaluate_relative_income` | `outputs/relative_income_social_comparison.csv` |
| Regional Mean GDP Direction | `Positive (+)` | Consistent with Regional Economic Spillovers, NOT Social Comparison | `analysis.relative_income:evaluate_relative_income` | `outputs/relative_income_social_comparison.csv` |
| Own Log GDP per capita VIF | `4.6920` | Multicollinearity Check ($VIF < 10.0$) | `analysis.relative_income:evaluate_relative_income` | `outputs/relative_income_vif.csv` |
| Regional Mean Log GDP VIF | `2.8113` | Multicollinearity Check ($VIF < 10.0$) | `analysis.relative_income:evaluate_relative_income` | `outputs/relative_income_vif.csv` |

---

## 6. Country Residuals, Fixed Effects & Regional Systematicity

| Claim / Metric | Value | Model / Specification | Producing Function | Source File / Output Artifact |
|---|---|---|---|---|
| Regional ANOVA $F$-Statistic | `9.1716` | One-Way ANOVA of Country Effects by Region ($df=5$) | `analysis.residuals:analyze_residuals` | `outputs/residual_diagnostics_summary.csv` |
| Regional ANOVA $p$-value | `1.26e-07` | Significant Regional Systematicity in Baseline Happiness | `analysis.residuals:analyze_residuals` | `outputs/residual_diagnostics_summary.csv` |
| Africa Mean Country Effect | `-1.2425` | Two-Way FE Country Intercept ($95\% \text{ CI: } [-1.3809, -1.1041]$) | `analysis.residuals:analyze_residuals` | `outputs/regional_residual_effects.csv` |
| Asia Mean Country Effect | `-1.3651` | Two-Way FE Country Intercept ($95\% \text{ CI: } [-1.5067, -1.2235]$) | `analysis.residuals:analyze_residuals` | `outputs/regional_residual_effects.csv` |
| Europe Mean Country Effect | `-1.1458` | Two-Way FE Country Intercept ($95\% \text{ CI: } [-1.2481, -1.0435]$) | `analysis.residuals:analyze_residuals` | `outputs/regional_residual_effects.csv` |
| North America Mean Country Effect | `-0.6735` | Two-Way FE Country Intercept ($95\% \text{ CI: } [-0.9325, -0.4146]$) | `analysis.residuals:analyze_residuals` | `outputs/regional_residual_effects.csv` |
| South America Mean Country Effect | `-0.6595` | Two-Way FE Country Intercept ($95\% \text{ CI: } [-0.8115, -0.5075]$) | `analysis.residuals:analyze_residuals` | `outputs/regional_residual_effects.csv` |
| Within-Country Residual Lag-1 Autocorr | `0.4519` | Longitudinal Persistence of Idiosyncratic Residuals ($N=1,948$ pairs) | `analysis.residuals:analyze_residuals` | `outputs/residual_diagnostics_summary.csv` |
| Top 1 Over-Performer | `Costa Rica` | Country Effect `=-0.0101` ($N=18$ years) | `analysis.residuals:analyze_residuals` | `outputs/top_15_overperformers.csv` |
| Top 1 Under-Performer | `Botswana` | Country Effect `=-2.8188` ($N=14$ years) | `analysis.residuals:analyze_residuals` | `outputs/top_15_underperformers.csv` |

