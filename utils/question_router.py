import streamlit as st

def render_question(question_text):
    try:
        qnum = int(question_text.split(":")[0].replace("Q", ""))
    except:
        st.warning("Invalid question format")
        return

    if qnum == 1:
        from questions.purchase.q1_user_levels import render
    elif qnum == 2:
        from questions.purchase.q2_time_to_first_purchase import render
    elif qnum == 3:
        from questions.purchase.q3_most_purchased_items import render
    elif qnum == 4:
        from questions.purchase.q4_purchasers_session_count import render
    elif qnum == 5:
        from questions.purchase.q5_repeat_vs_single import render
    elif qnum == 6:
        from questions.purchase.q6_purchase_sequence import render
    elif qnum == 7:
        from questions.purchase.q7_user_purchase_frequency import render
    elif qnum == 8:
        from questions.purchase.q8_lifecycle_vs_purchases import render
    elif qnum == 9:
        from questions.purchase.q9_ltv_first_purchase_grouping import render
    elif qnum == 10:
        from questions.purchase.q10_session_vs_spend import render
    elif qnum == 11:
        from questions.segmentation.q11_user_spend import render
    elif qnum == 12:
        from questions.segmentation.q12_persona_analysis import render
    elif qnum == 13:
        from questions.segmentation.q13_engagement_correlation import render
    elif qnum == 14:
        from questions.segmentation.q14_engagement_by_spend_tier import render
    elif 18 <= qnum <= 22:
        from questions.ad_monetization.q18_to_q22_placeholder import render
    elif 23 <= qnum <= 26:
        from questions.intent_conversion.q23_to_q26_placeholder import render
    elif 27 <= qnum <= 29:
        from questions.timing_session.q27_to_q29_placeholder import render
    elif 30 <= qnum <= 33:
        from questions.churn_lifecycle.q30_to_q33_placeholder import render
    elif 34 <= qnum <= 39:
        from questions.gameplay_economy.q34_to_q39_placeholder import render
    elif 40 <= qnum <= 42:
        from questions.predictive.q40_to_q42_placeholder import render
    elif 43 <= qnum <= 47:
        from questions.cohort_funnel.q43_to_q47_placeholder import render
    else:
        render = lambda: st.warning("Question not implemented.")

    render()


