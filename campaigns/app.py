import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as pc

# --- Page Config ---
st.set_page_config(page_title="Campaign Trend Clustering", layout="wide")
st.title("📊 Campaign Trend")
st.markdown("Theme can be changes in settings (light/dark)")
st.markdown("Clustering campaigns based on **CPI**, **CTR**, and **IPM** trends. This narrows the unique patterns from the bulk campaigns.")

# --- Load Local File ---
# ⛳ Change this to your actual file path
file_path = "../data/cpi_data_all.csv"  # <-- UPDATE THIS
df = pd.read_csv(file_path)
df["created_at"] = pd.to_datetime(df["created_at"])

st.success(f"✅ Data loaded from: `{file_path}`")
st.write(df.head())

# --- Configuration ---
st.markdown("The number of clusters can be changed from the slider below.")
n_clusters = st.slider("Number of clusters", 2, 10, 6)
metrics = ["cpi", "ctr", "ipm"]

# --- Pivot and Normalize Each Metric ---
pivot_tables = {}
for metric in metrics:
    pivot = df.pivot_table(index="file_id", columns="created_at", values=metric)
    pivot = pivot.fillna(method="ffill", axis=1).fillna(method="bfill", axis=1)
    pivot_norm = (pivot - pivot.mean(axis=1).values[:, None]) / pivot.std(axis=1).values[:, None]
    pivot_tables[metric] = pivot_norm

# --- Combine Metrics for Clustering ---
combined = pd.concat(pivot_tables.values(), axis=1).fillna(0)
campaign_ids = combined.index.tolist()

# --- KMeans Clustering ---
X = combined.values
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
labels = kmeans.fit_predict(X)

# --- Select 1 Representative per Cluster ---
rep_campaigns = []
for cluster_id in range(n_clusters):
    cluster_indices = np.where(labels == cluster_id)[0]
    if len(cluster_indices) == 0:
        continue
    center = kmeans.cluster_centers_[cluster_id]
    distances = [np.linalg.norm(X[i] - center) for i in cluster_indices]
    best_idx = cluster_indices[np.argmin(distances)]
    if campaign_ids[best_idx] == "F0962QRKB7H":
        continue
    rep_campaigns.append(campaign_ids[best_idx])

# --- Plotting ---
palette = pc.qualitative.Set2
color_map = {cid: palette[i % len(palette)] for i, cid in enumerate(rep_campaigns)}

fig = make_subplots(
    rows=len(metrics), cols=1, shared_xaxes=True,
    subplot_titles=[metric.upper() for metric in metrics],
    vertical_spacing=0.07
)

for row_idx, metric in enumerate(metrics, start=1):
    for campaign_id in rep_campaigns:
        df_c = df[df["file_id"] == campaign_id].sort_values("created_at")
        df_c = df_c[["created_at", metric]].dropna()
        if df_c.empty:
            continue

        # Apply rolling average smoothing
        df_c["smoothed"] = df_c[metric].rolling(window=3, center=True, min_periods=1).mean()

        # Join with spend for annotations
        df_spend = df[df["file_id"] == campaign_id][["created_at", "spend"]].dropna()
        df_c = df_c.merge(df_spend, on="created_at", how="left")

        # Spend annotations every 3rd point
        spend_labels = [
            f"${s:.0f}" if pd.notna(s) and i % 3 == 0 else ""
            for i, s in enumerate(df_c["spend"])
        ]

        fig.add_trace(
            go.Scatter(
                x=df_c["created_at"],
                y=df_c["smoothed"],
                mode="lines+markers+text",
                name=campaign_id if row_idx == 1 else None,
                line=dict(color=color_map[campaign_id], width=3),
                marker=dict(size=5),
                text=spend_labels,
                textposition="top center",
                showlegend=(row_idx == 1)
            ),
            row=row_idx, col=1
        )

fig.update_layout(
    height=900,
    title="📈 Distinct Campaign Trends (Cluster Representatives)",
    hovermode="x unified",
    legend_title="Campaign ID",
    margin=dict(t=80, b=50, r=150)
)

fig.update_xaxes(title_text="Date", row=len(metrics), col=1)
for i, col in enumerate(metrics, start=1):
    fig.update_yaxes(title_text=col.upper(), row=i, col=1)

st.plotly_chart(fig, use_container_width=True)
