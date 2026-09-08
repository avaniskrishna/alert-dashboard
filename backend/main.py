from fastapi import FastAPI
from backend.database import get_connection

app = FastAPI(
    title="Dozee Alert Analytics API",
    description="Backend APIs for the Dozee Vital Alert Operations Dashboard",
    version="1.0"
)


@app.get("/")
def root():
    return {
        "message": "Dozee Alert Analytics API is running"
    }


@app.get("/api/summary")
def summary():
    conn = get_connection()

    total_alerts = conn.execute(
        "SELECT COUNT(*) FROM alerts"
    ).fetchone()[0]

    conn.close()

    return {
        "total_alerts": total_alerts
    }

@app.get("/api/alerts")
def get_alerts(
    facility: str | None = None,
    severity: str | None = None,
    ward: str | None = None,
    vital: str | None = None
):
    conn = get_connection()

    query = "SELECT * FROM alerts WHERE 1=1"
    params = []

    if facility:
        query += " AND facility_id = ?"
        params.append(facility)

    if severity:
        query += " AND severity = ?"
        params.append(severity)

    if ward:
        query += " AND ward = ?"
        params.append(ward)

    if vital:
        query += " AND vital_name = ?"
        params.append(vital)

    query += " ORDER BY creation_time DESC"

    rows = conn.execute(query, params).fetchall()

    conn.close()

    return {
        "count": len(rows),
        "alerts": [dict(row) for row in rows]
    }

from datetime import datetime


def parse_time(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


@app.get("/api/response-metrics")
def response_metrics(
    facility: str | None = None,
    severity: str | None = None,
    ward: str | None = None
):
    conn = get_connection()

    query = "SELECT * FROM alerts WHERE 1=1"
    params = []

    if facility:
        query += " AND facility_id = ?"
        params.append(facility)

    if severity:
        query += " AND severity = ?"
        params.append(severity)

    if ward:
        query += " AND ward = ?"
        params.append(ward)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    time_to_open = []
    time_to_ack = []
    total_resolution = []

    abandoned_count = 0
    invalid_timestamp_count = 0

    for row in rows:
        creation = parse_time(row["creation_time"])
        opened = parse_time(row["opened_at"])
        acknowledged = parse_time(row["acknowledged_at"])

        # Abandoned alert
        if acknowledged is None:
            abandoned_count += 1

        # Time to Open
        if creation and opened:
            tto = (opened - creation).total_seconds() / 60

            # Ignore negative timestamps and >24h ghost alerts
            if 0 <= tto <= 1440:
                time_to_open.append(tto)
            else:
                invalid_timestamp_count += 1

        # Time to Acknowledge
        if creation and acknowledged:
            tta = (acknowledged - creation).total_seconds() / 60

            if 0 <= tta <= 1440:
                time_to_ack.append(tta)

        # Total Resolution Time
        if creation and acknowledged:
            resolution = (
                acknowledged - creation
            ).total_seconds() / 60

            if 0 <= resolution <= 1440:
                total_resolution.append(resolution)

    def median(values):
        if not values:
            return None

        values = sorted(values)
        n = len(values)

        if n % 2:
            return round(values[n // 2], 2)

        return round(
            (values[n // 2 - 1] + values[n // 2]) / 2,
            2
        )

    # SLA calculations
    tto_breaches = sum(value > 2 for value in time_to_open)
    resolution_breaches = sum(
        value > 10 for value in total_resolution
    )

    return {
        "total_alerts": len(rows),

        "abandoned_alerts": abandoned_count,
        "abandoned_rate": round(
            abandoned_count / len(rows) * 100, 2
        ) if rows else 0,

        "invalid_timestamp_records": invalid_timestamp_count,

        "valid_time_to_open_records": len(time_to_open),
        "median_time_to_open_min": median(time_to_open),

        "valid_time_to_ack_records": len(time_to_ack),
        "median_time_to_ack_min": median(time_to_ack),

        "valid_resolution_records": len(total_resolution),
        "median_total_resolution_min": median(
            total_resolution
        ),

        "tto_sla_minutes": 2,
        "tto_sla_breaches": tto_breaches,
        "tto_sla_breach_rate": round(
            tto_breaches / len(time_to_open) * 100, 2
        ) if time_to_open else 0,

        "resolution_sla_minutes": 10,
        "resolution_sla_breaches": resolution_breaches,
        "resolution_sla_breach_rate": round(
            resolution_breaches / len(total_resolution) * 100, 2
        ) if total_resolution else 0
    }

@app.get("/api/anomalies")
def get_anomalies():
    conn = get_connection()

    rows = conn.execute(
        "SELECT * FROM alerts"
    ).fetchall()

    conn.close()

    anomalies = {
        "abandoned_alerts": [],
        "negative_timestamps": [],
        "ghost_alerts": [],
        "invalid_spo2": [],
        "acknowledged_without_open": []
    }

    for row in rows:
        alert = dict(row)

        creation = parse_time(row["creation_time"])
        opened = parse_time(row["opened_at"])
        acknowledged = parse_time(row["acknowledged_at"])

        # 1. Abandoned alerts
        if acknowledged is None:
            anomalies["abandoned_alerts"].append(alert)

        # 2. Negative time-to-open / clock drift
        if creation and opened:
            time_to_open = (
                opened - creation
            ).total_seconds() / 60

            if time_to_open < 0:
                anomalies["negative_timestamps"].append({
                    **alert,
                    "time_to_open_min": round(time_to_open, 2)
                })

        # 3. Ghost alerts
        # Match the notebook:
        # acknowledged_at - creation_time > 24 hours
        if creation and acknowledged:
            total_resolution = (
                acknowledged - creation
            ).total_seconds() / 60

            if total_resolution > 24 * 60:
                anomalies["ghost_alerts"].append({
                    **alert,
                    "total_resolution_min": round(
                        total_resolution, 2
                    )
                })

        # 4. Invalid SpO2
        if (
            row["vital_name"] == "SpO2"
            and row["value"] > 100
        ):
            anomalies["invalid_spo2"].append(alert)

        # 5. Acknowledged without opened_at
        if acknowledged and opened is None:
            anomalies["acknowledged_without_open"].append(alert)

    return {
        "summary": {
            "abandoned_alerts": len(
                anomalies["abandoned_alerts"]
            ),
            "negative_timestamps": len(
                anomalies["negative_timestamps"]
            ),
            "ghost_alerts": len(
                anomalies["ghost_alerts"]
            ),
            "invalid_spo2": len(
                anomalies["invalid_spo2"]
            ),
            "acknowledged_without_open": len(
                anomalies["acknowledged_without_open"]
            )
        },
        "anomalies": anomalies
    }

@app.get("/api/workload")
def get_workload(
    group_by: str = "facility"
):
    conn = get_connection()

    allowed_groups = {
        "facility": "facility_id",
        "nurse": "attended_by",
        "ward": "ward",
        "hour": "strftime('%H', creation_time)"
    }

    if group_by not in allowed_groups:
        conn.close()
        return {
            "error": "Invalid group_by. Use facility, nurse, ward, or hour."
        }

    group_column = allowed_groups[group_by]

    query = f"""
        SELECT
            {group_column} AS group_name,
            COUNT(*) AS total_alerts,
            SUM(
                CASE
                    WHEN acknowledged_at IS NULL THEN 1
                    ELSE 0
                END
            ) AS abandoned_alerts
        FROM alerts
        GROUP BY {group_column}
        ORDER BY total_alerts DESC
    """

    rows = conn.execute(query).fetchall()

    conn.close()

    results = []

    for row in rows:
        total = row["total_alerts"]
        abandoned = row["abandoned_alerts"]

        results.append({
            "group": row["group_name"],
            "total_alerts": total,
            "abandoned_alerts": abandoned,
            "abandonment_rate": round(
                abandoned / total * 100, 2
            ) if total else 0
        })

    return {
        "group_by": group_by,
        "results": results
    }