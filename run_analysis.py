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
from analysis.panel_models import comparison_table, mundlak
from analysis.breakpoint import (
    multivariate_piecewise,
    block_bootstrap_tau,
    yearly_piecewise_significance,
)
from analysis.validation import evaluate_leak_free_models
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
    comp_df, gdp_ratio, dw_dict = comparison_table(df)
    comp_df.to_csv(out_dir / "panel_models_comparison.csv", index=False)
    
    mundlak_res = mundlak(df)
    mundlak_summary = pd.DataFrame([{
        "wald_statistic": mundlak_res["wald_statistic"],
        "wald_pvalue": mundlak_res["wald_pvalue"],
        "n_obs": mundlak_res["n_obs"],
        "n_countries": mundlak_res["n_countries"],
        "durbin_watson_pooled": dw_dict["Pooled OLS"],
        "durbin_watson_between": dw_dict["Between Estimator"],
        "durbin_watson_within_fe": dw_dict["Within FE"],
        "easterlin_gdp_between_to_within_ratio": gdp_ratio,
    }])
    mundlak_summary.to_csv(out_dir / "mundlak_specification.csv", index=False)
    print(f"-> Exported panel_models_comparison.csv and mundlak_specification.csv (Ratio={gdp_ratio:.4f})")
    
    # ------------------------------------------------------------- 2. Multivariate Piecewise & Bootstrap
    print("\n[2/6] Running Multivariate Piecewise Regression & Bootstrap...")
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
    print("-> Exported validation_leak_free_benchmarks.csv")
    
    # ------------------------------------------------------------- 4. Affect Models (Kahneman & Deaton)
    print("\n[4/6] Running Fully-Standardized Affect Models...")
    aff_res = run_affect_models(df)
    aff_res["summary_table"].to_csv(out_dir / "affect_standardized_comparison.csv", index=False)
    print("-> Exported affect_standardized_comparison.csv")
    
    # ------------------------------------------------------------- 5. Country Residuals & ANOVA
    print("\n[5/6] Running Residual & Fixed Effects Analysis...")
    resid_res = analyze_residuals(df)
    resid_res["top_15_overperformers"].to_csv(out_dir / "top_15_overperformers.csv")
    resid_res["top_15_underperformers"].to_csv(out_dir / "top_15_underperformers.csv")
    resid_res["regional_table"].to_csv(out_dir / "regional_residual_effects.csv", index=False)
    
    resid_summary = pd.DataFrame([{
        "regional_anova_f": resid_res["regional_anova_f"],
        "regional_anova_p": resid_res["regional_anova_p"],
        "persistence_autocorr": resid_res["persistence_autocorr"],
        "n_countries": resid_res["n_countries"],
        "n_obs": resid_res["n_obs"],
    }])
    resid_summary.to_csv(out_dir / "residual_diagnostics_summary.csv", index=False)
    print("-> Exported residual diagnostics and top/bottom performers.")
    
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
    fig3, ax3 = plt.subplots(figsize=(9, 5))
    val_table = val_res["summary_table"]
    labels = [f"{row['Model']}\n({row['Protocol'].split()[0]})" for _, row in val_table.iterrows()]
    r2_vals = val_table["R2"].values
    bars = ax3.bar(labels, r2_vals, color=["#4e79a7", "#59a14f", "#e15759", "#4e79a7", "#59a14f"])
    ax3.axhline(0.8663, color="#888888", linestyle=":", label="Old Leaking RF R2 (0.866)")
    for b in bars:
        height = b.get_height()
        ax3.annotate(f"{height:.3f}", xy=(b.get_x() + b.get_width() / 2, height),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom")
    ax3.set_ylabel("Test R-squared")
    ax3.set_title("Predictive Performance Under Leak-Free Validation Protocols")
    ax3.set_ylim(0, 1.0)
    ax3.legend()
    save_figure_multi_format(fig3, fig_dir / "fig3_leak_free_model_benchmarks")
    
    # Figure 4: Affect Model Comparison
    fig4, ax4 = plt.subplots(figsize=(8, 5))
    aff_tab = aff_res["summary_table"]
    x = np.arange(len(aff_tab))
    bars = ax4.bar(x, aff_tab["Fully_Standardized_Log_GDP_Beta"], yerr=aff_tab["SE"], capsize=4, color=["#4e79a7", "#76b7b2", "#f28e2b"])
    ax4.axhline(0, color="#888888", linestyle="--")
    ax4.set_xticks(x)
    ax4.set_xticklabels(aff_tab["Outcome"])
    ax4.set_ylabel("Standardized Log GDP Beta (SD / SD)")
    ax4.set_title("Income Predicts Life Evaluation, Not Day-to-Day Affect (Kahneman & Deaton)")
    for b, r2 in zip(bars, aff_tab["R_squared"]):
        h = b.get_height()
        offset = 5 if h >= 0 else -15
        ax4.annotate(f"R2={r2:.3f}", xy=(b.get_x() + b.get_width() / 2, h),
                     xytext=(0, offset), textcoords="offset points", ha="center")
    save_figure_multi_format(fig4, fig_dir / "fig4_affect_standardized_comparison")
    
    # Figure 5: Regional Residual Country Effects
    fig5, ax5 = plt.subplots(figsize=(9, 5))
    reg_tab = resid_res["regional_table"]
    y_pos = np.arange(len(reg_tab))
    ax5.errorbar(reg_tab["mean"], y_pos, xerr=reg_tab["ci95_margin"], fmt="o", color="#4e79a7", ecolor="#e15759", elinewidth=2, capsize=4)
    ax5.set_yticks(y_pos)
    ax5.set_yticklabels(reg_tab["region"])
    ax5.set_xlabel("Mean Country Fixed Effect (Baseline Well-Being vs 6 Factors)")
    ax5.set_title(f"Regional Differences in Baseline Well-Being (ANOVA F={resid_res['regional_anova_f']:.2f}, p={resid_res['regional_anova_p']:.2e})")
    save_figure_multi_format(fig5, fig_dir / "fig5_regional_fixed_effects_ci")
    
    print("\nAll analyses executed and all figures saved successfully!")


if __name__ == "__main__":
    main()

