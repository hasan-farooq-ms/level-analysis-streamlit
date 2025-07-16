import streamlit as st
import pandas as pd
import altair as alt
from utils.data_loader import load_main_data

def render():
    st.title("What’s the average purchase frequency per user type?")

    df = load_main_data()

    df_q7 = df.dropna(subset=[
        "user_data.user_id",
        "lifetime_status_lifetime_level_completed",
        "adjust_post_events_iap.adj_converted_usd_value_dimension"
    ])
    df_q7["revenue"] = df_q7["adjust_post_events_iap.adj_converted_usd_value_dimension"].astype(float)

    user_summary = df_q7.groupby("user_data.user_id").agg({
        "lifetime_status_lifetime_level_completed": "first",
        "adjust_post_events_iap.adj_purchase_order": "count",
        "revenue": "sum"
    }).rename(columns={
        "lifetime_status_lifetime_level_completed": "levels_completed",
        "adjust_post_events_iap.adj_purchase_order": "purchase_count",
        "revenue": "total_revenue"
    })

    def tag_user_type(x):
        if x <= 50:
            return "Casual"
        elif x <= 200:
            return "Midcore"
        else:
            return "Hardcore"

    user_summary["user_type"] = user_summary["levels_completed"].map(tag_user_type)

    type_summary = round(user_summary.groupby("user_type").agg(
        user_count=("purchase_count", "count"),
        avg_purchases=("purchase_count", "mean"),
        total_revenue=("total_revenue", "sum"),
        avg_revenue_per_user=("total_revenue", "mean")), 2
    )
    type_summary["user_pct"] = round(type_summary["user_count"] / type_summary["user_count"].sum() * 100, 2)
    type_summary["revenue_pct"] = round(type_summary["total_revenue"] / type_summary["total_revenue"].sum() * 100, 2)
    type_summary = type_summary.reset_index()

    st.subheader("Summary by User Type")
    st.dataframe(type_summary.style.format({
        "avg_purchases": "{:.2f}",
        "avg_revenue_per_user": "${:.2f}",
        "total_revenue": "${:,.0f}",
        "user_pct": "{:.1f}%",
        "revenue_pct": "{:.1f}%"
    }))

    chart1 = alt.Chart(type_summary).mark_bar().encode(
        x=alt.X("avg_revenue_per_user:Q", title="Avg Revenue per User (USD)"),
        y=alt.Y("user_type:N", sort="-x", title="User Type"),
        color=alt.value("skyblue"),
        tooltip=["user_type", "avg_revenue_per_user"]
    ).properties(
        width=600,
        height=300,
        title="Avg Revenue per User by Type"
    )

    chart2_data = type_summary.melt(id_vars="user_type", value_vars=["user_pct", "revenue_pct"],
                                    var_name="Metric", value_name="Percentage")

    chart2 = alt.Chart(chart2_data).mark_bar().encode(
        x=alt.X("Percentage:Q"),
        y=alt.Y("user_type:N", title="User Type", sort="-x"),
        color=alt.Color("Metric:N", scale=alt.Scale(scheme="category10")),
        tooltip=["user_type", "Metric", "Percentage"]
    ).properties(
        width=650,
        height=300,
        title="User Share vs Revenue Share by Type"
    )

    st.altair_chart(chart1, use_container_width=True)
    st.altair_chart(chart2, use_container_width=True)

    with st.expander("Show raw user-level data"):
        st.dataframe(user_summary.reset_index())

