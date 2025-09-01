import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import plotly.express as px
import altair as alt

from utils.data_loader import load_main_data


def render():
    st.title("Q11: Spend-Based User Clusters")

    df = load_main_data()

    # Compute spend features
    df_q11 = (
        df.groupby("user_data.user_id")
          .agg(
              total_spend=("adjust_post_events_iap.adj_converted_usd_value_dimension", "sum"),
              purchase_count=("adjust_post_events_iap.adj_converted_usd_value_dimension", "count")
          )
          .reset_index()
    )
    df_q11["avg_purchase_value"] = df_q11["total_spend"] / df_q11["purchase_count"]

    # Filter high-volume purchasers
    df_q11_filtered = df_q11[df_q11["purchase_count"] < 200].copy()

    # Scale features
    features = ["total_spend", "purchase_count", "avg_purchase_value"]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_q11_filtered[features])

    # Run KMeans
    kmeans = KMeans(n_clusters=3, random_state=42)
    df_q11_filtered["cluster"] = kmeans.fit_predict(X_scaled)

    # Assign spend segments
    cluster_means = df_q11_filtered.groupby("cluster")["total_spend"].mean().sort_values()
    cluster_map = {
        cluster_means.index[0]: "Minnow",
        cluster_means.index[1]: "Dolphin",
        cluster_means.index[2]: "Whale"
    }
    df_q11_filtered["segment"] = df_q11_filtered["cluster"].map(cluster_map)

    st.subheader("📊 2D Cluster Scatter")
    chart = alt.Chart(df_q11_filtered).mark_circle(size=60, opacity=0.7).encode(
        x=alt.X("purchase_count:Q", title="Purchase Count"),
        y=alt.Y("total_spend:Q", title="Total Spend (USD)"),
        color=alt.Color("segment:N", scale=alt.Scale(
            domain=["Minnow", "Dolphin", "Whale"],
            range=["blue", "green", "orange"]
        )),
        tooltip=["user_data.user_id", "purchase_count", "total_spend", "avg_purchase_value", "segment"]
    ).properties(
        width=600,
        height=400,
        title="User Segments by Spend Behavior"
    ).interactive()
    st.altair_chart(chart)

    st.subheader("🌐 3D Spend Behavior")
    fig = px.scatter_3d(
        df_q11_filtered,
        x="purchase_count",
        y="total_spend",
        z="avg_purchase_value",
        color="segment",
        color_discrete_map={"Minnow": "blue", "Dolphin": "green", "Whale": "orange"},
        title="3D Spend Clustering",
        opacity=0.7
    )
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=30))
    st.plotly_chart(fig)

    with st.expander("🔍 View Clustered User Data"):
        st.dataframe(df_q11_filtered)
