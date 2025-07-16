import streamlit as st
import pandas as pd
import altair as alt
from utils.data_loader import load_main_data

def render():
    st.title("Top Countries Among Purchasers")

    df = load_main_data()
    df_q4 = df.dropna(subset=["adjust_post_events_iap.adj_country"])

    country_pct = round((
        df_q4["adjust_post_events_iap.adj_country"]
        .value_counts(normalize=True) * 100
    ), 2)

    top_n = st.slider("Top N countries to display", 5, 30, 10)
    country_df = country_pct.head(top_n).reset_index()
    country_df.columns = ["Country", "Percentage"]

    chart = alt.Chart(country_df).mark_bar().encode(
        x=alt.X("Country:N", sort=None),
        y=alt.Y("Percentage:Q"),
        tooltip=["Country", "Percentage"]
    ).properties(
        width=700,
        height=400,
        title="Top Countries Among Purchasers (%)"
    )

    st.altair_chart(chart, use_container_width=True)

    with st.expander("Show raw data"):
        st.dataframe(country_df)
