# RESULTS.md — Numbers Register

This document serves as the authoritative Numbers Register for HappiScope. Every statistic, parameter estimate, test statistic, and performance metric cited in project reports and publications traces directly to an entry in this register.

---

## 1. Panel Econometric Models

### Bivariate Specifications (Easterlin Paradox Test: Life Ladder ~ Log GDP per capita only)

| Claim / Metric | Value | Model / Specification | Producing Function | Source File / Output Artifact |
|---|---|---|---|---|
| Bivariate Pooled OLS Log GDP Beta (raw, ladder points / log unit) | `+0.7750` | Pooled OLS (Complete Cases, N=2,103, SE=0.0132, 95% CI: [0.7490, 0.8009], $R^2=0.6198$) | `analysis.panel_models:bivariate_panel_models` | `outputs/bivariate_panel_models.csv` |
| Bivariate Pooled OLS (Clustered SE) (raw) | `+0.7750` | Pooled OLS (Cluster-Robust SE=0.0353, 95% CI: [0.7058, 0.8442]) | `analysis.panel_models:bivariate_panel_models` | `outputs/bivariate_panel_models.csv` |
| Pairwise Bivariate OLS Log GDP Beta (raw, ladder points / log unit) | `+0.7609` | Pairwise Complete on GDP and Ladder ($N=2,335, R^2=0.6140$) | `views/the_debate.py` | `views/the_debate.py` |
| Bivariate Between Estimator Log GDP Beta (raw, ladder points / log unit) | `+0.7454` | Between Estimator (Country Means, N=155, SE=0.0398, 95% CI: [0.6668, 0.8240], $R^2=0.6964$) | `analysis.panel_models:bivariate_panel_models` | `outputs/bivariate_panel_models.csv` |
| Bivariate Within FE (Country only) Beta (raw, ladder points / log unit) | `+0.7229` | Within Country FE (Entity Clustered SE=0.1526, 95% CI: [0.4236, 1.0222], $R^2_{\text{within}}=0.0974$) | `analysis.panel_models:bivariate_panel_models` | `outputs/bivariate_panel_models.csv` |
| Bivariate Within FE (Country + Year) Beta (raw, ladder points / log unit) | `+0.7175` | Two-Way FE (Entity Clustered SE=0.1807, 95% CI: [0.3631, 1.0719], $R^2_{\text{within}}=0.0974$) | `analysis.panel_models:bivariate_panel_models` | `outputs/bivariate_panel_models.csv` |
| Bivariate Mundlak Slope Equality Wald | `0.1137` | Wald $\chi^2(1)$ Test ($p = 0.7360$, Cannot Reject Between == Within Equality) | `analysis.panel_models:bivariate_panel_models` | `outputs/bivariate_panel_models.csv` |
| Bivariate Mundlak Difference Coef ($\gamma$, raw) | `+0.0533` | Mean Term Coef $\beta_{\text{between}} - \beta_{\text{within}}$ ($SE=0.1582, z=0.337, p=0.7360$) | `analysis.panel_models:bivariate_panel_models` | `outputs/bivariate_panel_models.csv` |
| Easterlin Ratio (Between / Within Country-Only) | `1.0311` | Point Ratio of Between Beta (0.7454) to Within Country-FE Beta (0.7229) | `analysis.panel_models:bivariate_panel_models` | `outputs/bivariate_panel_models.csv` |
| Secular-Trend-Absorbed Ratio (Between / Within Two-Way) | `1.0388` | Point Ratio of Between Beta (0.7454) to Within Two-Way FE Beta (0.7175) | `analysis.panel_models:bivariate_panel_models` | `outputs/bivariate_panel_models.csv` |
| Joint Test of Year Fixed Effects | `1075.24` | Wald $\chi^2(18)$ Test ($p = 5.75 \times 10^{-217}$, Strongly Significant) | Verification Step C | Session Terminal |
| Centered Year Effects Linear Trend (2006–2023) | `+0.0015` | OLS Slope on Centered Year Effects ($SE=0.0031, p=0.6449, R^2=0.0136$) | Verification Step 1 | `outputs/year_effects_linear_trend.csv` |

### Multivariate Specifications (Conditional / Partial Effects Controlling for Other 5 WHR Drivers)

| Claim / Metric | Value | Model / Specification | Producing Function | Source File / Output Artifact |
|---|---|---|---|---|
| Pooled OLS Log GDP Beta (raw, ladder points / log unit) | `+0.3566` | Pooled OLS (Complete Cases, N=2,103) | `analysis.panel_models:pooled_ols` | `outputs/panel_models_comparison.csv` |
| Pooled OLS Social Support Beta (raw) | `+2.6272` | Pooled OLS (Complete Cases, N=2,103) | `analysis.panel_models:pooled_ols` | `outputs/panel_models_comparison.csv` |
| Pooled OLS Healthy Life Exp Beta (raw) | `+0.0258` | Pooled OLS (Complete Cases, N=2,103) | `analysis.panel_models:pooled_ols` | `outputs/panel_models_comparison.csv` |
| Pooled OLS Freedom Beta (raw) | `+1.2308` | Pooled OLS (Complete Cases, N=2,103) | `analysis.panel_models:pooled_ols` | `outputs/panel_models_comparison.csv` |
| Pooled OLS Generosity Beta (raw) | `+0.5174` | Pooled OLS (Complete Cases, N=2,103) | `analysis.panel_models:pooled_ols` | `outputs/panel_models_comparison.csv` |
| Pooled OLS Corruption Beta (raw) | `-0.7417` | Pooled OLS (Complete Cases, N=2,103) | `analysis.panel_models:pooled_ols` | `outputs/panel_models_comparison.csv` |
| Pooled OLS Durbin-Watson | `0.5650` | Pooled OLS (Severe Residual Autocorrelation) | `analysis.panel_models:pooled_ols` | `outputs/mundlak_specification.csv` |
| Between Estimator Log GDP Beta (raw, ladder points / log unit) | `+0.3106` | Between Estimator (Country Means, N=155) | `analysis.panel_models:between_estimator` | `outputs/panel_models_comparison.csv` |
| Between Estimator Social Support Beta (raw) | `+2.4157` | Between Estimator (Country Means, N=155) | `analysis.panel_models:between_estimator` | `outputs/panel_models_comparison.csv` |
| Between Estimator Healthy Life Exp Beta (raw) | `+0.0305` | Between Estimator (Country Means, N=155) | `analysis.panel_models:between_estimator` | `outputs/panel_models_comparison.csv` |
| Between Estimator Freedom Beta (raw) | `+1.6438` | Between Estimator (Country Means, N=155) | `analysis.panel_models:between_estimator` | `outputs/panel_models_comparison.csv` |
| Between Estimator Generosity Beta (raw) | `+0.4410` | Between Estimator (Country Means, N=155) | `analysis.panel_models:between_estimator` | `outputs/panel_models_comparison.csv` |
| Between Estimator Corruption Beta (raw) | `-0.6163` | Between Estimator (Country Means, N=155) | `analysis.panel_models:between_estimator` | `outputs/panel_models_comparison.csv` |
| Between Estimator Durbin-Watson | `2.0096` | Between Estimator (Cross-Sectional Zero Autocorr) | `analysis.panel_models:between_estimator` | `outputs/mundlak_specification.csv` |
| Within FE Log GDP Beta (raw, ladder points / log unit) | `+0.5626` | Two-Way Fixed Effects (Country + Year, Clustered SE) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Log GDP Clustered SE | `0.1098` | Two-Way Fixed Effects (Entity-Clustered) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Log GDP p-value | `3.28e-07` | Two-Way Fixed Effects ($t = 5.12$) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Social Support Beta (raw) | `+2.4137` | Two-Way Fixed Effects (Entity-Clustered) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Healthy Life Exp Beta (raw) | `-0.0101` | Two-Way Fixed Effects (Statistically Null, p=0.259) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Freedom Beta (raw) | `+0.8543` | Two-Way Fixed Effects (Entity-Clustered) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Generosity Beta (raw) | `+0.6206` | Two-Way Fixed Effects (Entity-Clustered) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Corruption Beta | `-0.8282` | Two-Way Fixed Effects (Entity-Clustered) | `analysis.panel_models:within_fe` | `outputs/panel_models_comparison.csv` |
| Within FE Durbin-Watson | `1.1723` | Two-Way Fixed Effects Residual Autocorrelation | `analysis.panel_models:within_fe` | `outputs/mundlak_specification.csv` |
| Multivariate Partial Between-to-Within Ratio | `0.5521` | Ratio of Partial Between Beta to Within Beta (0.3106 / 0.5626) | `analysis.panel_models:comparison_table` | `outputs/mundlak_specification.csv` |
| Mundlak Joint Wald Statistic | `16.7814` | Wald Chi-Square Test ($df=6$) | `analysis.panel_models:mundlak` | `outputs/mundlak_specification.csv` |
| Mundlak Joint Wald p-value | `0.0101` | Rejection of Within == Between Equality | `analysis.panel_models:mundlak` | `outputs/mundlak_specification.csv` |
| Multivariate Mundlak Log GDP Within vs Between Diff | `-0.2564` | Within +0.5630 vs Between +0.3066 ($\text{Wald } \chi^2(1)=4.9606, p=0.0259$) | `analysis.panel_models:mundlak` | `outputs/mundlak_driver_tests.csv` |
| Multivariate Mundlak Health Within vs Between Diff | `+0.0454` | Within -0.0108 vs Between +0.0346 ($\text{Wald } \chi^2(1)=7.8673, p=0.0050$) | `analysis.panel_models:mundlak` | `outputs/mundlak_driver_tests.csv` |
| Multivariate Mundlak Freedom Within vs Between Diff | `+0.7345` | Within +0.7978 vs Between +1.5323 ($\text{Wald } \chi^2(1)=2.4597, p=0.1168$) | `analysis.panel_models:mundlak` | `outputs/mundlak_driver_tests.csv` |
| Multivariate Mundlak Support Within vs Between Diff | `+0.2603` | Within +2.3058 vs Between +2.5661 ($\text{Wald } \chi^2(1)=0.2189, p=0.6399$) | `analysis.panel_models:mundlak` | `outputs/mundlak_driver_tests.csv` |

---

## 2. Multivariate Piecewise Regression & Threshold Stability

| Claim / Metric | Value | Model / Specification | Producing Function | Source File / Output Artifact |
|---|---|---|---|---|
| Sample AIC Minimum Breakpoint $\tau_1^*$ | `7.6480` | AIC Global Minimum with Controls ($\approx \$2,096$) | `analysis.breakpoint:multivariate_piecewise` | `outputs/multivariate_piecewise.csv` |
| Observations Below $\tau_1^*$ (7.648) | `210 (9.99%)` | Thin tail identifying lower mode ($<10\%$ of panel) | Evaluation script | Session Terminal |
| Observations Above $\tau_1^*$ (7.648) | `1,893 (90.01%)` | Bulk of complete-case panel ($N=2,103$) | Evaluation script | Session Terminal |
| Slope Below Breakpoint 7.648 ($\beta_1$) | `-0.2811` | Clustered SE ($SE=0.1495, p=0.0600$, Thin-Tail Artifact) | `analysis.breakpoint:multivariate_piecewise` | `outputs/multivariate_piecewise.csv` |
| Slope Change at 7.648 ($\beta_2$) | `+0.7026` | Clustered SE ($SE=0.1717, p = 4.26 \times 10^{-5}$) | `analysis.breakpoint:multivariate_piecewise` | `outputs/multivariate_piecewise.csv` |
| Combined Slope Above 7.648 ($\beta_1 + \beta_2$) | `+0.4215` | Linear Combination ($SE=0.0710, p=2.96 \times 10^{-9}$) | `analysis.breakpoint:multivariate_piecewise` | `outputs/multivariate_piecewise.csv` |
| Breakpoint 7.648 Model $R^2$ | `0.7590` | Multivariate Continuous Piecewise Regression | `analysis.breakpoint:piecewise_threshold_sensitivity` | `outputs/piecewise_threshold_sensitivity.csv` |
| Breakpoint 7.648 Model AIC | `3527.1647` | Sample AIC Global Minimum | `analysis.breakpoint:piecewise_threshold_sensitivity` | `outputs/piecewise_threshold_sensitivity.csv` |
| Breakpoint 7.648 Model BIC | `3572.3736` | Sample AIC Global Minimum | `analysis.breakpoint:piecewise_threshold_sensitivity` | `outputs/piecewise_threshold_sensitivity.csv` |
| Substantively Preferred Breakpoint $\tau_2^*$ | `9.4050` | Block Bootstrap Median Mode ($\approx \$12,149$) | `analysis.breakpoint:block_bootstrap_tau` | `outputs/breakpoint_block_bootstrap_summary.csv` |
| Observations Below $\tau_2^*$ (9.405) | `986 (46.89%)` | Balanced sample partition | `analysis.breakpoint:piecewise_threshold_sensitivity` | `outputs/piecewise_threshold_sensitivity.csv` |
| Observations Above $\tau_2^*$ (9.405) | `1,117 (53.11%)` | Balanced sample partition | `analysis.breakpoint:piecewise_threshold_sensitivity` | `outputs/piecewise_threshold_sensitivity.csv` |
| Slope Below Breakpoint 9.405 ($\beta_1$) | `+0.2349` | Clustered SE ($SE=0.0826, p=0.0045$, Statistically Positive) | `analysis.breakpoint:piecewise_threshold_sensitivity` | `outputs/piecewise_threshold_sensitivity.csv` |
| Slope Change at 9.405 ($\beta_2$) | `+0.2988` | Clustered SE ($SE=0.1289, p=0.0205$, Statistically Positive) | `analysis.breakpoint:piecewise_threshold_sensitivity` | `outputs/piecewise_threshold_sensitivity.csv` |
| Combined Slope Above 9.405 ($\beta_1 + \beta_2$) | `+0.5337` | Linear Combination ($SE=0.1009, p=1.23 \times 10^{-7}$) | `analysis.breakpoint:piecewise_threshold_sensitivity` | `outputs/piecewise_threshold_sensitivity.csv` |
| Breakpoint 9.405 Model $R^2$ | `0.7581` | Multivariate Continuous Piecewise Regression | `analysis.breakpoint:piecewise_threshold_sensitivity` | `outputs/piecewise_threshold_sensitivity.csv` |
| Breakpoint 9.405 Model AIC | `3534.9658` | Secondary AIC Mode ($\Delta \text{AIC} = +7.80$ vs 7.648) | `analysis.breakpoint:piecewise_threshold_sensitivity` | `outputs/piecewise_threshold_sensitivity.csv` |
| Breakpoint 9.405 Model BIC | `3580.1748` | Secondary AIC Mode | `analysis.breakpoint:piecewise_threshold_sensitivity` | `outputs/piecewise_threshold_sensitivity.csv` |
| Block Bootstrap 95% CI Lower | `7.5319` | 2.5th Percentile ($\approx \$1,867$) | `analysis.breakpoint:block_bootstrap_tau` | `outputs/breakpoint_block_bootstrap_summary.csv` |
| Block Bootstrap 95% CI Upper | `10.8600` | 97.5th Percentile ($\approx \$52,052$) | `analysis.breakpoint:block_bootstrap_tau` | `outputs/breakpoint_block_bootstrap_summary.csv` |
| Satiation Evidence Characterization | `No Evidence` | Relationship accelerates above threshold, no flattening | `analysis.breakpoint:multivariate_piecewise` | `outputs/multivariate_piecewise.csv` |
| Significant Yearly Breakpoints ($p < 0.05$) | `14 / 18` | Annual Single-Year Regressions 2006–2023 ($77.8\%$) | `analysis.breakpoint:yearly_piecewise_significance` | `outputs/yearly_piecewise_stability.csv` |
| 2023 Cross-Sectional Breakpoint p-value | `0.1050` | Complete-Case 2023 Piecewise Regression ($N=120$) | `analysis.breakpoint:yearly_piecewise_significance` | `outputs/yearly_piecewise_stability.csv` |
| 2022 Cross-Sectional Breakpoint p-value | `0.0686` | Complete-Case 2022 Piecewise Regression ($N=127$) | `analysis.breakpoint:yearly_piecewise_significance` | `outputs/yearly_piecewise_stability.csv` |

---

## 3. Leak-Free Model Validation Benchmarks

| Claim / Metric | Value | Model / Specification | Producing Function | Source File / Output Artifact |
|---|---|---|---|---|
| Old Leaking Random Split RF $R^2$ | `0.8663` | Random Row 80/20 Split (Information Leakage) | `happiscope.ipynb` (Historical Baseline) | `data/importance_comparison.csv` |
| Temporal Split Test OLS (contemporaneous) $R^2$ | `0.7604` | Forward-Chaining Temporal Split (Test 2019–2023, 6 WHR Drivers) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Test OLS (contemporaneous) RMSE | `0.5468` | Forward-Chaining Temporal Split (Test N=595, MAE=0.4132) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Test RF (contemporaneous) $R^2$ | `0.7731` | Forward-Chaining Temporal Split (Test 2019–2023, 6 WHR Drivers) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Test RF (contemporaneous) RMSE | `0.5321` | Forward-Chaining Temporal Split (Test N=595, MAE=0.4002) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Naive Baseline $R^2$ | `0.8671` | Country Prior-Year Value Persistence (has access to lagged outcome $Y_{i, t-1}$) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Naive Baseline RMSE | `0.4072` | Country Prior-Year Persistence (Test N=595, MAE=0.2876) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Augmented OLS (with lagged outcome) $R^2$ | `0.8913` | Forward-Chaining Temporal Split (6 WHR Drivers + $Y_{i, t-1}$) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Augmented OLS RMSE | `0.3682` | Forward-Chaining Temporal Split (Test N=595, MAE=0.2623) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Augmented RF (with lagged outcome) $R^2$ | `0.8804` | Forward-Chaining Temporal Split (6 WHR Drivers + $Y_{i, t-1}$) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Temporal Split Augmented RF RMSE | `0.3864` | Forward-Chaining Temporal Split (Test N=595, MAE=0.2759) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| Nested Model F-Test (Incremental Value of Drivers) | `28.4171` | $F(6, 587)$ on Test Set ($p < 1.0 \times 10^{-20}$, Highly Significant Improvement) | Evaluation Script | Session Terminal |
| GroupKFold OLS Mean $R^2$ | `0.7065` | 5-Fold Cross-Validation Grouped by Country (N=2,103, MAE=0.4506) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| GroupKFold OLS Mean RMSE | `0.5850` | 5-Fold Cross-Validation Grouped by Country | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| GroupKFold RF Mean $R^2$ | `0.6940` | 5-Fold Cross-Validation Grouped by Country (N=2,103, MAE=0.4712) | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |
| GroupKFold RF Mean RMSE | `0.6068` | 5-Fold Cross-Validation Grouped by Country | `analysis.validation:evaluate_leak_free_models` | `outputs/validation_leak_free_benchmarks.csv` |

---

## 4. Evaluative vs. Emotional Affect Models (Kahneman & Deaton, 2010)

| Claim / Metric | Value | Model / Specification | Producing Function | Source File / Output Artifact |
|---|---|---|---|---|
| Life Ladder Raw SD | `1.1357` | Complete Cases (N=2,103, Mean=5.465) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Life Ladder Bivariate GDP Beta (Pairwise, standardized, SD / SD) | `+0.7836` | Unconditional OLS, Pairwise ($N=2,335, SE=0.0129, p<0.0001, R^2=0.6140$) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Life Ladder Bivariate GDP Beta (Complete Cases, standardized, SD / SD) | `+0.7873` | Unconditional OLS, Complete Sample ($N=2,103, SE=0.0135, p<0.0001, R^2=0.6198$) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Life Ladder Conditional GDP Beta (standardized, SD / SD) | `+0.3623` | Fully Standardized, Controlling for 5 Drivers ($SE=0.0226, p=8.69e-55, R^2=0.7532$) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Positive Affect Raw SD | `0.1074` | Complete Cases (N=2,098, Mean=0.6538) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Positive Affect Bivariate GDP Beta (Pairwise, standardized, SD / SD) | `+0.2309` | Unconditional OLS, Pairwise ($N=2,311, SE=0.0202, p=2.46e-29, R^2=0.0533$) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Positive Affect Bivariate GDP Beta (Complete Cases, standardized, SD / SD) | `+0.2226` | Unconditional OLS, Complete Sample ($N=2,098, SE=0.0213, p=5.75e-25, R^2=0.0495$) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Positive Affect Conditional GDP Beta (standardized, SD / SD) | `-0.1523` | Fully Standardized, Controlling for 5 Drivers ($SE=0.0344, p=1.02e-05, R^2=0.4274$) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Negative Affect Raw SD | `0.0854` | Complete Cases (N=2,102, Mean=0.2747) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Negative Affect Bivariate GDP Beta (Pairwise, standardized, SD / SD) | `-0.2607` | Unconditional OLS, Pairwise ($N=2,319, SE=0.0201, p=2.46e-37, R^2=0.0680$) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Negative Affect Bivariate GDP Beta (Complete Cases, standardized, SD / SD) | `-0.2691` | Unconditional OLS, Complete Sample ($N=2,102, SE=0.0210, p=3.30e-36, R^2=0.0724$) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Negative Affect Conditional GDP Beta (standardized, SD / SD) | `-0.0527` | Fully Standardized, Controlling for 5 Drivers ($SE=0.0383, p=0.1683, R^2=0.2906$) | `analysis.affect:run_affect_models` | `outputs/affect_standardized_comparison.csv` |
| Log GDP Variance Inflation Factor (Conditional Models) | `4.3286` | Multicollinearity Check in 6-factor model (Pos Affect: 4.33, Neg Affect: 4.33, Ladder: 4.33) | Verification Step A | Session Terminal |

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

## 6. Country Effects, Deviations from Global Mean & Regional Systematicity

| Claim / Metric | Value | Model / Specification | Producing Function | Source File / Output Artifact |
|---|---|---|---|---|
| Total Countries in Panel | `155` | Complete Cases Panel | `analysis.residuals:analyze_residuals` | `outputs/residual_diagnostics_summary.csv` |
| Excluded Countries (<8 observations) | `23` | Dropped to prevent small-sample noise (Somalia, Qatar, etc.) | `analysis.residuals:analyze_residuals` | `outputs/excluded_countries_under_8_obs.csv` |
| Analyzed Countries (>=8 observations) | `132` | Final Stable Sample for Fixed Effects Ranking | `analysis.residuals:analyze_residuals` | `outputs/residual_diagnostics_summary.csv` |
| Regional ANOVA $F$-Statistic | `4.7126` | One-Way ANOVA of Centered Country Effects by Region ($df=5$) | `analysis.residuals:analyze_residuals` | `outputs/residual_diagnostics_summary.csv` |
| Regional ANOVA $p$-value | `0.000558` | Significant Regional Systematicity ($p = 5.58 \times 10^{-4}$) | `analysis.residuals:analyze_residuals` | `outputs/residual_diagnostics_summary.csv` |
| Regional ANOVA Invariance ($F_{\text{raw}} = F_{\text{centered}}$) | `Identical` | Raw F=4.7126 vs Centered F=4.7126 (Difference $< 10^{-14}$) | `analysis.residuals:analyze_residuals` | `outputs/residual_diagnostics_summary.csv` |
| North America Mean Country Effect | `+0.3998` | Deviation from Global Mean ($95\% \text{ CI: } [+0.1000, +0.6995], N=12$) | `analysis.residuals:analyze_residuals` | `outputs/regional_residual_effects.csv` |
| South America Mean Country Effect | `+0.3547` | Deviation from Global Mean ($95\% \text{ CI: } [+0.1470, +0.5623], N=10$) | `analysis.residuals:analyze_residuals` | `outputs/regional_residual_effects.csv` |
| Oceania Mean Country Effect | `+0.1489` | Deviation from Global Mean ($N=2$, Australia & NZ; not interpretable due to small sample size) | `analysis.residuals:analyze_residuals` | `outputs/regional_residual_effects.csv` |
| Europe Mean Country Effect | `+0.0160` | Deviation from Global Mean ($95\% \text{ CI: } [-0.1000, +0.1320], N=39$) | `analysis.residuals:analyze_residuals` | `outputs/regional_residual_effects.csv` |
| Africa Mean Country Effect | `-0.1121` | Deviation from Global Mean ($95\% \text{ CI: } [-0.2630, +0.0389], N=37$) | `analysis.residuals:analyze_residuals` | `outputs/regional_residual_effects.csv` |
| Asia Mean Country Effect | `-0.1600` | Deviation from Global Mean ($95\% \text{ CI: } [-0.3235, +0.0035], N=32$) | `analysis.residuals:analyze_residuals` | `outputs/regional_residual_effects.csv` |
| Within-Country Residual Lag-1 Autocorr | `0.4519` | Longitudinal Persistence of Idiosyncratic Residuals ($N=1,948$ pairs) | `analysis.residuals:analyze_residuals` | `outputs/residual_diagnostics_summary.csv` |
| Top 1 Over-Performer | `Mexico` | Deviation `= +1.0915` ($N=17$ years, North America) | `analysis.residuals:analyze_residuals` | `outputs/top_15_overperformers.csv` |
| Top 2 Over-Performer | `Israel` | Deviation `= +1.0798` ($N=17$ years, Asia) | `analysis.residuals:analyze_residuals` | `outputs/top_15_overperformers.csv` |
| Top 3 Over-Performer | `Costa Rica` | Deviation `= +0.9879` ($N=18$ years, North America) | `analysis.residuals:analyze_residuals` | `outputs/top_15_overperformers.csv` |
| Top 1 Under-Performer | `Botswana` | Deviation `= -1.8066` ($N=14$ years, Africa) | `analysis.residuals:analyze_residuals` | `outputs/top_15_underperformers.csv` |
| Top 2 Under-Performer | `Sri Lanka` | Deviation `= -1.3909` ($N=17$ years, Asia) | `analysis.residuals:analyze_residuals` | `outputs/top_15_underperformers.csv` |
| Top 3 Under-Performer | `Tanzania` | Deviation `= -0.9512` ($N=18$ years, Africa) | `analysis.residuals:analyze_residuals` | `outputs/top_15_underperformers.csv` |

---

## 7. Methodological Audit & Sample Metrics

| Claim / Metric | Value | Model / Specification | Producing Function | Source File / Output Artifact |
|---|---|---|---|---|
| Complete-Case Panel Observations | `2,103` | Listwise complete across 6 drivers (2005–2023) | `common:complete_cases` | `common.py` |
| Total Panel Raw Observations | `2,363` | WHR 2024 updated dataset | `common:load_data` | `data/happiscope_master.csv` |
| Complete-Case Attrition Count | `260` | Dropped observations (11.00%) | Verification script | Session Terminal |
| Complete-Case Attrition Percentage | `11.00%` | Fraction of raw panel lost | Verification script | Session Terminal |
| Dropped Asian Observations Count | `176` | Asian records dropped due to missing indicators | Verification script | Session Terminal |
| Dropped Asian Observations Concentration | `67.69%` | 176 of 260 dropped rows concentrated in Asia | Verification script | Session Terminal |
| Dropped Sample Mean Log GDP | `9.81` | Higher than retained sample ($9.35$) | Verification script | Session Terminal |
| Retained Sample Mean Log GDP | `9.35` | Complete cases average Log GDP | Verification script | Session Terminal |
| Dropped Sample Mean Life Ladder | `5.63` | Higher than retained sample ($5.47$) | Verification script | Session Terminal |
| Retained Sample Mean Life Ladder | `5.47` | Complete cases average Life Ladder | Verification script | Session Terminal |
| Unstandardized OLS vs MDI Spearman Rho | `-0.0857` | Raw arbitrary scales vs Tree Split Importance ($p=0.8717$) | Historical audit | Session Terminal |
| Standardized OLS vs Permutation Spearman Rho | `0.8857` | Standardized Beta vs Test MSE Degradation ($p=0.0188$) | `views.factor_breakdown` | `data/importance_comparison.csv` |

---

## 8. Clustering & Dimensionality Diagnostics

| Claim / Metric | Value | Model / Specification | Producing Function | Source File / Output Artifact |
|---|---|---|---|---|
| 2023 Base Year Complete Observations | `120` | Countries with full 6 drivers in 2023 | `views.clusters_and_trends` | `views/clusters_and_trends.py` |
| 2023 Dropped Countries Count | `18` | Missing drivers in 2023 (13.04% attrition) | `views.clusters_and_trends` | `views/clusters_and_trends.py` |
| 2023 PC1 Explained Variance | `50.80%` | First Principal Component | PCA on 2023 Scaled Factors | Session Terminal |
| 2023 PC2 Explained Variance | `19.79%` | Second Principal Component | PCA on 2023 Scaled Factors | Session Terminal |
| 2023 Total 2D PCA Variance | `70.59%` | Combined 2D Visualization Plane | PCA on 2023 Scaled Factors | Session Terminal |
| K=4 Cluster Bootstrap Stability (Jaccard) | `0.5864` | 100 Bootstrap Resamples Pairwise Co-Membership | Cluster validation | Session Terminal |
| Cluster 1 Standardized Centroid Profile | `GDP +1.28, Trust +1.84` | High-Wealth / High-Institutional-Trust ($N=19$, Mean Ladder=6.99) | `KMeans(k=4, 2023)` | Session Terminal |
| Cluster 2 Standardized Centroid Profile | `GDP -1.31, Support -1.29` | Low-Income / Multi-Deficit Vulnerable ($N=33$, Mean Ladder=4.42) | `KMeans(k=4, 2023)` | Session Terminal |
| Cluster 0 Standardized Centroid Profile | `GDP +0.44, Donation -1.04` | Higher-Income / Low-Donation & High-Corruption ($N=34$, Mean Ladder=5.69) | `KMeans(k=4, 2023)` | Session Terminal |
| Cluster 3 Standardized Centroid Profile | `Freedom +0.58, Support +0.40` | Middle-Income / High-Social-Capital Emerging ($N=34$, Mean Ladder=5.96) | `KMeans(k=4, 2023)` | Session Terminal |

