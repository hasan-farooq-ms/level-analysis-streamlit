import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from utils.data_loader import load_main_data

def render():
    st.title("Do high-value purchases happen at higher levels or earlier in the lifecycle?")

    df = load_main_data()

    df_q8 = df.dropna(subset=[
        "adjust_post_events_iap.user_level_linear",
        "adjust_post_events_iap.adj_converted_usd_value_dimension",
        "adjust_post_events_iap.adj_session_count"
    ])

    df_q8["user_level"] = df_q8["adjust_post_events_iap.user_level_linear"].astype(int)
    df_q8["session_count"] = df_q8["adjust_post_events_iap.adj_session_count"].astype(int)
    df_q8["usd_value"] = df_q8["adjust_post_events_iap.adj_converted_usd_value_dimension"].astype(float)
    df_q8["value_band"] = df_q8["usd_value"].apply(lambda x: "High ($10+)" if x >= 10 else "Low (<$10)")

    # trim outliers (5th–95th percentile)
    level_bounds = df_q8["user_level"].quantile([0.05, 0.95])
    session_bounds = df_q8["session_count"].quantile([0.05, 0.95])

    df_q8_trimmed = df_q8[
        (df_q8["user_level"] >= level_bounds.iloc[0]) &
        (df_q8["user_level"] <= level_bounds.iloc[1]) &
        (df_q8["session_count"] >= session_bounds.iloc[0]) &
        (df_q8["session_count"] <= session_bounds.iloc[1])
    ]

    level_bins = np.linspace(level_bounds.iloc[0], level_bounds.iloc[1], 50)
    level_dist = []

    for label, group in df_q8_trimmed.groupby("value_band"):
        counts, bins = np.histogram(group["user_level"], bins=level_bins)
        pct = np.round(counts / counts.sum() * 100, 2)
        mid = 0.5 * (bins[1:] + bins[:-1])
        temp = pd.DataFrame({
            "User Level": mid,
            "Percentage": pct,
            "Value Band": label
        })
        level_dist.append(temp)

    df_level_plot = pd.concat(level_dist)

    session_bins = np.linspace(session_bounds.iloc[0], session_bounds.iloc[1], 50)
    session_dist = []

    for label, group in df_q8_trimmed.groupby("value_band"):
        counts, bins = np.histogram(group["session_count"], bins=session_bins)
        pct = np.round(counts / counts.sum() * 100, 2)
        mid = 0.5 * (bins[1:] + bins[:-1])
        temp = pd.DataFrame({
            "Session Count": mid,
            "Percentage": pct,
            "Value Band": label
        })
        session_dist.append(temp)

    df_session_plot = pd.concat(session_dist)

    st.subheader("User Level at Purchase")
    chart1 = alt.Chart(df_level_plot).mark_line(point=True).encode(
        x=alt.X("User Level:Q"),
        y=alt.Y("Percentage:Q"),
        color="Value Band:N",
        tooltip=["User Level", "Percentage", "Value Band"]
    ).properties(
        width=700,
        height=300,
        title="Distribution of Purchases by User Level"
    )
    st.altair_chart(chart1, use_container_width=True)

    st.subheader("Session Count at Purchase")
    chart2 = alt.Chart(df_session_plot).mark_line(point=True).encode(
        x=alt.X("Session Count:Q"),
        y=alt.Y("Percentage:Q"),
        color="Value Band:N",
        tooltip=["Session Count", "Percentage", "Value Band"]
    ).properties(
        width=700,
        height=300,
        title="Distribution of Purchases by Session Count"
    )
    st.altair_chart(chart2, use_container_width=True)

    with st.expander("Show trimmed (extreme outliers removed) data sample"):
        st.dataframe(df_q8_trimmed[["user_level", "session_count", "usd_value", "value_band"]].sample(10))
