import streamlit as st
import pandas as pd
import altair as alt
from utils.data_loader import load_main_data

def render():
    st.title("How many users make just one purchase vs. repeat purchases?")

    df = load_main_data()

    purchase_counts = df["user_data.user_id"].value_counts()

    def bucket(n):
        if n == 1:
            return "1"
        elif 2 <= n <= 5:
            return "2–5"
        elif 6 <= n <= 10:
            return "6–10"
        elif 11 <= n <= 15:
            return "11–15"
        elif 16 <= n <= 20:
            return "16–20"
        elif 21 <= n <= 30:
            return "21–30"
        else:
            return "30+"

    buckets = purchase_counts.map(bucket)
    bucket_dist = round(buckets.value_counts(normalize=True) * 100, 2)
    bucket_df = bucket_dist.reset_index()
    bucket_df.columns = ["Bucket", "Percentage"]
    bucket_df = bucket_df.sort_values("Bucket")

    chart = alt.Chart(bucket_df).mark_bar().encode(
        x=alt.X("Bucket:N", title="Purchase Count Bucket"),
        y=alt.Y("Percentage:Q"),
        tooltip=["Bucket", "Percentage"]
    ).properties(
        width=600,
        height=350,
        title="Purchase Frequency Buckets (%)"
    )

    st.altair_chart(chart, use_container_width=True)

    with st.expander("Show raw data"):
        st.dataframe(bucket_df)

