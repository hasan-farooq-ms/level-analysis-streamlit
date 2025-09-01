import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_main_data


def render():
    st.title("Q12: Persona-based Spend Analysis")

    df = load_main_data()

    q12_cols = [
        "user_data.user_id",
        "lifetime_status_lifetime_hammer_used",
        "lifetime_status_lifetime_replace_used",
        "lifetime_status_lifetime_refresh_used",
        "lifetime_status_lifetime_revive_used",
        "lifetime_status_lifetime_level_failed",
        "lifetime_status_lifetime_level_completed",
        "lifetime_status_lifetime_attempts",
        "lifetime_status_lifetime_rv_watched",
        "session_count",
        "time_in_app",
        "lifetime_spend_iap"
    ]

    df_q12 = df[q12_cols].dropna()

    # Persona tagging
    df_q12["revive_heavy"] = df_q12["lifetime_status_lifetime_revive_used"] > 20
    df_q12["booster_heavy"] = (
        df_q12["lifetime_status_lifetime_hammer_used"] +
        df_q12["lifetime_status_lifetime_replace_used"] +
        df_q12["lifetime_status_lifetime_refresh_used"]
    ) > 30
    df_q12["failure_reliant"] = df_q12["lifetime_status_lifetime_level_failed"] > 100
    df_q12["engaged_heavy"] = (
        (df_q12["session_count"] > 500) |
        (df_q12["time_in_app"] > 1_000_000)
    )

    def label_persona(row):
        tags = []
        if row["revive_heavy"]: tags.append("Revive")
        if row["booster_heavy"]: tags.append("Booster")
        if row["failure_reliant"]: tags.append("Failure")
        if row["engaged_heavy"]: tags.append("Engaged")
        return "+".join(tags) if tags else "None"

    df_q12["persona_combo"] = df_q12.apply(label_persona, axis=1)

    # Average spend per persona combo
    combo_avg = (
        df_q12.groupby("persona_combo")["lifetime_spend_iap"]
        .mean()
        .reset_index()
        .rename(columns={"lifetime_spend_iap": "avg_spend"})
    )
    combo_avg["avg_spend"] = combo_avg["avg_spend"].round(2)

    st.subheader("🌳 Treemap of Avg Spend by Persona Combination")

    fig = px.treemap(
        combo_avg,
        path=[px.Constant(""), "persona_combo"],
        values="avg_spend",
        color="avg_spend",
        color_continuous_scale="viridis",
        title="Avg Spend by Persona Combination",
        hover_data={"persona_combo": True, "avg_spend": True}
    )

    fig.update_traces(
        textinfo="label+value",
        hovertemplate="<b>%{label}</b><br>Avg Spend: $%{value}<extra></extra>"
    )

    fig.update_layout(margin=dict(t=40, l=10, r=10, b=10))
    st.plotly_chart(fig)

    with st.expander("📄 View Raw Persona Data"):
        st.dataframe(df_q12[["user_data.user_id", "persona_combo", "lifetime_spend_iap"]])
