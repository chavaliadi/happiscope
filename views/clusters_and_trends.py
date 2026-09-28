import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from common import FACTOR_COLS, FACTORS, TARGET, load_data

CLUSTER_COLORS = ["#2b5c8f", "#d95f02", "#7570b3", "#1b9e77", "#e7298a", "#e6ab02"]


@st.cache_data
def _compute_clustering(year: int, k: int):
    """Cluster complete countries for a given year using standardized WHR factors."""
    df = load_data()
    cols = ["Country name", "region", TARGET] + FACTOR_COLS
    d_yr = df[(df["year"] == year) & df[cols].notna().all(axis=1)].copy()

    if len(d_yr) < k:
        return None, None, None, None, None, None

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(d_yr[FACTOR_COLS])

    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    # 1-indexed cluster names for clarity: "Cluster 1", "Cluster 2", etc.
    d_yr["cluster"] = [f"Cluster {c + 1}" for c in labels]

    sil = float(silhouette_score(X_scaled, labels))
    inertia = float(km.inertia_)

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X_scaled)
    d_yr["pca1"] = coords[:, 0]
    d_yr["pca2"] = coords[:, 1]
    var_exp = [float(v) for v in pca.explained_variance_ratio_]

    return d_yr, X_scaled, sil, inertia, var_exp, km


@st.cache_data
def _compute_k_diagnostics(year: int):
    """Compute Inertia and Silhouette scores for K in 2..8."""
    df = load_data()
    cols = ["Country name"] + FACTOR_COLS
    d_yr = df[(df["year"] == year) & df[cols].notna().all(axis=1)].copy()

    if len(d_yr) < 10:
        return None

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(d_yr[FACTOR_COLS])

    records = []
    for candidate_k in range(2, 9):
        if candidate_k >= len(d_yr):
            break
        km = KMeans(n_clusters=candidate_k, random_state=42, n_init=10)
        lbls = km.fit_predict(X_scaled)
        records.append({
            "K": candidate_k,
            "Inertia (WCSS)": float(km.inertia_),
            "Silhouette Score": float(silhouette_score(X_scaled, lbls)),
        })
    return pd.DataFrame(records)


def render():
    df = load_data()

    st.title("Clusters & Trends")
    st.markdown(
        "**How do nations group naturally according to their well-being factor profiles?** "
        "Using unsupervised K-Means clustering, this page groups countries sharing similar patterns across "
        "the six World Happiness Report drivers, projects them into two dimensions using Principal Component Analysis (PCA), "
        "and tracks each cluster's average happiness trajectory over 20 years."
    )

    with st.expander("Methodology & Mathematical Specifications"):
        st.markdown(
            "- **Clustering Features:** The six explanatory factors (`Log GDP per capita`, `Social support`, "
            "`Healthy life expectancy`, `Freedom`, `Generosity`, `Perceptions of corruption`).\n"
            "- **Excluded from Clustering:** Country names, geographical regions, and the happiness score (`Life Ladder`) "
            "are **not** fed into the clustering algorithm. This ensures clusters reflect pure structural factor profiles rather than happiness scores alone.\n"
            "- **Standardization:** Factors are z-score standardized ($\\\\mu=0, \\\\sigma=1$) via `StandardScaler` so differing units (e.g. GDP vs life expectancy in years) do not distort Euclidean distances.\n"
            "- **Reproducibility:** K-Means runs with `random_state=42` and `n_init=10`.\n"
            "- **PCA Projection:** PCA maps 6-dimensional factor space onto 2 orthogonal axes maximizing variance for visualization. PCA axes represent linear combinations of factors, not real-world units.\n"
            "- **Longitudinal Tracking Rule:** Countries are clustered at a chosen **base year**. We then track the average happiness score of those *same* country cohorts from 2005 to 2023, avoiding artificial yearly cluster churn."
        )

    # ------------------------------------------------------------- Controls
    st.subheader("1. Clustering Configuration")
    valid_years = sorted(
        df[df[FACTOR_COLS].notna().all(axis=1)]["year"].unique().astype(int),
        reverse=True,
    )
    c1, c2 = st.columns([1, 1])
    with c1:
        base_year = st.selectbox(
            "Clustering Base Year",
            valid_years,
            index=0,
            key="ct_base_year",
            help="Year used to partition countries into structural factor clusters.",
        )
    with c2:
        k = st.slider(
            "Cluster Count (K) — User-selectable",
            min_value=3,
            max_value=6,
            value=4,
            key="ct_k",
            help="Select number of clusters. K is user-selectable and exploratory; no single K is universally optimal.",
        )

    clustered_df, X_scaled, sil, inertia, var_exp, km = _compute_clustering(base_year, k)
    if clustered_df is None or len(clustered_df) < k:
        st.error(f"Insufficient complete observations in {base_year} to fit {k} clusters.")
        return

    # ------------------------------------------------------------- Diagnostics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Countries Clustered", len(clustered_df))
    m2.metric("Selected K", k)
    m3.metric("Silhouette Score", f"{sil:.3f}", help="Ranges from -1 to +1. Higher values indicate more cohesive, well-separated clusters.")
    m4.metric("Inertia (WCSS)", f"{inertia:.1f}", help="Within-cluster sum of squared distances to centroids.")

    with st.expander("K-Selection Diagnostics (Elbow Curve & Silhouette Scores across K=2..8)"):
        diag_df = _compute_k_diagnostics(base_year)
        if diag_df is not None:
            col_l, col_r = st.columns(2)
            with col_l:
                fig_elbow = px.line(
                    diag_df, x="K", y="Inertia (WCSS)", markers=True,
                    title=f"Elbow Method: Inertia vs K ({base_year})",
                )
                fig_elbow.add_vline(x=k, line_dash="dash", line_color="#d95f02", annotation_text=f"Selected K={k}")
                fig_elbow.update_layout(height=280, margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig_elbow, width="stretch")
            with col_r:
                fig_sil = px.line(
                    diag_df, x="K", y="Silhouette Score", markers=True,
                    title=f"Silhouette Analysis vs K ({base_year})",
                )
                fig_sil.add_vline(x=k, line_dash="dash", line_color="#d95f02", annotation_text=f"Selected K={k}")
                fig_sil.update_layout(height=280, margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig_sil, width="stretch")
            st.caption("Note: Silhouette scores in social science panel surveys typically range between 0.20 and 0.40 due to continuous, overlapping distributions.")

    # ------------------------------------------------------------- PCA Visualization
    st.subheader(f"2. 2D PCA Cluster Map ({base_year})")
    pca_title = (
        f"Principal Component Analysis of Countries (PC1: {var_exp[0]*100:.1f}%, PC2: {var_exp[1]*100:.1f}% variance explained)"
    )

    hover_data = {
        "Country name": True,
        "region": True,
        TARGET: ":.2f",
        "pca1": False,
        "pca2": False,
        "cluster": True,
    }
    for col in FACTOR_COLS:
        hover_data[col] = ":.2f"

    fig_pca = px.scatter(
        clustered_df,
        x="pca1",
        y="pca2",
        color="cluster",
        color_discrete_sequence=CLUSTER_COLORS,
        hover_name="Country name",
        hover_data=hover_data,
        title=pca_title,
        labels={"pca1": f"PCA Component 1 ({var_exp[0]*100:.1f}% var)", "pca2": f"PCA Component 2 ({var_exp[1]*100:.1f}% var)"},
        category_orders={"cluster": [f"Cluster {i+1}" for i in range(k)]},
    )
    fig_pca.update_traces(marker=dict(size=10, opacity=0.85, line=dict(width=0.5, color="#333")))
    fig_pca.update_layout(height=480, margin=dict(l=0, r=0, t=40, b=0), legend_title_text="")
    st.plotly_chart(fig_pca, width="stretch")
    st.caption("Hover over any dot to view country name, region, happiness score, and all six underlying factor values. "
               "Axes are mathematical projections of the 6 dimensions onto 2 orthogonal axes, not direct real-world units.")

    # ------------------------------------------------------------- Cluster Profiles
    st.subheader("3. Cluster Profiles & Factor Comparison")
    prof_means = clustered_df.groupby("cluster")[FACTOR_COLS].mean().reset_index()
    prof_counts = clustered_df.groupby("cluster")["Country name"].count().rename("Country Count")
    prof_hap = clustered_df.groupby("cluster")[TARGET].mean().rename("Avg Life Ladder")
    prof_summary = pd.concat([prof_counts, prof_hap], axis=1).loc[[f"Cluster {i+1}" for i in range(k)]]

    st.dataframe(
        prof_summary.style.format({"Avg Life Ladder": "{:.2f}"}),
        width="stretch",
    )

    melted_prof = prof_means.melt(id_vars="cluster", var_name="Factor", value_name="Mean Value")
    melted_prof["Factor Label"] = melted_prof["Factor"].map(FACTORS)

    fig_bar = px.bar(
        melted_prof,
        x="Factor Label",
        y="Mean Value",
        color="cluster",
        barmode="group",
        color_discrete_sequence=CLUSTER_COLORS,
        title=f"Mean Driver Levels Across Clusters ({base_year})",
        labels={"Mean Value": "Mean Unstandardized Level", "Factor Label": "Factor"},
        category_orders={"cluster": [f"Cluster {i+1}" for i in range(k)]},
    )
    fig_bar.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0), legend_title_text="")
    st.plotly_chart(fig_bar, width="stretch")
    st.caption("Clusters represent structural groupings (e.g. high GDP and strong social support vs lower resources with high freedom). "
               "Cluster names are neutral numeric labels to avoid subjective stereotyping.")

    # ------------------------------------------------------------- Country Explorer
    st.subheader("4. Country Explorer: Cluster Context")
    all_countries = sorted(clustered_df["Country name"].unique())
    default_idx = all_countries.index("India") if "India" in all_countries else 0
    sel_country = st.selectbox("Select a country to inspect:", all_countries, index=default_idx, key="ct_sel_country")

    c_row = clustered_df[clustered_df["Country name"] == sel_country].iloc[0]
    c_cluster = c_row["cluster"]
    c_cluster_mean = clustered_df[clustered_df["cluster"] == c_cluster][FACTOR_COLS].mean()

    e1, e2, e3 = st.columns(3)
    e1.metric("Country", sel_country)
    e2.metric("Assigned Cluster", c_cluster)
    e3.metric(f"Life Ladder ({base_year})", f"{c_row[TARGET]:.2f}")

    diff_df = pd.DataFrame({
        "Factor": [FACTORS[f] for f in FACTOR_COLS],
        f"{sel_country} Level": [c_row[f] for f in FACTOR_COLS],
        f"{c_cluster} Average": [c_cluster_mean[f] for f in FACTOR_COLS],
    })
    diff_df["Diff vs Cluster Avg"] = diff_df[f"{sel_country} Level"] - diff_df[f"{c_cluster} Average"]

    st.dataframe(
        diff_df.style.format({
            f"{sel_country} Level": "{:.2f}",
            f"{c_cluster} Average": "{:.2f}",
            "Diff vs Cluster Avg": "{:+.2f}",
        }),
        width="stretch",
    )

    # ------------------------------------------------------------- Longitudinal Trends
    st.subheader(f"5. Longitudinal Happiness Trends of {base_year} Clusters (2005–2023)")
    st.markdown(
        f"This longitudinal analysis fixes the country groupings established in **{base_year}** and tracks their "
        f"collective average happiness score across the entire 2005–2023 dataset. "
        "This ensures trend lines represent the historical trajectory of consistent country cohorts rather than shifting annual cluster definitions."
    )

    cohort_map = clustered_df.set_index("Country name")["cluster"].to_dict()
    cohort_df = df[df["Country name"].isin(cohort_map) & df[TARGET].notna()].copy()
    cohort_df["cluster"] = cohort_df["Country name"].map(cohort_map)

    trend_series = cohort_df.groupby(["year", "cluster"])[TARGET].agg(["mean", "count"]).reset_index()
    trend_series.rename(columns={"mean": "Average Life Ladder", "count": "Sample Count"}, inplace=True)

    fig_trend = px.line(
        trend_series,
        x="year",
        y="Average Life Ladder",
        color="cluster",
        color_discrete_sequence=CLUSTER_COLORS,
        markers=True,
        title=f"Happiness Trajectory of {base_year} Cluster Cohorts Over Time (2005–2023)",
        labels={"year": "Year", "Average Life Ladder": "Average Happiness Score (0-10)"},
        category_orders={"cluster": [f"Cluster {i+1}" for i in range(k)]},
    )
    fig_trend.add_vline(x=base_year, line_dash="dash", line_color="#888", annotation_text=f"Base Year {base_year}")
    fig_trend.update_layout(height=420, margin=dict(l=0, r=0, t=50, b=0), legend_title_text="")
    st.plotly_chart(fig_trend, width="stretch")

    st.caption("When survey coverage is sparse in earlier years (e.g. 2005–2007), cluster averages reflect available country observations within each cohort.")
