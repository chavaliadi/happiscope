import plotly.express as px
import streamlit as st

from common import TARGET, load_data


def render():
    df = load_data()

    st.title("HappiScope")
    st.markdown(
        "**What makes a country happy, and how has that changed?** "
        "Explore 20 years of World Happiness Report data across "
        f"**{df['Country name'].nunique()} countries**, and see which factors "
        "(money, social support, health, freedom, generosity, corruption) actually drive the scores."
    )

    year = st.slider("Year", int(df["year"].min()), int(df["year"].max()), int(df["year"].max()))
    d = df[(df["year"] == year) & df[TARGET].notna()]

    c1, c2, c3 = st.columns(3)
    c1.metric("Countries with data", len(d))
    c2.metric("Average happiness score (0-10)", f"{d[TARGET].mean():.2f}")
    best = d.loc[d[TARGET].idxmax()]
    c3.metric("Happiest country", best["Country name"], f"{best[TARGET]:.2f}")

    if year < 2008:
        st.info(f"Only {len(d)} countries were surveyed in {year}, so the map is sparse.")

    fig = px.choropleth(
        d.dropna(subset=["iso3"]),
        locations="iso3",
        color=TARGET,
        hover_name="Country name",
        color_continuous_scale="Viridis",
        range_color=(2, 8.5),
        labels={TARGET: "Happiness score"},
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=460)
    st.plotly_chart(fig, width="stretch")

    left, right = st.columns(2)
    cols = ["Country name", TARGET]
    with left:
        st.subheader(f"Top 10 in {year}")
        st.dataframe(d.nlargest(10, TARGET)[cols].reset_index(drop=True), hide_index=True, width="stretch")
    with right:
        st.subheader(f"Bottom 10 in {year}")
        st.dataframe(d.nsmallest(10, TARGET)[cols].reset_index(drop=True), hide_index=True, width="stretch")

    st.caption("Source: World Happiness Report (Gallup World Poll). Score = 'Life Ladder': "
               "people rate their life from 0 (worst possible) to 10 (best possible).")
