import streamlit as st
import requests
import plotly.express as px

st.set_page_config(
    page_title="Dozee Alert Dashboard",
    page_icon="🏥",
    layout="wide"
)

API_BASE_URL = "http://127.0.0.1:8000"


def get_api(endpoint, params=None):
    response = requests.get(
        f"{API_BASE_URL}{endpoint}",
        params=params,
        timeout=10
    )
    response.raise_for_status()
    return response.json()


# -----------------------------
# Header
# -----------------------------

st.title("🏥 Dozee Vital Alert Operations Dashboard")

st.caption(
    "Monitor alert volume, response performance, SLA breaches "
    "and operational anomalies."
    "This dashboard is intended for operational and analytical review. "
    "It does not replace clinical judgment or patient-care decisions."
)


# -----------------------------
# Backend connection
# -----------------------------

try:
    summary = get_api("/api/summary")
    st.success("Backend API connected")
except Exception as e:
    st.error(f"Unable to connect to backend API: {e}")
    st.stop()


# -----------------------------
# Filters
# -----------------------------

st.sidebar.header("Filters")

facility = st.sidebar.selectbox(
    "Facility",
    ["All", "F001", "F002", "F003"]
)

severity = st.sidebar.selectbox(
    "Severity",
    ["All", "High", "Medium", "Low"]
)

ward = st.sidebar.selectbox(
    "Ward",
    ["All", "General", "ICU", "CCU", "Pediatric"]
)

facility_param = None if facility == "All" else facility
severity_param = None if severity == "All" else severity
ward_param = None if ward == "All" else ward

st.sidebar.divider()

st.sidebar.caption(
    "Use filters to explore alert performance across "
    "facilities, wards and severity levels."
)

# -----------------------------
# Response metrics
# -----------------------------

metrics = get_api(
    "/api/response-metrics",
    {
        "facility": facility_param,
        "severity": severity_param,
        "ward": ward_param
    }
)


# -----------------------------
# KPI cards
# -----------------------------

st.subheader("Alert Performance")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Alerts",
    f"{metrics['total_alerts']:,}"
)

col2.metric(
    "Abandoned Alerts",
    f"{metrics['abandoned_alerts']:,}",
    f"{metrics['abandoned_rate']}%"
)

col3.metric(
    "Median Time to Open",
    f"{metrics['median_time_to_open_min']:.2f} min"
)

col4.metric(
    "TTO SLA Breach",
    f"{metrics['tto_sla_breach_rate']:.1f}%"
)


# -----------------------------
# SLA section
# -----------------------------

st.subheader("SLA Performance")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Time-to-Open SLA",
        f"{metrics['tto_sla_breach_rate']:.1f}% breached",
        f"Target: ≤ {metrics['tto_sla_minutes']} min"
    )

with col2:
    st.metric(
        "Resolution SLA",
        f"{metrics['resolution_sla_breach_rate']:.1f}% breached",
        f"Target: ≤ {metrics['resolution_sla_minutes']} min"
    )


# -----------------------------
# Current filter
# -----------------------------

st.info(
    f"Showing analysis for "
    f"**{facility if facility != 'All' else 'all facilities'}**, "
    f"**{severity if severity != 'All' else 'all severities'}**, "
    f"**{ward if ward != 'All' else 'all wards'}**."
)

# -----------------------------
# Operational Workload Analysis
# -----------------------------

st.divider()

st.subheader("Operational Workload")


# Get workload data
facility_data = get_api(
    "/api/workload",
    {"group_by": "facility"}
)["results"]

ward_data = get_api(
    "/api/workload",
    {"group_by": "ward"}
)["results"]

nurse_data = get_api(
    "/api/workload",
    {"group_by": "nurse"}
)["results"]

hour_data = get_api(
    "/api/workload",
    {"group_by": "hour"}
)["results"]


# -----------------------------
# Facility workload
# -----------------------------

col1, col2 = st.columns(2)

with col1:

    st.markdown("#### Facility Alert Volume")

    fig = px.bar(
        facility_data,
        x="group",
        y="total_alerts",
        text="total_alerts",
        labels={
            "group": "Facility",
            "total_alerts": "Alerts"
        }
    )

    fig.update_layout(
        showlegend=False,
        height=350
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key = "facility_volume"
    )


with col2:

    st.markdown("#### Facility Abandonment Rate")

    fig = px.bar(
        facility_data,
        x="group",
        y="abandonment_rate",
        text="abandonment_rate",
        labels={
            "group": "Facility",
            "abandonment_rate": "Abandonment Rate (%)"
        }
    )

    fig.update_layout(
        showlegend=False,
        height=350
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key = "facility_abandonment"
    )


# -----------------------------
# Ward workload
# -----------------------------

st.markdown("#### Ward Workload")

fig = px.bar(
    ward_data,
    x="group",
    y="total_alerts",
    text="total_alerts",
    labels={
        "group": "Ward",
        "total_alerts": "Alerts"
    }
)

fig.update_layout(
    showlegend=False,
    height=350
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key = "ward_workload"
)


# -----------------------------
# Nurse workload
# -----------------------------

st.markdown("#### Nurse Alert Handling")

nurse_sorted = sorted(
    nurse_data,
    key=lambda x: x["abandonment_rate"],
    reverse=True
)

fig = px.bar(
    nurse_sorted,
    x="group",
    y="abandonment_rate",
    text="abandonment_rate",
    labels={
        "group": "Nurse",
        "abandonment_rate": "Abandonment Rate (%)"
    }
)

fig.update_layout(
    xaxis_tickangle=-45,
    showlegend=False,
    height=450
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key = "nurse_abandonment"

)


# -----------------------------
# Hourly alert volume
# -----------------------------

st.markdown("#### Alert Volume by Hour")

hour_sorted = sorted(
    hour_data,
    key=lambda x: int(x["group"])
)

for item in hour_sorted:
    item["hour_label"] = f"{int(item['group']):02d}:00"

fig = px.line(
    hour_sorted,
    x="hour_label",
    y="total_alerts",
    markers=True,
    labels={
        "hour_label": "Hour of Day",
        "total_alerts": "Alerts"
    }
)

fig.update_layout(
    height=400
)

st.plotly_chart(
    fig,
    use_container_width=True,
    key="hourly_alert_volume"
)

# -----------------------------
# Data Quality & Anomalies
# -----------------------------

st.divider()

st.subheader("⚠️ Data Quality & Operational Anomalies")

anomaly_data = get_api("/api/anomalies")

anomaly_summary = anomaly_data["summary"]


# -----------------------------
# Anomaly KPI cards
# -----------------------------

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Abandoned",
    anomaly_summary["abandoned_alerts"]
)

col2.metric(
    "Negative Timestamps",
    anomaly_summary["negative_timestamps"]
)

col3.metric(
    "Ghost Alerts",
    anomaly_summary["ghost_alerts"]
)

col4.metric(
    "Invalid SpO₂",
    anomaly_summary["invalid_spo2"]
)

col5.metric(
    "Ack Without Open",
    anomaly_summary["acknowledged_without_open"]
)


# -----------------------------
# Explanation
# -----------------------------

st.markdown(
    """
    **Audit flags identified in the source data:**

    - **Abandoned alerts:** alerts without an acknowledgement timestamp
    - **Negative timestamps:** alerts opened before they were created
    - **Ghost alerts:** alerts acknowledged more than 24 hours after creation
    - **Invalid SpO₂:** SpO₂ values above the physiological maximum of 100%
    - **Acknowledged without open:** alerts acknowledged without a recorded open event
    """
)


# -----------------------------
# Anomaly details
# -----------------------------

anomaly_options = {
    "Abandoned Alerts": "abandoned_alerts",
    "Negative Timestamps": "negative_timestamps",
    "Ghost Alerts (>24h)": "ghost_alerts",
    "Invalid SpO₂": "invalid_spo2",
    "Acknowledged Without Open": "acknowledged_without_open"
}

selected_anomaly = st.selectbox(
    "Inspect anomaly records",
    list(anomaly_options.keys())
)

selected_key = anomaly_options[selected_anomaly]

anomaly_records = anomaly_data["anomalies"][selected_key]

if anomaly_records:

    st.dataframe(
        anomaly_records,
        use_container_width=True
    )

else:

    st.success("No records found for this anomaly type.")

# -----------------------------
# Alert Explorer
# -----------------------------

st.divider()

st.subheader("🔎 Alert Explorer")

st.caption(
    "Drill down into individual alerts using the selected filters."
)

alert_params = {}

if facility_param:
    alert_params["facility"] = facility_param

if severity_param:
    alert_params["severity"] = severity_param

if ward_param:
    alert_params["ward"] = ward_param


alerts_response = get_api(
    "/api/alerts",
    alert_params
)

alerts = alerts_response["alerts"]

st.write(
    f"**{len(alerts):,} alerts** match the current filters."
)

if alerts:

    st.dataframe(
        alerts,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No alerts match the selected filters.")

# -----------------------------
# Key Findings
# -----------------------------

st.divider()

st.subheader("📌 Key Operational Findings")

st.markdown(
    """
    ### 1. High-severity alerts are not being prioritized

    High-severity alerts show a similar response pattern to lower-severity
    alerts, indicating that severity-based prioritization may not currently
    translate into faster operational response.

    **Action:** Review high-severity alert routing and escalation workflows.

    ---

    ### 2. Facility F003 is a major abandonment outlier

    F003 has a substantially higher abandonment rate than F001 and F002,
    despite having a comparable alert volume.

    **Action:** Investigate facility-level workflow, staffing, connectivity
    and alert-delivery processes.

    ---

    ### 3. Alert abandonment is concentrated among specific handlers

    A small number of nurses show substantially higher abandonment rates
    than the rest of the handling group.

    **Action:** Investigate workload, shift patterns and workflow conditions
    before drawing conclusions about individual performance.

    ---

    ### 4. Alert volume peaks around 06:00

    The 06:00 hour records the highest alert volume in the dataset.

    **Action:** Review staffing and alert-handling capacity around this
    period to determine whether additional coverage is required.

    ---

    ### 5. Source-data quality requires monitoring

    The dataset contains abandoned alerts, negative timestamps,
    unusually long acknowledgement times and invalid SpO₂ values.

    **Action:** Introduce automated data-quality checks before using these
    records for downstream clinical or operational analysis.
    """
)