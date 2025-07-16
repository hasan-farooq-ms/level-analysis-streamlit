import streamlit as st
from streamlit_option_menu import option_menu
from utils.question_router import render_question

st.set_page_config(page_title="Shop Analysis", layout="wide")

CATEGORY_QUESTIONS = {
    "🎯 Purchase Behavior": [
        "Q1: At which user levels do purchases occur?",
        "Q2: Time between install and first purchase?",
        "Q3: What are the most purchased items?",
        "Q4: What are the top countries among purchasers?",
        "Q5: How many users make just one purchase vs. repeat purchases?",
        "Q6: How does the sequence of purchases evolve?",
        "Q7: What’s the average purchase frequency per user type?",
        "Q8: Do high-value purchases happen at higher levels or earlier in the lifecycle?",
        "Q9: What is the lifetime value (LTV) segmented by first purchase level or product?",
        "Q10: How do session counts relate to total IAP spend?",
    ],
    "👤 Segmentation": [f"Q{n}: Placeholder" for n in range(12, 18)],
    "💸 Ad Monetization": [f"Q{n}: Placeholder" for n in range(18, 23)],
    "🧪 Purchase Intent": [f"Q{n}: Placeholder" for n in range(23, 27)],
    "⏳ Timing & Sessions": [f"Q{n}: Placeholder" for n in range(27, 30)],
    "📉 Churn & Lifecycle": [f"Q{n}: Placeholder" for n in range(30, 34)],
    "🎮 Gameplay": [f"Q{n}: Placeholder" for n in range(34, 40)],
    "📐 Predictive Modeling": [f"Q{n}: Placeholder" for n in range(40, 43)],
    "🔍 Cohort & Funnel": [f"Q{n}: Placeholder" for n in range(43, 48)],
}

# with st.sidebar:
#     category = option_menu("Shop Insights", list(CATEGORY_QUESTIONS.keys()), 
#           icons=["cart", "person", "dollar-sign", "flask", "clock", "bar-chart", "gamepad", "cpu", "search"], default_index=0)
#     question = st.selectbox("Select a question", CATEGORY_QUESTIONS[category])

with st.sidebar:
    selected_category = option_menu(
        "Sections",
        options=list(CATEGORY_QUESTIONS.keys()),
        default_index=0
    )

st.header(f"{selected_category}")
selected_question = st.selectbox("Select a question", CATEGORY_QUESTIONS[selected_category])
render_question(selected_question)

# if question:
#     render_question(question)