import streamlit as st
import pandas as pd
import altair as alt
from utils.data_loader import load_main_data

def render():
    st.title("How do session counts relate to total IAP spend?")

    df = load_main_data()

    df_q10 = df.dropna(subset=[
        "user_data.user_id",
        "adjust_post_events_iap.adj_session_count",
        "adjust_post_events_iap.adj_converted_usd_value_dimension"
    ])

    df_q10["session_count"] = df_q10["adjust_post_events_iap.adj_session_count"].astype(int)
    df_q10["revenue"] = df_q10["adjust_post_events_iap.adj_converted_usd_value_dimension"].astype(float)

    user_iap = df_q10.groupby("user_data.user_id").agg({
        "session_count": "max",        # max = final session
        "revenue": "sum"               # total IAP spend
    }).rename(columns={
        "session_count": "final_session",
        "revenue": "total_spend"
    })

    # extreme outliers (1st–99th percentile)
    session_bounds = user_iap["final_session"].quantile([0.01, 0.99])
    spend_bounds = user_iap["total_spend"].quantile([0.01, 0.99])

    df_trimmed = user_iap[
        (user_iap["final_session"] >= session_bounds.iloc[0]) &
        (user_iap["final_session"] <= session_bounds.iloc[1]) &
        (user_iap["total_spend"] >= spend_bounds.iloc[0]) &
        (user_iap["total_spend"] <= spend_bounds.iloc[1])
    ].reset_index()

    st.markdown("This chart shows the relationship between total session count and in-app spend at the user level, excluding extreme outliers.")

    chart = alt.Chart(df_trimmed).mark_circle(size=20, opacity=0.2).encode(
        x=alt.X("final_session:Q", title="Final Session Count"),
        y=alt.Y("total_spend:Q", title="Total IAP Spend (USD)"),
        tooltip=["user_data.user_id", "final_session", "total_spend"]
    ).properties(
        width=700,
        height=400,
        title="Total IAP Spend vs Final Session Count"
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    with st.expander("Show data sample"):
        st.dataframe(df_trimmed.head(10))
