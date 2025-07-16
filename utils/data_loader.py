import pandas as pd
import streamlit as st

@st.cache_data
def load_main_data():
    df = pd.read_csv("./data/shop_qa_without_json.csv")
    return df.dropna(subset=["adjust_post_events_iap.user_level_linear"])