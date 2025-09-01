import streamlit as st
import pandas as pd
import altair as alt

from utils.data_loader import load_main_data


def render():
    st.title("Q13: Engagement vs Spend Correlation")

    df = load_main_data()

    q13_cols = [
        "user_data.user_id",
        "session_count",
        "time_in_app",
        "lifetime_status_lifetime_attempts",
        "lifetime_status_lifetime_level_completed",
        "lifetime_status_lifetime_stack_velocity",
        "lifetime_status_lifetime_stacks_placed",
        "lifetime_status_lifetime_highest_stack_size",
        "lifetime_status_meta_completed",
        "lifetime_spend_iap"
    ]

    df_q13 = df[q13_cols].dropna()

    # Outlier filtering (1st–99th percentile)
    engagement_cols = [
        "session_count", "time_in_app", "lifetime_status_lifetime_attempts",
        "lifetime_status_lifetime_level_completed", "lifetime_status_lifetime_stack_velocity",
        "lifetime_status_lifetime_stacks_placed", "lifetime_status_meta_completed"
    ]

    df_q13_filtered = df_q13.copy()
    for col in engagement_cols + ["lifetime_spend_iap"]:
        q_low = df_q13[col].quantile(0.01)
        q_high = df_q13[col].quantile(0.99)
        df_q13_filtered = df_q13_filtered[
            (df_q13_filtered[col] >= q_low) & (df_q13_filtered[col] <= q_high)
        ]

    # Compute correlation
    corr = df_q13_filtered.drop(columns=["user_data.user_id"]).corr()
    corr_target = corr[["lifetime_spend_iap"]].drop("lifetime_spend_iap")
    corr_target = corr_target.rename(columns={"lifetime_spend_iap": "correlation"})
    corr_target["correlation_pct"] = (corr_target["correlation"] * 100).round(1)
    corr_target = corr_target.sort_values("correlation", ascending=False).reset_index()
    corr_target.rename(columns={"index": "metric"}, inplace=True)

    st.subheader("📊 Engagement Metrics Correlation with Spend")

    chart = alt.Chart(corr_target).mark_bar().encode(
        y=alt.Y("metric:N", sort="-x", title="Metric", axis=alt.Axis(labelLimit=300)),
        x=alt.X("correlation_pct:Q", title="Correlation with Spend (%)"),
        color=alt.Color("correlation_pct:Q", scale=alt.Scale(scheme="redblue")),
        tooltip=["metric", "correlation_pct"]
    ).properties(
        width=700,
        height=400,
        title="Engagement Correlation with IAP Spend",
        padding={"left": 20}  # extra padding to avoid truncation
    )

    st.altair_chart(chart)

    with st.expander("📄 View Cleaned Input Data"):
        st.dataframe(df_q13_filtered)
