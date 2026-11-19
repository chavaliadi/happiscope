"""Execution script for HappiScope analytical pipeline.

Executes all Phase 2 analyses, exports CSV tables to outputs/,
and saves publication figures across .png, .pdf, .svg, and .eps formats to figures/.
"""
import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import FACTOR_COLS, FACTORS, TARGET, load_data
from analysis.panel_models import (
    bivariate_panel_models,
    bivariate_mundlak,
    year_fixed_effects_diagnostics,
    comparison_table,
    mundlak,
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
from analysis.affect import run_affect_models
from analysis.residuals import analyze_residuals
from analysis.relative_income import evaluate_relative_income


def save_figure_multi_format(fig: plt.Figure, base_path: Path):
    """Saves a matplotlib figure in .png, .pdf, .svg, and .eps in a single loop."""
    for ext in [".png", ".pdf", ".svg", ".eps"]:
        out_file = base_path.with_suffix(ext)
        fig.savefig(out_file, bbox_inches="tight", dpi=300)
    plt.close(fig)


def main():
    root_dir = Path(__file__).parent
    out_dir = root_dir / "outputs"
    fig_dir = root_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)
    
    print("Loading data via common.load_data()...")
    df = load_data()
    print("df.columns.tolist():", df.columns.tolist())
    print(f"Total raw dataset shape: {df.shape}")
    
    # ------------------------------------------------------------- 1. Panel Econometrics
    print("\n[1/6] Running Panel Econometric Models...")
    biv_res = bivariate_panel_models(df)
    biv_res["summary_table"].to_csv(out_dir / "bivariate_panel_models.csv", index=False)
    print(f"-> Exported bivariate_panel_models.csv (Easterlin Ratio={biv_res['easterlin_ratio']:.4f}, Secular Trend Ratio={biv_res['secular_trend_ratio']:.4f})")
    
    biv_mundlak_res = bivariate_mundlak(df)
    biv_mundlak_df = pd.DataFrame([{
        "Test": "Bivariate Mundlak (Life Ladder ~ Within GDP + Mean GDP)",
        "beta_within": biv_mundlak_res["beta_within"],
        "se_within": biv_mundlak_res["se_within"],
        "p_within": biv_mundlak_res["p_within"],
        "beta_between": biv_mundlak_res["beta_between"],
        "se_between": biv_mundlak_res["se_between"],
        "p_between": biv_mundlak_res["p_between"],
        "gamma_difference": biv_mundlak_res["gamma_diff"],
        "gamma_se": biv_mundlak_res["gamma_se"],
        "gamma_pvalue": biv_mundlak_res["gamma_pvalue"],
        "wald_chi2": biv_mundlak_res["wald_statistic"],
        "wald_pvalue": biv_mundlak_res["wald_pvalue"],
        "n_obs": biv_mundlak_res["n_obs"],
        "n_countries": biv_mundlak_res["n_countries"],
    }])
    biv_mundlak_df.to_csv(out_dir / "bivariate_mundlak_easterlin_test.csv", index=False)
    print(f"-> Exported bivariate_mundlak_easterlin_test.csv (Wald Chi2={biv_mundlak_res['wald_statistic']:.4f}, p={biv_mundlak_res['wald_pvalue']:.4f})")
    
    year_diag = year_fixed_effects_diagnostics(df)
    year_diag["year_table"].to_csv(out_dir / "year_fixed_effects_table.csv", index=False)
    year_diag_summary = pd.DataFrame([{
        "joint_chi2": year_diag["joint_chi2"],
        "joint_pvalue": year_diag["joint_pvalue"],
        "df_difference": year_diag["df_difference"],
        "grand_mean_offset": year_diag["grand_mean_offset"],
        "base_year_2005_n": year_diag["base_year_2005_n"],
        "is_2005_thin": year_diag["is_2005_thin"],
    }])
    year_diag_summary.to_csv(out_dir / "year_fixed_effects_summary.csv", index=False)
    print(f"-> Exported year_fixed_effects_table.csv (Joint Chi2={year_diag['joint_chi2']:.2f}, df={year_diag['df_difference']}, p={year_diag['joint_pvalue']:.2e})")
    
    comp_df, gdp_ratio, dw_dict = comparison_table(df)
    comp_df.to_csv(out_dir / "panel_models_comparison.csv", index=False)
    comp_df.to_csv(out_dir / "multivariate_partial_effects.csv", index=False)
    
    mundlak_res = mundlak(df)
    mundlak_res["driver_wald_table"].to_csv(out_dir / "mundlak_driver_tests.csv", index=False)
    mundlak_summary = pd.DataFrame([{
        "wald_statistic": mundlak_res["wald_statistic"],
        "wald_pvalue": mundlak_res["wald_pvalue"],
        "n_obs": mundlak_res["n_obs"],
        "n_countries": mundlak_res["n_countries"],
        "durbin_watson_pooled": dw_dict["Pooled OLS"],
        "durbin_watson_between": dw_dict["Between Estimator"],
        "durbin_watson_within_fe": dw_dict["Within FE"],
        "bivariate_easterlin_ratio": biv_res["easterlin_ratio"],
        "bivariate_secular_ratio": biv_res["secular_trend_ratio"],
        "bivariate_mundlak_pvalue": biv_mundlak_res["wald_pvalue"],
        "multivariate_gdp_between_to_within_ratio": gdp_ratio,
    }])
    mundlak_summary.to_csv(out_dir / "mundlak_specification.csv", index=False)
    print(f"-> Exported panel_models_comparison.csv and mundlak_specification.csv (Multivariate Partial Ratio={gdp_ratio:.4f})")
    
    # ------------------------------------------------------------- 2. Multivariate Piecewise & Bootstrap
    print("\n[2/6] Running Multivariate Piecewise Regression & Bootstrap...")
    sens_df = piecewise_threshold_sensitivity(df, taus=[7.648, 9.405])
    sens_df.to_csv(out_dir / "piecewise_threshold_sensitivity.csv", index=False)
    print("-> Exported piecewise_threshold_sensitivity.csv (tau=7.648 vs tau=9.405)")
    
    pw_res = multivariate_piecewise(df)
    pw_df = pd.DataFrame([{
        "tau": pw_res["tau"],
        "slope_below_b1": pw_res["slope_below"],
        "se_below": pw_res["se_below"],
        "p_below": pw_res["p_below"],
        "slope_change_b2": pw_res["slope_change"],
        "se_change": pw_res["se_change"],
        "p_change": pw_res["p_change"],
        "slope_above": pw_res["slope_above"],
        "se_above": pw_res["se_above"],
        "p_above": pw_res["p_above"],
        "aic": pw_res["aic"],
        "bic": pw_res["bic"],
        "rsquared": pw_res["rsquared"],
        "n_obs": pw_res["n_obs"],
        "n_countries": pw_res["n_countries"],
    }])
    pw_df.to_csv(out_dir / "multivariate_piecewise.csv", index=False)
    
    print("-> Running Block Bootstrap (1,000 reps by country)...")
    boot_res = block_bootstrap_tau(df, n_reps=1000, seed=42)
    boot_df = pd.DataFrame({
        "tau_bootstrap_samples": boot_res["all_taus"]
    })
    boot_df.to_csv(out_dir / "breakpoint_block_bootstrap_samples.csv", index=False)
    boot_summary = pd.DataFrame([{
        "n_reps": boot_res["n_reps"],
        "tau_median": boot_res["tau_median"],
        "ci_lower_95": boot_res["ci_lower_95"],
        "ci_upper_95": boot_res["ci_upper_95"],
    }])
    boot_summary.to_csv(out_dir / "breakpoint_block_bootstrap_summary.csv", index=False)
    
    print("-> Running Yearly Piecewise Stability (2006-2023)...")
    yearly_df, n_sig, total_yrs = yearly_piecewise_significance(df)
    yearly_df.to_csv(out_dir / "yearly_piecewise_stability.csv", index=False)
    print(f"-> Exported piecewise results. Significant years: {n_sig}/{total_yrs}")
    
    # ------------------------------------------------------------- 3. Leak-Free Machine Learning Validation
    print("\n[3/6] Running Leak-Free Validation Benchmarks...")
    val_res = evaluate_leak_free_models(df, n_splits=5, seed=42)
    val_res["summary_table"].to_csv(out_dir / "validation_leak_free_benchmarks.csv", index=False)
    
    ftest_res = nested_lagged_model_ftest(df)
    ftest_res["summary_table"].to_csv(out_dir / "nested_lagged_model_ftest.csv", index=False)
    print(f"-> Exported validation_leak_free_benchmarks.csv and nested_lagged_model_ftest.csv (F={ftest_res['f_stat']:.4f}, p={ftest_res['p_value']:.2e})")
    
    # ------------------------------------------------------------- 4. Affect Models (Kahneman & Deaton)
    print("\n[4/6] Running Fully-Standardized Affect Models...")
    aff_res = run_affect_models(df)
    aff_res["summary_table"].to_csv(out_dir / "affect_standardized_comparison.csv", index=False)
    print("-> Exported affect_standardized_comparison.csv")
    
    # ------------------------------------------------------------- 5. Country Residuals & ANOVA
    print("\n[5/6] Running Residual & Fixed Effects Analysis...")
    resid_res = analyze_residuals(df, min_obs=8)
    resid_res["top_15_overperformers"].to_csv(out_dir / "top_15_overperformers.csv")
    resid_res["top_15_underperformers"].to_csv(out_dir / "top_15_underperformers.csv")
    resid_res["regional_table"].to_csv(out_dir / "regional_residual_effects.csv", index=False)
    pd.DataFrame({"excluded_country": resid_res["excluded_countries"]}).to_csv(out_dir / "excluded_countries_under_8_obs.csv", index=False)
    
    resid_summary = pd.DataFrame([{
        "regional_anova_f": resid_res["regional_anova_f"],
        "regional_anova_p": resid_res["regional_anova_p"],
        "regional_anova_f_raw": resid_res["regional_anova_f_raw"],
        "regional_anova_p_raw": resid_res["regional_anova_p_raw"],
        "persistence_autocorr": resid_res["persistence_autocorr"],
        "total_countries": resid_res["total_countries"],
        "n_countries_analyzed": resid_res["n_countries"],
        "n_excluded_countries": resid_res["n_excluded_countries"],
        "n_obs": resid_res["n_obs"],
    }])
    resid_summary.to_csv(out_dir / "residual_diagnostics_summary.csv", index=False)
    print(f"-> Exported residual diagnostics: {resid_res['n_countries']} countries retained, {resid_res['n_excluded_countries']} excluded (<8 obs).")
    
    # ------------------------------------------------------------- 6. Relative Income & Social Comparison
    print("\n[6/6] Running Relative Income & Social Comparison Models...")
    rel_res = evaluate_relative_income(df)
    rel_res["summary_table"].to_csv(out_dir / "relative_income_social_comparison.csv", index=False)
    rel_res["vif_table"].to_csv(out_dir / "relative_income_vif.csv", index=False)
    print("-> Exported relative_income_social_comparison.csv and relative_income_vif.csv")
    
    # ------------------------------------------------------------- Figures Generation
    print("\nGenerating Publication Figures across (.png, .pdf, .svg, .eps)...")
    
    # Figure 1: Panel Model Driver Coefficients (Pooled vs Between vs Within FE)
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    x_idx = np.arange(len(FACTOR_COLS))
    width = 0.25
    ax1.bar(x_idx - width, comp_df["pooled beta"], width=width, label="Pooled OLS", color="#4e79a7")
    ax1.bar(x_idx, comp_df["between beta"], width=width, label="Between Estimator", color="#f28e2b")
    ax1.bar(x_idx + width, comp_df["within beta"], width=width, yerr=comp_df["clustered SE"], capsize=4, label="Within FE (Two-Way)", color="#59a14f")
    ax1.axhline(0, color="#888888", linestyle="--", linewidth=0.8)
    ax1.set_xticks(x_idx)
    ax1.set_xticklabels([FACTORS[f] for f in FACTOR_COLS], rotation=25, ha="right")
    ax1.set_ylabel("Unstandardized Coefficient")
    ax1.set_title("Driver Coefficients Across Panel Estimators (with Entity-Clustered SE)")
    ax1.legend()
    save_figure_multi_format(fig1, fig_dir / "fig1_panel_estimator_comparison")
    
    # Figure 2: Multivariate Piecewise Threshold and Bootstrap Distribution
    fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(12, 5))
    ax2a.hist(boot_res["all_taus"], bins=25, color="#76b7b2", edgecolor="white", density=True)
    ax2a.axvline(pw_res["tau"], color="#e15759", linestyle="-", linewidth=2, label=f"Point Estimate tau={pw_res['tau']:.2f}")
    ax2a.axvline(boot_res["ci_lower_95"], color="#4e79a7", linestyle="--", label=f"95% CI [{boot_res['ci_lower_95']:.2f}, {boot_res['ci_upper_95']:.2f}]")
    ax2a.axvline(boot_res["ci_upper_95"], color="#4e79a7", linestyle="--")
    ax2a.set_xlabel("Breakpoint tau (Log GDP)")
    ax2a.set_ylabel("Bootstrap Density")
    ax2a.set_title("Block Bootstrap Distribution of tau (1,000 Resamples)")
    ax2a.legend()
    
    ax2b.plot(yearly_df["year"], yearly_df["p_value_beta2"], marker="o", color="#b07aa1", linewidth=1.5)
    ax2b.axhline(0.05, color="#e15759", linestyle="--", label="alpha = 0.05")
    ax2b.set_xlabel("Year")
    ax2b.set_ylabel("p-value for Slope Change (beta2)")
    ax2b.set_title(f"Yearly Piecewise Significance (14/18 Years Significant)")
    ax2b.legend()
    save_figure_multi_format(fig2, fig_dir / "fig2_breakpoint_bootstrap_and_stability")
    
    # Figure 3: Leak-Free Validation Benchmarks
    fig3, ax3 = plt.subplots(figsize=(11, 5.5))
    val_table = val_res["summary_table"]
    labels = [f"{row['Model'].replace(' (contemporaneous)', '').replace(' (has access to lagged outcome)', '').replace(' (with lagged outcome)', ' + Lag')}\n({row['Protocol'].split()[0]})" for _, row in val_table.iterrows()]
    r2_vals = val_table["R2"].values
    bar_colors = ["#4e79a7", "#59a14f", "#e15759", "#76b7b2", "#edc948", "#b07aa1", "#ff9da7"][:len(val_table)]
    bars = ax3.bar(labels, r2_vals, color=bar_colors)
    ax3.axhline(0.8663, color="#888888", linestyle=":", label="Old Leaking RF R2 (0.866)")
    for b in bars:
        height = b.get_height()
        ax3.annotate(f"{height:.3f}", xy=(b.get_x() + b.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8)
    ax3.set_ylabel("Test R-squared")
    ax3.set_title("Predictive Performance Under Leak-Free Validation Protocols (with Lagged Outcome Benchmarks)")
    ax3.set_ylim(0, 1.05)
    ax3.tick_params(axis="x", rotation=15)
    ax3.legend()
    save_figure_multi_format(fig3, fig_dir / "fig3_leak_free_model_benchmarks")
    
    # Figure 4: Affect Model Comparison (Bivariate vs Conditional)
    fig4, ax4 = plt.subplots(figsize=(9, 5))
    aff_tab = aff_res["summary_table"]
    x = np.arange(len(aff_tab))
    width = 0.35
    
    bars1 = ax4.bar(x - width/2, aff_tab["Bivariate_Beta"], width=width, yerr=aff_tab["Bivariate_SE"],
                    capsize=4, color="#4e79a7", label="Bivariate (Unconditional)")
    bars2 = ax4.bar(x + width/2, aff_tab["Fully_Standardized_Log_GDP_Beta"], width=width, yerr=aff_tab["SE"],
                    capsize=4, color="#e15759", label="Conditional (Controlling for 5 Non-Income Drivers)")
    
    ax4.axhline(0, color="#888888", linestyle="--", linewidth=0.8)
    ax4.set_xticks(x)
    ax4.set_xticklabels(aff_tab["Outcome"])
    ax4.set_ylabel("Standardized Log GDP Beta (SD / SD)")
    ax4.set_title("Life Evaluation vs. Emotional Affect: Bivariate vs. Conditional Slopes")
    ax4.legend(loc="upper right")
    
    for b in list(bars1) + list(bars2):
        h = b.get_height()
        offset = 4 if h >= 0 else -14
        ax4.annotate(f"{h:+.2f}", xy=(b.get_x() + b.get_width() / 2, h),
                     xytext=(0, offset), textcoords="offset points", ha="center", fontsize=8)
                     
    save_figure_multi_format(fig4, fig_dir / "fig4_affect_standardized_comparison")
    
    # Figure 5: Regional Residual Country Effects
    fig5, ax5 = plt.subplots(figsize=(9, 5))
    reg_tab = resid_res["regional_table"]
    y_pos = np.arange(len(reg_tab))
    ax5.errorbar(reg_tab["mean"], y_pos, xerr=reg_tab["ci95_margin"], fmt="o", color="#4e79a7", ecolor="#e15759", elinewidth=2, capsize=4)
    ax5.axvline(0, color="#888888", linestyle="--", linewidth=0.8)
    ax5.set_yticks(y_pos)
    ax5.set_yticklabels(reg_tab["region"])
    ax5.set_xlabel("Mean Country Fixed Effect (Deviation from Global Mean)")
    ax5.set_title(f"Regional Country Fixed Effects (ANOVA F={resid_res['regional_anova_f']:.2f}, p={resid_res['regional_anova_p']:.2e})")
    save_figure_multi_format(fig5, fig_dir / "fig5_regional_fixed_effects_ci")
    
    print("\nAll analyses executed and all figures saved successfully!")


if __name__ == "__main__":
    main()

