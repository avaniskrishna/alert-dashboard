import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Dozee Alert Dashboard",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Dozee Vital Alert Operations Dashboard")

st.markdown(
    """
    ### Alert Monitoring & Operational Analysis
    Interactive analysis of vital alerts, response performance,
    SLA breaches and operational anomalies.
    """
)

st.success("Streamlit application is running successfully!")