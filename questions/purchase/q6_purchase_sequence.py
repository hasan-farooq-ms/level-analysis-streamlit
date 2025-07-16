import streamlit as st
import pandas as pd
import altair as alt
from utils.data_loader import load_main_data

def render():
    st.title("How does the sequence of purchases evolve?")

    df = load_main_data()

    df_q6 = df.dropna(subset=[
        "user_data.user_id",
        "adjust_post_events_iap.adj_purchase_order",
        "adjust_post_events_iap.adj_converted_usd_value_dimension"
    ])

    df_q6["purchase_order"] = df_q6["adjust_post_events_iap.adj_purchase_order"].astype(int)
    df_q6["usd_value"] = df_q6["adjust_post_events_iap.adj_converted_usd_value_dimension"].astype(float)

    def price_band(x):
        if x <= 2:
            return "$0–2"
        elif x <= 5:
            return "$2–5"
        elif x <= 10:
            return "$5–10"
        else:
            return "$10+"

    df_q6b = df_q6[df_q6["purchase_order"] <= 50].copy()
    df_q6b["price_band"] = df_q6b["usd_value"].map(price_band)

    band_counts = df_q6b.groupby(["purchase_order", "price_band"]).size().unstack(fill_value=0)
    band_percentages = round(band_counts.div(band_counts.sum(axis=1), axis=0) * 100, 2)
    band_percentages = band_percentages.reset_index().melt(id_vars="purchase_order", var_name="Price Band", value_name="Percentage")

    chart = alt.Chart(band_percentages).mark_area().encode(
        x=alt.X("purchase_order:Q", title="Purchase Order"),
        y=alt.Y("Percentage:Q", stack="normalize"),
        color=alt.Color("Price Band:N", scale=alt.Scale(scheme="tableau20")),
        tooltip=["purchase_order", "Price Band", "Percentage"]
    ).properties(
        width=750,
        height=400,
        title="Price Band Composition by Purchase Order"
    )

    st.altair_chart(chart, use_container_width=True)

    with st.expander("Show raw distribution data"):
        st.dataframe(band_percentages)

