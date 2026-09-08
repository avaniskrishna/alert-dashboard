# 🏥 Dozee Vital Alert Operations Dashboard

A full-stack prototype for monitoring hospital vital-alert operations using a database-backed REST API and an interactive Streamlit dashboard.

The project demonstrates an end-to-end architecture:

**CSV → SQLite Database → FastAPI REST APIs → Streamlit Frontend → User**

## 🚀 Live Demo

* **Dashboard:** [https://alertsdashboard.streamlit.app/](https://alertsdashboard.streamlit.app/)
* **Backend API:** [https://alert-dashboard-api.onrender.com/](https://alert-dashboard-api.onrender.com/)
* **Swagger API Docs:** [https://alert-dashboard-api.onrender.com/docs](https://alert-dashboard-api.onrender.com/docs)

---

## 🔄 Data Flow

```text
                    Raw Dataset
                 alerts (2).csv
                        │
                        ▼
               Data Loading Script
                load_database.py
                        │
                        ▼
                 SQLite Database
                    alerts.db
                        │
                        ▼
                 FastAPI Backend
                    main.py
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
      /summary       /alerts     /response-metrics
          │             │             │
          └─────────────┼─────────────┘
                        │
                        ▼
                  REST API Layer
                        │
                        ▼
              Streamlit Frontend
               streamlit_app.py
                        │
                        ▼
                  Interactive UI
                        │
                        ▼
                      User
```

### How the data flows

1. The raw CSV dataset is loaded into SQLite using Python.
2. SQLite acts as the relational data layer.
3. FastAPI exposes the data and analytics through REST APIs.
4. APIs accept query parameters for filtering.
5. Streamlit sends HTTP requests to the FastAPI backend.
6. API responses populate KPIs, tables, and Plotly visualizations.
7. The user interacts with the Streamlit frontend.

---

## 🏗️ System Architecture

```text
┌──────────────────────┐
│      CSV Dataset     │
│   alerts (2).csv     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Data Ingestion     │
│ load_database.py     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   SQLite Database    │
│      alerts.db       │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────┐
│       FastAPI Backend        │
│                              │
│  REST API Endpoints          │
│  ├── /api/summary            │
│  ├── /api/alerts             │
│  ├── /api/response-metrics   │
│  ├── /api/anomalies          │
│  └── /api/workload            │
└──────────────┬───────────────┘
               │
               │ HTTP Requests
               ▼
┌──────────────────────────────┐
│      Streamlit Frontend      │
│                              │
│  Filters                     │
│  KPIs                        │
│  Charts                      │
│  Alert Explorer              │
└──────────────┬───────────────┘
               │
               ▼
             User
```

---

## 🛠️ Technology Stack

| Layer               | Technology                | Purpose                           |
| ------------------- | ------------------------- | --------------------------------- |
| Data Source         | CSV                       | Raw alert dataset                 |
| Data Processing     | Python                    | Data ingestion and processing     |
| Database            | SQLite                    | Relational data storage           |
| Backend             | FastAPI                   | REST API layer                    |
| API Server          | Uvicorn                   | Runs the FastAPI application      |
| Frontend            | Streamlit                 | Interactive dashboard             |
| Visualization       | Plotly                    | Interactive charts                |
| HTTP Client         | Requests                  | Frontend-to-backend communication |
| Package Management  | uv                        | Dependency management             |
| Version Control     | Git / GitHub              | Source control                    |
| Development         | GitHub Codespaces         | Development environment           |
| Backend Deployment  | Render                    | FastAPI hosting                   |
| Frontend Deployment | Streamlit Community Cloud | Streamlit hosting                 |

---

## 📁 Project Structure

```text
alert-dashboard/
│
├── backend/
│   ├── database.py
│   └── main.py
│
├── data/
│   ├── alerts (2).csv
│   ├── alerts.db
│   └── load_database.py
│
├── streamlit_app.py
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

---

## 📊 Dataset

The application uses a sample vital-alert dataset containing **1,005 alert records**.

Each row represents an individual alert.

### Main fields

* `alert_id`
* `facility_id`
* `ward`
* `vital_name`
* `value`
* `unit`
* `severity`
* `attended_by`
* `creation_time`
* `opened_at`
* `acknowledged_at`

---

## 🎯 Dashboard Capabilities

### Alert Monitoring

* Facility filtering
* Severity filtering
* Ward filtering
* Vital filtering
* Alert-level exploration
* Alert volume analysis

### Response Performance

* Time-to-open metrics
* Time-to-acknowledgement metrics
* Resolution metrics
* SLA breach monitoring

### Operational Analysis

* Facility workload
* Ward workload
* Nurse workload
* Hourly alert volume
* Abandoned alerts

### Data Quality & Anomalies

* Missing acknowledgements
* Invalid timestamps
* Negative timestamps
* Ghost alerts
* Invalid SpO₂ values
* Acknowledgements without an open event

---

## 🔌 REST API

| Endpoint                    | Purpose                                |
| --------------------------- | -------------------------------------- |
| `GET /`                     | Backend health check                   |
| `GET /api/summary`          | Overall alert summary                  |
| `GET /api/alerts`           | Alert records with filters             |
| `GET /api/response-metrics` | Response and SLA metrics               |
| `GET /api/anomalies`        | Data-quality and operational anomalies |
| `GET /api/workload`         | Workload analysis                      |

### Example API Filters

```text
/api/alerts?facility=F003
```

```text
/api/alerts?severity=High
```

```text
/api/alerts?facility=F003&severity=High&ward=ICU
```

For workload analysis:

```text
/api/workload?group_by=facility
```

```text
/api/workload?group_by=nurse
```

```text
/api/workload?group_by=hour
```

---

## 📖 API Documentation

FastAPI automatically provides interactive Swagger documentation.

**Swagger UI:**
[https://alert-dashboard-api.onrender.com/docs](https://alert-dashboard-api.onrender.com/docs)

---

## 💻 Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/avaniskrishna/alert-dashboard.git
cd alert-dashboard
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Start the FastAPI backend

```bash
uv run uvicorn backend.main:app --reload --port 8000
```

Backend:

`http://localhost:8000`

Swagger:

`http://localhost:8000/docs`

### 4. Start the Streamlit frontend

Open another terminal:

```bash
uv run streamlit run streamlit_app.py
```

---

## 🗄️ Database Setup

The SQLite database is included in the repository.

To recreate it from the CSV:

```bash
uv run python data/load_database.py
```

Data flow:

**CSV → `load_database.py` → `alerts.db`**

---

## ☁️ Deployment

The frontend and backend are deployed separately.

### Backend

**Render**

```text
Streamlit Cloud
       │
       │ HTTP Requests
       ▼
Render
FastAPI Backend
       │
       │ SQL
       ▼
SQLite Database
```

### Frontend

**Streamlit Community Cloud**

The Streamlit application communicates with the deployed FastAPI backend through HTTP requests.

This separation keeps the frontend independent from the database and creates a clear API layer between the application and data layer.

---

## 💡 Design Decisions

### Why SQLite?

The dataset is relatively small, so SQLite provides a lightweight relational database without requiring a separate database server.

For a production-scale application, this could be replaced with PostgreSQL or another managed relational database.

### Why FastAPI?

FastAPI provides a lightweight REST API layer between the database and frontend.

It also provides automatic OpenAPI/Swagger documentation.

### Why Streamlit?

Streamlit enables rapid development of an interactive analytical frontend with filters, KPIs, tables, and visualizations.

### Why separate frontend and backend?

The application follows a clear separation of responsibilities:

```text
SQLite
  ↓
Data Storage

FastAPI
  ↓
Data Access + API Logic

Streamlit
  ↓
Presentation + User Interaction
```

This also allows other clients to consume the same APIs in the future.

---

## ⚠️ Error Handling

The frontend handles backend connectivity failures and displays API errors to the user.

API requests use a timeout to prevent the frontend from waiting indefinitely.

> The backend is hosted on Render's free tier. The service may experience a cold start after inactivity, so the first API request can occasionally take longer than subsequent requests.

---

## 🔮 Future Improvements

* PostgreSQL or managed production database
* Authentication and role-based access
* API pagination
* Database indexing
* Automated data ingestion
* API caching
* Automated testing
* CI/CD
* Monitoring and logging
* Docker containerization
* Production-grade infrastructure
* More granular operational metrics

---

## ⚕️ Disclaimer

This project is a prototype created to demonstrate **data engineering, backend API development, frontend development, database integration, and deployment**.

The dashboard is intended for **operational and analytical review only** and is not a clinical decision-support system.

---

## 👩‍💻 Author

**Avani Shaji Krishna**

B.Tech — Computer Science & Engineering
Artificial Intelligence & Data Engineering

GitHub: [https://github.com/avaniskrishna](https://github.com/avaniskrishna)
