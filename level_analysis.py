import pandas as pd
import seaborn as sns
import numpy as np
from matplotlib import pyplot as plt
import plotly.express as px
import streamlit as st
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

df = pd.read_csv("./data/level-details.csv")

del df["Event Data Unq Users Level Started (Before X Days)"]
del df["Event Data Unq Users Level Completed (Before X Days)"]

cols = [
    "Event Data Level Sequence In Catalog", "Avg Stacks Placed to Complete", "Avg Stacks Placed to Fail", 
    "Level Churn %", "Level Fail %",
    "Retry Ratio", "Unique Level Fail %", "Avg Play on used", "Avg Powerup Used", "Rv Slot % (unique)",
    "Total RV Revenue / User", "Total Ad Revenue / User", "IAP Revenue / User", "ARPPU",
    "Lvl complete % (1st Attempt)", "Lvl complete % (2nd Attempt)", "Lvl complete % (3+ Attempt)",
    "Coin Sink", "Unq Users level start", "Unq Users level complete"
]

df = df[cols]

for col in df.columns:
    if df[col].dtype == "object":
        if df[col].astype(str).str.contains(r'[%$,]').any():
            cleaned = (
                df[col].astype(str)
                .str.replace(r'[$,%]', '', regex=True)
                .str.replace(',', '', regex=True)
            )
            df[col] = pd.to_numeric(cleaned, errors="coerce")

df["Avg Coin Sink"] = round(df["Coin Sink"]/df["Unq Users level start"], 2)

st.title("Level Analysis")

st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "Go to section:",
    [
        "Data Preview",
        "Exploration",
        "Correlations",
        "Outlier Levels",
        "Level Clustering"
    ]
)

level_col = "Event Data Level Sequence In Catalog"
all_columns = df.columns.tolist()
numeric_columns = [c for c in df.columns if df[c].dtype in ["int64", "float64"]]

if section == "Data Preview":
    st.subheader("📋 Data Preview")
    preview_size = st.slider("Rows to display", min_value=5, max_value=len(df), value=5, step=5)
    st.dataframe(df.head(preview_size))

elif section == "Exploration":
    st.header("Exploration")

    xcol = st.selectbox(
        "Select column for X-axis",
        [c for c in all_columns if c != level_col],
        index=0
    )

    ycol = st.selectbox(
        "Select column for Y-axis",
        [c for c in numeric_columns if c != level_col],
        index=0
    )

    filter_col = st.selectbox("Select column to filter by", numeric_columns, index=0)
    col_min, col_max = df[filter_col].min(), df[filter_col].max()
    slider_vals = st.slider(f"Filter {filter_col} range", float(col_min), float(col_max), (float(col_min), float(col_max)))

    remove_x_outliers = st.checkbox("Remove X-axis outliers (1% - 99%)")
    remove_y_outliers = st.checkbox("Remove Y-axis outliers (1% - 99%)")
    sort_x = st.checkbox("Sort X-axis (ascending)", value=True)
    chart_type = st.radio("Chart type", ["Scatter", "Line"], index=0)
    trendline_type = st.radio("Add Regression Trendline", ["None", "Linear", "Curve (auto)"], index=0)

    dff = df[(df[filter_col] >= slider_vals[0]) & (df[filter_col] <= slider_vals[1])]

    if remove_x_outliers:
        lower, upper = dff[xcol].quantile(0.01), dff[xcol].quantile(0.99)
        dff = dff[(dff[xcol] >= lower) & (dff[xcol] <= upper)]

    if remove_y_outliers:
        lower, upper = dff[ycol].quantile(0.01), dff[ycol].quantile(0.99)
        dff = dff[(dff[ycol] >= lower) & (dff[ycol] <= upper)]

    if sort_x:
        dff = dff.sort_values(xcol)

    if chart_type == "Scatter":
        fig = px.scatter(dff, x=xcol, y=ycol, opacity=0.7)
        fig.update_traces(marker=dict(color="royalblue", size=6), selector=dict(mode="markers"))
    else:
        dff_line = dff.groupby(xcol)[ycol].mean().reset_index()
        fig = px.line(dff_line, x=xcol, y=ycol, markers=True)
        fig.update_traces(line=dict(color="royalblue", width=2))

    if trendline_type != "None" and len(dff) > 2:
        X = np.array(dff[xcol]).reshape(-1, 1)
        y = np.array(dff[ycol])

        best_degree = 1
        best_r2 = -1
        best_pred = None

        lin_model = LinearRegression().fit(X, y)
        X_sorted = np.linspace(X.min(), X.max(), 200).reshape(-1, 1)
        y_lin_pred = lin_model.predict(X_sorted)
        r2_lin = r2_score(y, lin_model.predict(X))
        best_degree, best_r2, best_pred = 1, r2_lin, (X_sorted.ravel(), y_lin_pred)

        if trendline_type == "Curve (auto)":
            for degree in [2, 3]:
                poly = PolynomialFeatures(degree=degree)
                X_poly = poly.fit_transform(X)
                poly_model = LinearRegression().fit(X_poly, y)
                y_poly_pred = poly_model.predict(X_poly)
                r2_poly = r2_score(y, y_poly_pred)

                if r2_poly > best_r2:
                    X_sorted = np.linspace(X.min(), X.max(), 200).reshape(-1, 1)
                    best_pred = (X_sorted.ravel(), poly_model.predict(poly.transform(X_sorted)))
                    best_degree, best_r2 = degree, r2_poly

        y_pred = best_pred[1]
        y_std = np.std(y - np.interp(X.ravel(), best_pred[0], y_pred))
        y_upper = y_pred + y_std
        y_lower = y_pred - y_std

        fig.add_scatter(x=best_pred[0], y=y_pred, mode="lines",
                        line=dict(color="firebrick", width=3),
                        name=f"Best fit (deg {best_degree}, R²={best_r2:.2f})")

        fig.add_scatter(x=np.concatenate([best_pred[0], best_pred[0][::-1]]),
                        y=np.concatenate([y_upper, y_lower[::-1]]),
                        fill="toself",
                        fillcolor="rgba(255,0,0,0.2)",
                        line=dict(color="rgba(255,0,0,0)"),
                        name="Confidence band")

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Level Sequence Views")
    dff_level = df.sort_values(level_col)

    col1, col2 = st.columns(2)

    with col1:
        if xcol in numeric_columns:
            fig_x = px.line(
                dff_level.groupby(level_col)[xcol].mean().reset_index(),
                x=level_col, y=xcol, markers=True,
                color_discrete_sequence=["firebrick"]
            )
            fig_x.update_traces(line=dict(width=2))
            st.plotly_chart(fig_x, use_container_width=True)
        else:
            st.info(f"X-axis column '{xcol}' is not numeric, skipping Level vs X plot.")

    with col2:
        fig_y = px.line(
            dff_level.groupby(level_col)[ycol].mean().reset_index(),
            x=level_col, y=ycol, markers=True,
            color_discrete_sequence=["seagreen"]
        )
        fig_y.update_traces(line=dict(width=2))
        st.plotly_chart(fig_y, use_container_width=True)

elif section == "Correlations":
    st.header("Correlations")

    min_level, max_level = int(df[level_col].min()), int(df[level_col].max())
    level_range = st.slider("Select Level Range", min_level, max_level, (min_level, max_level))

    df_corr = df[(df[level_col] >= level_range[0]) & (df[level_col] <= level_range[1])]
    numeric_cols_corr = [c for c in numeric_columns if c != level_col]
    corr = df_corr[numeric_cols_corr].corr()

    threshold = st.slider("Correlation Threshold", 0.0, 1.0, 0.6, 0.05)
    mask = (corr.abs() >= threshold) & (corr != 1.0)
    filtered_corr = corr.where(mask)
    mask_upper = np.triu(np.ones_like(filtered_corr, dtype=bool))

    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        filtered_corr,
        mask=mask_upper,
        cmap="coolwarm",
        center=0,
        annot=True,
        fmt=".2f",
        linewidths=0.5,
        cbar_kws={"shrink": 0.7},
        ax=ax
    )
    ax.set_title(f"Correlation Heatmap (Levels {level_range[0]} – {level_range[1]}, Threshold |r| ≥ {threshold:.2f})")
    st.pyplot(fig)

elif section == "Outlier Levels":
    st.header("Outlier Levels")
    outlier_candidates = [c for c in numeric_columns if c != level_col]
    outlier_metric = st.selectbox("Select metric for outlier detection", outlier_candidates)
    method = st.radio("Detection Method", ["Z-Score", "IQR (Percentiles)"], index=0)
    df_out = df.copy()

    if method == "Z-Score":
        mean_val = df_out[outlier_metric].mean()
        std_val = df_out[outlier_metric].std()
        df_out["zscore"] = (df_out[outlier_metric] - mean_val) / std_val
        outliers = df_out[abs(df_out["zscore"]) > 3]
        st.write(f"Outliers detected: {len(outliers)} levels")
    elif method == "IQR (Percentiles)":
        Q1 = df_out[outlier_metric].quantile(0.15)
        Q3 = df_out[outlier_metric].quantile(0.85)
        IQR = Q3 - Q1
        lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
        outliers = df_out[(df_out[outlier_metric] < lower) | (df_out[outlier_metric] > upper)]
        st.write(f"Outliers detected: {len(outliers)} levels")

    if not outliers.empty:
        fig_out = px.scatter(
            df_out,
            x=level_col, y=outlier_metric,
            opacity=0.6,
            title=f"Outlier Detection on {outlier_metric}"
        )
        fig_out.add_scatter(
            x=outliers[level_col], y=outliers[outlier_metric],
            mode="markers",
            marker=dict(color="red", size=10, symbol="x"),
            name="Outliers"
        )
        st.plotly_chart(fig_out, use_container_width=True)
        st.subheader("Outlier Levels")
        st.dataframe(outliers[[level_col, outlier_metric]].sort_values(outlier_metric))
    else:
        st.info("✅ No strong outliers detected.")

elif section == "Level Clustering":
    st.header("Level Clustering")
    cluster_features = [c for c in numeric_columns if c != level_col]
    selected_features = st.multiselect(
        "Select features for clustering",
        cluster_features,
        default=["Level Fail %", "Retry Ratio", "Level Churn %"]
    )

    if len(selected_features) >= 2:
        X = df[selected_features].dropna()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        k = st.slider("Number of clusters (k)", 2, 5, 3)
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        df["Cluster"] = clusters.astype(str)
        st.success(f"✅ Clustering complete! Found {k} clusters.")
        st.subheader("Cluster Summary")
        cluster_summary = df.groupby("Cluster")[selected_features].mean().round(2)
        st.dataframe(cluster_summary)
        st.subheader("Level Sequence with Clusters")
        fig_seq = px.scatter(
            df,
            x=level_col,
            y=selected_features[0],
            color="Cluster",
            hover_data=[level_col] + selected_features,
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig_seq.update_traces(marker=dict(size=8, opacity=0.8))
        st.plotly_chart(fig_seq, use_container_width=True)
    else:
        st.info("Please select at least 2 features for clustering.")
