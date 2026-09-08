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

# Load the alert dataset
df = pd.read_csv("alerts (2).csv")

st.subheader("Alert Dataset")

st.write(f"Total records: **{len(df):,}**")

st.dataframe(
    df,
    use_container_width=True
)