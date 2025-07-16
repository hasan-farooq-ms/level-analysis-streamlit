import streamlit as st
import pandas as pd
import altair as alt
from utils.data_loader import load_main_data

def render():
    st.title("What are the most purchased items and their revenue contribution?")

    df = load_main_data()

    df_q3 = df.dropna(subset=[
        "adjust_post_events_iap.adj_product_id",
        "adjust_post_events_iap.adj_converted_usd_value_dimension"
    ])
    df_q3["revenue"] = df_q3["adjust_post_events_iap.adj_converted_usd_value_dimension"].astype(float)

    purchase_pct = (
        round(df_q3["adjust_post_events_iap.adj_product_id"]
        .value_counts(normalize=True) * 100, 2)
    )

    revenue_pct = (
        round(df_q3.groupby("adjust_post_events_iap.adj_product_id")["revenue"]
        .sum()
        .div(df_q3["revenue"].sum()) * 100, 2)
    )

    q3_summary = pd.DataFrame({
        "purchase_pct": purchase_pct,
        "revenue_pct": revenue_pct
    }).fillna(0).sort_values("revenue_pct", ascending=False)


    top_n = st.slider("Top N products to display", 5, 15, 10)
    q3_summary.index.name = "product_id"
    q3_summary_top = q3_summary.head(top_n).reset_index()

    melted = q3_summary_top.melt(id_vars="product_id", value_vars=["purchase_pct", "revenue_pct"],
                                 var_name="Metric", value_name="Percentage")

    chart = alt.Chart(melted).mark_bar().encode(
        x=alt.X("product_id:N", title="Product ID/Name", sort=None),
        y=alt.Y("Percentage:Q"),
        color=alt.Color("Metric:N", scale=alt.Scale(scheme="set2")),
        tooltip=["product_id", "Metric", "Percentage"]
    ).properties(
        width=750,
        height=500,
        title="Top Products by % of Purchases and Revenue"
    )

    st.altair_chart(chart, use_container_width=True)

    with st.expander("Show raw product summary"):
        st.dataframe(q3_summary_top)
