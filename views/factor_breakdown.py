import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import spearmanr

from common import (
    FACTOR_COLS, FACTORS, MIN_COMPLETE_YEAR, MIN_REGION_OBS, TARGET,
    complete_cases, global_model, global_standardized, load_data, load_importance,
    pooled_period, region_results, yearly_coefs,
)

GREEN, RED = "#2e9e5b", "#d64545"


def render():
    df = load_data()
    st.title("Factor Breakdown")
    st.caption("Which factors drive happiness scores, how much, and has that changed over time?")

    t1, t2, t3, t4 = st.tabs(["Country breakdown", "What drives happiness (global)",
                              "How drivers shifted", "By region"])
    with t1:
        _country_tab(df)
    with t2:
        _global_tab(df)
    with t3:
        _shift_tab(df)
    with t4:
        _region_tab(df)

    with st.expander("Method notes"):
        st.markdown(
            f"- **Data:** World Happiness Report panel, {df['Country name'].nunique()} countries, "
            f"{int(df['year'].min())}-{int(df['year'].max())}. Only rows with all six factors present are used in regressions.\n"
            "- **Model:** ordinary least squares (OLS) of the happiness score (Life Ladder) on the six WHR factors. "
            "This mirrors the WHR's own regression-based approach and gives coefficients we can interpret.\n"
            "- **Fair comparison:** the six factors are on different scales (GDP is logged, life expectancy is in years, "
            "the rest run 0-1), so raw coefficients can't be ranked against each other. "
            "We standardize (z-score) the factors before comparing importance.\n"
            "- **Cross-check:** a Random Forest, scored with permutation importance on a held-out 20% test set.\n"
            f"- **Guards:** single-year regressions need at least {MIN_COMPLETE_YEAR} complete countries "
            f"(2005 has only 1, so it's excluded); regional regressions need at least {MIN_REGION_OBS} rows.\n"
            "- **Limits:** the analysis shows association, not causation, and the set of countries surveyed changes from year to year."
        )


# --------------------------------------------------------------- tab 1
def _country_tab(df: pd.DataFrame):
    table, _, _ = global_model(df)
    coefs = table.loc[FACTOR_COLS, "coefficient"]

    c1, c2 = st.columns([2, 1])
    country = c1.selectbox("Country", sorted(df["Country name"].unique()),
                           index=sorted(df["Country name"].unique()).index("India"))
    cdf = df[df["Country name"] == country]
    years = sorted(cdf.loc[cdf[FACTOR_COLS + [TARGET]].notna().all(axis=1), "year"].astype(int))
    if not years:
        st.warning(f"{country} doesn't have a year with all six factors, so it can't be broken down.")
        return
    year = c2.selectbox("Year", years, index=len(years) - 1)

    row = cdf[cdf["year"] == year].iloc[0]
    world = complete_cases(df[df["year"] == year])
    world_avg_score = world[TARGET].mean()

    # explained gap vs the world average for that year: coefficient x (country value - world average)
    contrib = {FACTORS[c]: coefs[c] * (row[c] - world[c].mean()) for c in FACTOR_COLS}
    explained = sum(contrib.values())
    actual_gap = row[TARGET] - world_avg_score
    contrib["Not explained by these six"] = actual_gap - explained

    m1, m2, m3 = st.columns(3)
    m1.metric(f"{country} score ({year})", f"{row[TARGET]:.2f}")
    m2.metric(f"World average ({year})", f"{world_avg_score:.2f}")
    m3.metric("Gap vs world", f"{actual_gap:+.2f}")

    labels, values = list(contrib), list(contrib.values())
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker_color=[GREEN if v >= 0 else RED for v in values],
        text=[f"{v:+.2f}" for v in values], textposition="outside",
    ))
    fig.update_layout(
        title=f"Why {country}'s score is {'above' if actual_gap >= 0 else 'below'} the world average in {year}",
        xaxis_title="Points of happiness score (vs world average)", yaxis=dict(autorange="reversed"),
        height=380, margin=dict(l=0, r=30, t=50, b=0),
    )
    fig.add_vline(x=0, line_color="#888")
    st.plotly_chart(fig, width="stretch")
    st.caption("Each bar = (global regression coefficient) x (how far the country is from the world average on that factor). "
               "Green pushes the score up, red pulls it down.")

    trend = df[df[TARGET].notna()].groupby("year")[TARGET].mean().rename("World average")
    line = pd.concat([cdf.set_index("year")[TARGET].rename(country), trend], axis=1).dropna(how="all").reset_index()
    fig2 = px.line(line.melt("year", var_name="Series", value_name="Score"), x="year", y="Score",
                   color="Series", markers=True, title=f"{country} over time vs world average")
    fig2.update_layout(height=320, margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(fig2, width="stretch")


# --------------------------------------------------------------- tab 2
def _global_tab(df: pd.DataFrame):
    table, r2, n = global_model(df)
    imp = load_importance()
    rf_r2 = float(imp["rf_test_r2"].iloc[0])

    a, b, c = st.columns(3)
    a.metric("Regression R-squared", f"{r2:.3f}", help="Share of the variation in happiness scores explained by the six factors.")
    b.metric("Country-year observations", f"{n:,}")
    c.metric("Random Forest test R-squared", f"{rf_r2:.3f}", help="Scored on 20% of data the model never saw.")

    std = global_standardized(df)
    order = std.abs().sort_values(ascending=False).index
    fig = go.Figure(go.Bar(
        x=[std[k] for k in order], y=[FACTORS[k] for k in order], orientation="h",
        marker_color=[GREEN if std[k] >= 0 else RED for k in order],
        text=[f"{std[k]:+.2f}" for k in order], textposition="outside",
    ))
    fig.update_layout(title="How much each factor matters (standardized coefficients)",
                      xaxis_title="Change in happiness score for a 1-standard-deviation increase in the factor",
                      yaxis=dict(autorange="reversed"), height=360, margin=dict(l=0, r=30, t=50, b=0))
    fig.add_vline(x=0, line_color="#888")
    st.plotly_chart(fig, width="stretch")

    st.subheader("Do two very different models agree?")
    cmp_ = imp.set_index("factor")
    cmp_["OLS rank"] = cmp_["standardized_ols"].abs().rank(ascending=False).astype(int)
    cmp_["RF rank"] = cmp_["rf_permutation"].rank(ascending=False).astype(int)
    rho, p = spearmanr(cmp_["OLS rank"], cmp_["RF rank"])
    view = cmp_.rename(index=FACTORS)[["standardized_ols", "OLS rank", "rf_permutation", "RF rank"]]
    view.columns = ["Standardized OLS coef.", "OLS rank", "RF permutation importance", "RF rank"]
    st.dataframe(view.sort_values("OLS rank").style.format(
        {"Standardized OLS coef.": "{:+.3f}", "RF permutation importance": "{:.3f}"}), width="stretch")
    st.success(f"Rank agreement (Spearman) = **{rho:.2f}** (p = {p:.3f}). A linear model and a non-linear model, "
               "measured fairly, largely agree on which factors matter most.")

    with st.expander("Why we standardize (and what the raw coefficients look like)"):
        st.write("Raw coefficients depend on each factor's units. Life expectancy is measured in years, so its raw coefficient "
                 "looks tiny (about 0.03) even though it matters; social support runs 0-1, so its raw coefficient looks huge. "
                 "Ranking raw coefficients would be misleading. Standardizing puts every factor on the same footing.")
        raw = table.rename(index={**FACTORS, "const": "Intercept"})
        st.dataframe(raw.style.format({"coefficient": "{:+.3f}", "p_value": "{:.2e}"}), width="stretch")


# --------------------------------------------------------------- tab 3
def _shift_tab(df: pd.DataFrame):
    st.markdown("#### Year by year")
    yc = yearly_coefs(df)
    st.caption(f"One regression per year, using years with at least {MIN_COMPLETE_YEAR} complete countries "
               f"({yc.index.min()}-{yc.index.max()}). Single-year estimates are noisy, so read the trend, not one point.")
    long = yc[FACTOR_COLS].rename(columns=FACTORS).reset_index().melt("year", var_name="Factor", value_name="Raw coefficient")
    fig = px.line(long, x="year", y="Raw coefficient", facet_col="Factor", facet_col_wrap=3, markers=True, height=520)
    fig.update_yaxes(matches=None, showticklabels=True)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, width="stretch")

    st.markdown("#### Compare two periods")
    lo, hi = int(yc.index.min()), int(yc.index.max())
    c1, c2 = st.columns(2)
    pa = c1.slider("Earlier period", lo, hi, (max(lo, 2010), 2014))
    pb = c2.slider("Later period", lo, hi, (2019, hi))
    ra, rb = pooled_period(df, *pa), pooled_period(df, *pb)
    if ra is None or rb is None:
        st.warning("Not enough complete data in one of those periods. Widen the range.")
        return
    comp = pd.DataFrame({
        f"{pa[0]}-{pa[1]}": ra[1], f"{pb[0]}-{pb[1]}": rb[1],
    })
    comp["Change"] = comp.iloc[:, 1] - comp.iloc[:, 0]
    comp = comp.rename(index=FACTORS).reindex(comp.rename(index=FACTORS)["Change"].abs().sort_values(ascending=False).index)
    st.dataframe(comp.style.format("{:+.3f}"), width="stretch")
    st.caption(f"Standardized coefficients from pooled regressions ({ra[3]:,} vs {rb[3]:,} country-years; "
               f"R-squared {ra[2]:.2f} vs {rb[2]:.2f}). Sorted by size of change. Pooling several years gives steadier estimates than two single years.")
    with st.expander("Raw (unstandardized) coefficients for the same periods"):
        raw = pd.DataFrame({f"{pa[0]}-{pa[1]}": ra[0], f"{pb[0]}-{pb[1]}": rb[0]}).rename(index=FACTORS)
        raw["Change"] = raw.iloc[:, 1] - raw.iloc[:, 0]
        st.dataframe(raw.style.format("{:+.3f}"), width="stretch")


# --------------------------------------------------------------- tab 4
def _region_tab(df: pd.DataFrame):
    res, excluded = region_results(df)
    fig = px.bar(res.reset_index(), x="region", y="r_squared", text=res["r_squared"].round(2).astype(str),
                 title="How well do the six factors explain happiness in each region? (R-squared)",
                 labels={"r_squared": "R-squared", "region": ""})
    fig.update_layout(height=340, margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(fig, width="stretch")

    heat = res[FACTOR_COLS].rename(columns=FACTORS)
    fig2 = px.imshow(heat, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu",
                     color_continuous_midpoint=0, title="What matters most in each region (standardized coefficients)")
    fig2.update_layout(height=380, margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(fig2, width="stretch")

    st.dataframe(res[["n_obs", "r_squared"]].rename(columns={"n_obs": "Country-year rows", "r_squared": "R-squared"})
                 .style.format({"R-squared": "{:.3f}"}), width="stretch")
    if excluded:
        names = ", ".join(f"{r} ({n} rows)" for r, n in excluded)
        st.caption(f"Excluded as too small for a six-factor regression (under {MIN_REGION_OBS} rows): {names}. "
                   "Oceania here is only Australia and New Zealand.")
    st.caption("Regions are continents (Russia and Kosovo counted as Europe; Central America and the Caribbean under North America). "
               "A rough grouping, not the WHR's official regions.")
