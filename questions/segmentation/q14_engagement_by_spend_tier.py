import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import percentileofscore

from utils.data_loader import load_main_data


def render():
    st.title("Q14: Engagement Profiles by Spend Tier")

    df = load_main_data()

    engagement_cols = [
        "session_count", "time_in_app", "lifetime_status_lifetime_attempts",
        "lifetime_status_lifetime_level_completed", "lifetime_status_lifetime_stack_velocity",
        "lifetime_status_lifetime_stacks_placed", "lifetime_status_lifetime_highest_stack_size",
        "lifetime_status_meta_completed"
    ]

    df_q14 = df[engagement_cols + ["lifetime_spend_iap"]].dropna()

    # Define spend tiers
    df_q14["spend_tier_v2"] = pd.cut(
        df_q14["lifetime_spend_iap"],
        bins=[0, 10, 20, 50, 200, 500],
        labels=["dummy", "Low", "Medium", "High", "High"],
        include_lowest=True,
        ordered=False
    )

    # Group by tier and compute mean engagement
    mean_stats_v2 = (
        df_q14[df_q14["spend_tier_v2"] != "dummy"]
        .groupby("spend_tier_v2", observed=True)[engagement_cols]
        .mean()
    )

    # Normalize using global percentiles
    normalized_v2 = pd.DataFrame(index=mean_stats_v2.index, columns=engagement_cols)
    for col in engagement_cols:
        global_dist = df_q14[col].dropna()
        for tier in mean_stats_v2.index:
            val = mean_stats_v2.loc[tier, col]
            normalized_v2.loc[tier, col] = percentileofscore(global_dist, val)

    normalized_v2 = normalized_v2.reindex(["Low", "Medium", "High"])

    # Radar chart
    categories = engagement_cols + [engagement_cols[0]]  # loop to start

    fig = go.Figure()

    color_map = {"Low": "blue", "Medium": "orange", "High": "green"}

    for tier in normalized_v2.index:
        values = normalized_v2.loc[tier].tolist()
        values += values[:1]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=tier,
            line=dict(color=color_map.get(tier, "gray"))
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)
        ),
        title="Engagement Profiles by Spend Tier (Percentile Scaled)",
        showlegend=True,
        margin=dict(t=40, b=20, l=20, r=20)
    )

    st.plotly_chart(fig)

    with st.expander("📄 View Normalized Percentiles"):
        st.dataframe(normalized_v2.round(1))
