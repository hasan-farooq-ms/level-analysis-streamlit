import streamlit as st
import pandas as pd
from utils.data_loader import load_main_data

def render():
    st.title("Time between install and first purchase")
    
    df = load_main_data()

    df_q2 = df.dropna(subset=[
        "user_data.user_id",
        "install_timestamp",
        "adjust_post_events_iap.adj_event_timestamp_time",
        "adjust_post_events_iap.adj_session_count"
    ])

    df_q2["install_timestamp"] = pd.to_datetime(df_q2["install_timestamp"])
    df_q2["purchase_time"] = pd.to_datetime(df_q2["adjust_post_events_iap.adj_event_timestamp_time"])

    first_purchases = (
        df_q2.sort_values(by="purchase_time")
        .groupby("user_data.user_id")
        .first()
    )

    first_purchases["hours_to_first_purchase"] = (
        (first_purchases["purchase_time"] - first_purchases["install_timestamp"])
        .dt.total_seconds() / 3600
    )
    first_purchases["session_gap"] = first_purchases["adjust_post_events_iap.adj_session_count"]

    time_percentiles = first_purchases["hours_to_first_purchase"].quantile([0.25, 0.5, 0.75])
    session_percentiles = first_purchases["session_gap"].quantile([0.25, 0.5, 0.75])
    time_mean = first_purchases["hours_to_first_purchase"].mean()
    session_mean = first_purchases["session_gap"].mean()

    st.subheader("🕓 Time to First Purchase (in hours)")
    st.markdown(f"- **Mean:** {time_mean:.2f}h")
    st.markdown(f"- **25th percentile:** {time_percentiles.loc[0.25]:.2f}h")
    st.markdown(f"- **Median:** {time_percentiles.loc[0.5]:.2f}h")
    st.markdown(f"- **75th percentile:** {time_percentiles.loc[0.75]:.2f}h")

    st.subheader("🎮 Session Count at First Purchase")
    st.markdown(f"- **Mean:** {session_mean:.2f}")
    st.markdown(f"- **25th percentile:** {session_percentiles.loc[0.25]:.0f}")
    st.markdown(f"- **Median:** {session_percentiles.loc[0.5]:.0f}")
    st.markdown(f"- **75th percentile:** {session_percentiles.loc[0.75]:.0f}")

    with st.expander("Show raw first purchase data"):
        st.dataframe(first_purchases[[
            "install_timestamp", "purchase_time", "hours_to_first_purchase", "session_gap"
        ]].reset_index())

