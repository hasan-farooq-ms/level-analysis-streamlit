import streamlit as st
import pandas as pd
import altair as alt
from utils.data_loader import load_main_data

def render():
    df = load_main_data()
    st.title("At what levels do most purchases occur?")

    top_n = st.slider("Level Slider", min_value=5, max_value=50, value=30)
    metric = st.radio("Choose metric:", ["Percentage", "Count"])

    counts = df['adjust_post_events_iap.user_level_linear'].value_counts()
    if metric == "Percentage":
        data = round((counts / counts.sum()) * 100, 2)
    else:
        data = counts

    plot_data = data.head(top_n).sort_index()
    chart_data = plot_data.reset_index()
    chart_data.columns = ['User Level', 'Purchases']

    chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('User Level:O', sort=None),
        y=alt.Y('Purchases:Q'),
        tooltip=['User Level', 'Purchases']
    ).properties(
        title=f"{metric} of Purchases by Level LayoutID",
        width=800,
        height=400
    )

    st.altair_chart(chart, use_container_width=True)

    st.markdown("### Conclusion")
    if metric == "Percentage":
        st.write(f"The top {top_n} levels account for **{plot_data.sum():.1f}%** of all purchases.")
    else:
        st.write(f"The top {top_n} levels account for **{int(plot_data.sum())}** total purchases.")

    with st.expander("Show raw data table"):
        st.dataframe(chart_data)

