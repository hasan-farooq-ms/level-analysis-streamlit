import streamlit as st
import pandas as pd
import altair as alt
from utils.data_loader import load_main_data

def render():
    st.title("What is the lifetime value (LTV) segmented by first purchase level or product?")

    df = load_main_data()

    df_q9 = df.dropna(subset=[
        "user_data.user_id",
        "adjust_post_events_iap.adj_event_timestamp_time",
        "adjust_post_events_iap.adj_converted_usd_value_dimension",
        "adjust_post_events_iap.user_level_linear",
        "adjust_post_events_iap.adj_product_id"
    ])

    df_q9["revenue"] = df_q9["adjust_post_events_iap.adj_converted_usd_value_dimension"].astype(float)
    df_q9["user_level"] = df_q9["adjust_post_events_iap.user_level_linear"]
    df_q9["product_id"] = df_q9["adjust_post_events_iap.adj_product_id"]

    first_purchases = (
        df_q9.sort_values(by="adjust_post_events_iap.adj_event_timestamp_time")
        .groupby("user_data.user_id")
        .first()
    )

    user_revenue = round(df_q9.groupby("user_data.user_id")["revenue"].sum(), 2)
    first_purchases["ltv"] = user_revenue

    view_mode = st.radio("Segment LTV by:", ["First Purchased Product", "First Purchase User Level Bin"])

    if view_mode == "First Purchased Product":
        ltv_by_product = round(first_purchases.groupby("product_id")["ltv"].agg(["mean", "count"]), 2)
        ltv_by_product["user_pct"] = round(ltv_by_product["count"] / ltv_by_product["count"].sum() * 100, 2)
        ltv_by_product = ltv_by_product.sort_values("mean", ascending=False).reset_index()

        st.subheader("LTV by First Purchased Product")
        top_n = st.slider("Top N products to display", 5, 30, 10)

        chart = alt.Chart(ltv_by_product.head(top_n)).mark_bar().encode(
            x=alt.X("mean:Q", title="Avg LTV (USD)"),
            y=alt.Y("product_id:N", sort="-x", title="Product ID"),
            tooltip=["product_id", "mean", "count", "user_pct"]
        ).properties(
            width=700,
            height=400,
            title="Average LTV by First Product Purchased"
        )
        st.altair_chart(chart, use_container_width=True)

        with st.expander("Show raw product-level LTV"):
            st.dataframe(ltv_by_product)

    else:
        bins = [0, 20, 50, 100, 200, 500, 1000]
        labels = ["0–20", "21–50", "51–100", "101–200", "201–500", "501–1000"]
        first_purchases["level_bin"] = pd.cut(first_purchases["user_level"], bins=bins, labels=labels)

        ltv_by_level = round(first_purchases.groupby("level_bin")["ltv"].agg(["mean", "count"]), 2)
        ltv_by_level["user_pct"] = round(ltv_by_level["count"] / ltv_by_level["count"].sum() * 100, 2)
        ltv_by_level = ltv_by_level.reset_index()

        st.subheader("LTV by User Level Bin at First Purchase")

        chart = alt.Chart(ltv_by_level).mark_bar().encode(
            x=alt.X("mean:Q", title="Avg LTV (USD)"),
            y=alt.Y("level_bin:N", sort="-x", title="User Level Bin"),
            tooltip=["level_bin", "mean", "count", "user_pct"]
        ).properties(
            width=700,
            height=400,
            title="Average LTV by First Purchase Level Bin"
        )
        st.altair_chart(chart, use_container_width=True)

        with st.expander("Show raw level-bin LTV"):
            st.dataframe(ltv_by_level)

