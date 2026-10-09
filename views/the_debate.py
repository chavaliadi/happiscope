import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
import streamlit as st

from common import TARGET, load_data

GDP_COL = "Log GDP per capita"


@st.cache_data
def _fit_linear_model(x_vals: np.ndarray, y_vals: np.ndarray):
    """Fit simple OLS: Life Ladder ~ Log GDP per capita."""
    X_mat = sm.add_constant(x_vals)
    m = sm.OLS(y_vals, X_mat).fit()
    return {
        "model": m,
        "intercept": float(m.params[0]),
        "slope": float(m.params[1]),
        "p_value_slope": float(m.pvalues[1]),
        "r2": float(m.rsquared),
        "aic": float(m.aic),
        "bic": float(m.bic),
        "rss": float(m.ssr),
        "n": len(y_vals),
    }


@st.cache_data
def _find_optimal_breakpoint(x_vals: np.ndarray, y_vals: np.ndarray):
    """Grid search over 10th to 90th percentiles to find tau minimizing AIC."""
    q10, q90 = np.percentile(x_vals, 10), np.percentile(x_vals, 90)
    candidates = np.linspace(q10, q90, 80)
    best_tau = float(candidates[0])
    best_aic = float("inf")

    for tau in candidates:
        hinge = np.maximum(0, x_vals - tau)
        X_mat = np.column_stack([np.ones_like(x_vals), x_vals, hinge])
        m = sm.OLS(y_vals, X_mat).fit()
        if m.aic < best_aic:
            best_aic = float(m.aic)
            best_tau = float(tau)

    return best_tau


@st.cache_data
def _fit_piecewise_model(x_vals: np.ndarray, y_vals: np.ndarray, tau: float):
    """Fit continuous piecewise OLS: y = beta0 + beta1*x + beta2*max(0, x - tau)."""
    hinge = np.maximum(0, x_vals - tau)
    X_mat = np.column_stack([np.ones_like(x_vals), x_vals, hinge])
    m = sm.OLS(y_vals, X_mat).fit()

    beta0 = float(m.params[0])
    beta1 = float(m.params[1])
    beta2 = float(m.params[2])
    p_val_change = float(m.pvalues[2])
    slope_below = beta1
    slope_above = beta1 + beta2

    return {
        "model": m,
        "tau": float(tau),
        "beta0": beta0,
        "beta1": beta1,
        "beta2": beta2,
        "slope_below": slope_below,
        "slope_above": slope_above,
        "p_value_change": p_val_change,
        "r2": float(m.rsquared),
        "aic": float(m.aic),
        "bic": float(m.bic),
        "rss": float(m.ssr),
        "n": len(y_vals),
    }


def render():
    df = load_data()

    st.title("The Debate: Does Income Plateau?")
    st.markdown(
        "**Does national wealth continue to lift life satisfaction indefinitely, or does happiness plateau after basic and moderate needs are met?** "
        "This section investigates the central debate in well-being economics by comparing a standard linear regression against an empirical "
        "piecewise (segmented) regression model."
    )

    with st.expander("Methodology & Mathematical Specifications"):
        st.markdown(
            "- **Predictor ($X$):** `Log GDP per capita` (log-transformed GDP per capita from the World Happiness Report).\n"
            "- **Target ($Y$):** `Life Ladder` (national subjective well-being on a 0–10 Cantril ladder).\n"
            "- **Linear Baseline:** $Y = \\beta_0 + \\beta_1 X + \\epsilon$.\n"
            "- **Continuous Piecewise (Segmented) Model:**\n"
            "  $$Y = \\beta_0 + \\beta_1 X + \\beta_2 \\max(0, X - \\tau) + \\epsilon$$\n"
            "  - Below breakpoint ($\\le \\tau$): Slope $= \\beta_1$\n"
            "  - Above breakpoint ($> \\tau$): Slope $= \\beta_1 + \\beta_2$\n"
            "  - Continuity constraint: The two line segments join continuously at breakpoint $\\tau$.\n"
            "- **Grid Search Criterion:** The optimal empirical breakpoint $\\tau^*$ is selected from 80 candidate thresholds spanning the "
            "10th to 90th percentiles of Log GDP by minimizing the Akaike Information Criterion (AIC).\n"
            "- **Dollar Context Note:** For real-world intuition, Log GDP values can be exponentiated ($\\exp(X)$). This is an approximate "
            "mathematical conversion to raw purchasing-power GDP, not a definitive standalone pricing index."
        )

    # ------------------------------------------------------------- Controls
    st.subheader("1. Sample & Threshold Configuration")
    c1, c2 = st.columns([1, 1])

    with c1:
        sample_choice = st.radio(
            "Dataset Scope",
            ["Full Pooled Panel (2005–2023)", "Latest Survey Year (2023)"],
            index=0,
            key="td_sample_choice",
            help="Full pooled panel increases statistical power; single year isolates cross-sectional comparisons.",
        )

    if sample_choice == "Latest Survey Year (2023)":
        d_sub = df[(df["year"] == 2023) & df[[TARGET, GDP_COL]].notna().all(axis=1)].copy()
    else:
        d_sub = df[df[[TARGET, GDP_COL]].notna().all(axis=1)].copy()

    if len(d_sub) < 30:
        st.error("Insufficient complete data points to fit regression models.")
        return

    x_data = d_sub[GDP_COL].values
    y_data = d_sub[TARGET].values

    # Fit linear baseline
    lin_res = _fit_linear_model(x_data, y_data)
    optimal_tau = _find_optimal_breakpoint(x_data, y_data)

    min_x, max_x = float(np.min(x_data)), float(np.max(x_data))

    with c2:
        tau_mode = st.radio(
            "Breakpoint Mode",
            [f"Optimal Data-Estimated Breakpoint (tau = {optimal_tau:.2f})", "Custom User-Selected Breakpoint"],
            index=0,
            key="td_tau_mode",
            help="Choose between empirical minimum-AIC grid search result or interactive slider.",
        )

    if "Custom" in tau_mode:
        selected_tau = st.slider(
            "Select Custom Breakpoint (tau)",
            min_value=round(min_x + 0.5, 2),
            max_value=round(max_x - 0.5, 2),
            value=round(optimal_tau, 2),
            step=0.05,
            key="td_custom_tau",
            help="Adjust the income threshold where the piecewise slope shifts.",
        )
    else:
        selected_tau = optimal_tau

    pw_res = _fit_piecewise_model(x_data, y_data, selected_tau)
    approx_dollar = np.exp(selected_tau)

    # ------------------------------------------------------------- Key Metrics
    st.subheader("2. Model & Slope Estimates")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Breakpoint (tau)", f"{selected_tau:.2f}", f"~${approx_dollar:,.0f} GDP/cap")
    k2.metric("Slope Below tau", f"{pw_res['slope_below']:+.3f}", help="Gain in happiness score per 1-unit increase in Log GDP below the breakpoint.")
    k3.metric("Slope Above tau", f"{pw_res['slope_above']:+.3f}", help="Gain in happiness score per 1-unit increase in Log GDP above the breakpoint.")
    delta_r2 = pw_res["r2"] - lin_res["r2"]
    k4.metric("Piecewise R² vs Linear", f"{pw_res['r2']:.3f}", f"{delta_r2:+.3f} ΔR²")

    # ------------------------------------------------------------- Visualization
    st.subheader("3. Regression Visualization: Linear vs Piecewise Fit")

    # Generate smooth prediction curves
    x_grid = np.linspace(min_x, max_x, 200)
    y_lin_pred = lin_res["intercept"] + lin_res["slope"] * x_grid
    y_pw_pred = pw_res["beta0"] + pw_res["beta1"] * x_grid + pw_res["beta2"] * np.maximum(0, x_grid - selected_tau)

    # Scatter plot of countries
    d_sub["approx_gdp"] = np.exp(d_sub[GDP_COL])
    fig = px.scatter(
        d_sub,
        x=GDP_COL,
        y=TARGET,
        color="region" if "region" in d_sub.columns else None,
        hover_name="Country name",
        hover_data={"year": True, TARGET: ":.2f", GDP_COL: ":.2f", "approx_gdp": ":$,.0f"},
        opacity=0.6,
        title=f"Life Ladder vs Log GDP per capita ({sample_choice})",
        labels={GDP_COL: "Log GDP per capita", TARGET: "Happiness Score (Life Ladder)", "approx_gdp": "Approx GDP ($)"},
    )

    # Add Linear Fit line
    fig.add_trace(go.Scatter(
        x=x_grid, y=y_lin_pred,
        mode="lines", name="Linear OLS Fit",
        line=dict(color="#1f77b4", width=2.5, dash="dash"),
    ))

    # Add Piecewise Fit line
    fig.add_trace(go.Scatter(
        x=x_grid, y=y_pw_pred,
        mode="lines", name=f"Piecewise Fit (tau={selected_tau:.2f})",
        line=dict(color="#d62728", width=3.5),
    ))

    # Vertical threshold line
    fig.add_vline(
        x=selected_tau, line_dash="dot", line_color="#333",
        annotation_text=f"Breakpoint tau={selected_tau:.2f} (~${approx_dollar:,.0f})",
        annotation_position="top left",
    )

    fig.update_layout(height=520, margin=dict(l=0, r=0, t=50, b=0), legend=dict(yanchor="bottom", y=0.02, xanchor="right", x=0.98))
    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------------------------------------- Comparative Metrics Table
    st.subheader("4. Statistical Comparison Table")
    comp_df = pd.DataFrame({
        "Metric": ["Sample Size (N)", "R-squared", "Residual Sum of Squares (RSS)", "AIC", "BIC", "Slope Below tau (beta1)", "Slope Above tau (beta1 + beta2)", "Slope Change (beta2)", "p-value for Slope Change"],
        "Linear OLS": [
            f"{lin_res['n']:,}",
            f"{lin_res['r2']:.4f}",
            f"{lin_res['rss']:.2f}",
            f"{lin_res['aic']:.1f}",
            f"{lin_res['bic']:.1f}",
            f"{lin_res['slope']:.4f}",
            "—",
            "—",
            "—",
        ],
        "Piecewise OLS": [
            f"{pw_res['n']:,}",
            f"{pw_res['r2']:.4f}",
            f"{pw_res['rss']:.2f}",
            f"{pw_res['aic']:.1f}",
            f"{pw_res['bic']:.1f}",
            f"{pw_res['slope_below']:.4f}",
            f"{pw_res['slope_above']:.4f}",
            f"{pw_res['beta2']:+.4f}",
            f"{pw_res['p_value_change']:.2e}",
        ],
    })
    st.dataframe(comp_df, hide_index=True, use_container_width=True)

    # ------------------------------------------------------------- Plateau Interpretation
    st.subheader("5. Statistical Verdict & Interpretation")
    slope_above = pw_res["slope_above"]
    beta2 = pw_res["beta2"]
    p_change = pw_res["p_value_change"]

    if slope_above <= 0.05 and p_change < 0.05:
        verdict_msg = (
            fr"**Evidence consistent with an income plateau:** Above the breakpoint $\tau = {selected_tau:.2f}$, "
            f"the estimated slope drops to **{slope_above:.3f}** (statistically indistinguishable from zero or very flat). "
            f"In this subset, additional income past approximately **${approx_dollar:,.0f}** does not yield significant additional happiness."
        )
        st.info(verdict_msg)
    elif slope_above > 0.05:
        verdict_msg = (
            fr"**Evidence consistent with NO income plateau:** Above the breakpoint $\tau = {selected_tau:.2f}$, "
            f"the slope remains substantially positive at **{slope_above:.3f}** (gain per unit log GDP). "
            f"In this dataset, higher national income continues to be strongly associated with higher life satisfaction, "
            f"even among high-income countries exceeding **${approx_dollar:,.0f}**."
        )
        st.success(verdict_msg)
    else:
        st.warning("The slope shift does not reach conclusive statistical significance.")

    st.markdown(
        "> **Data Result vs Academic Interpretation:** This empirical finding reflects association in cross-national panel data. "
        "A non-zero slope does not prove that money directly causes life satisfaction; wealthy nations typically enjoy superior "
        "healthcare, institutional quality, social safety nets, and civil liberties, which are correlated with GDP."
    )

    # ------------------------------------------------------------- Academic Context Expander
    with st.expander("Academic Context: Four Decades of the Income-Happiness Debate"):
        st.markdown(
            "#### 1. The Easterlin Paradox (Easterlin, 1974)\n"
            "Richard Easterlin observed that while wealthy individuals within a country are consistently happier than poorer individuals at any given time, "
            "long-term economic growth over decades in developed nations (such as post-WWII US and Japan) did not produce a corresponding rise in average national happiness. "
            "Easterlin attributed this to **hedonic adaptation** (hedonic treadmill) and **relative social comparison**.\n\n"
            "#### 2. Stevenson & Wolfers (2008): Re-evaluating the Paradox\n"
            "Betsey Stevenson and Justin Wolfers analyzed international datasets (including Gallup World Poll and World Values Survey) across 130+ nations. "
            "They concluded there is **no satiation point** at the national level: the relationship between subjective well-being and log income is remarkably linear and positive, "
            "with comparable slopes in poor and rich countries alike.\n\n"
            "#### 3. Kahneman & Deaton (2010): Emotional Well-Being vs Life Evaluation\n"
            "Nobel laureates Daniel Kahneman and Angus Deaton famously distinguished two aspects of subjective well-being among 450,000 US residents:\n"
            "- **Emotional well-being** (day-to-day emotional experiences such as joy, sadness, stress): Plateaus at approximately **$75,000** annually, with no further gains above this threshold.\n"
            "- **Life evaluation** (Cantril Ladder / Life Ladder): Does **not** plateau; continues to rise log-linearly with income.\n"
            "Because the World Happiness Report primarily measures the *Life Ladder* (evaluative satisfaction), international WHR data generally reflects continued positive associations.\n\n"
            "#### 4. Killingsworth (2021) & Kahneman-Killingsworth-Mellers (2023) Adversarial Collaboration\n"
            "Using smartphone experience sampling across 33,000+ US workers, Matthew Killingsworth found that experienced well-being continues to rise well past $75,000. "
            "In an adversarial collaboration published in 2023, Kahneman and Killingsworth reconciled their findings: happiness rises steadily with income for the majority of people, "
            "while a plateau occurs only for an already-unhappy minority whose suffering (e.g. chronic illness, grief) is not mitigated by additional wealth."
        )
