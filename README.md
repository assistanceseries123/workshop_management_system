
# Ashok Leyland Workshop Management System

**Author: Aklesh**

A major Streamlit + Python workshop-management project designed for a commercial vehicle service/workshop environment.

## Features

- Workshop dashboard and KPIs
- Job card creation and technician allocation
- Technician workload tracking
- Job status workflow:
  - Open
  - In Progress
  - Waiting for Parts
  - Completed
  - Cancelled
- Warranty claim registration and status tracking
- Warranty failure, diagnosis, corrective-action and claim-amount fields
- Technician expense tracker
- Expense approval workflow
- Technician master
- Customer and vehicle master
- Technician performance / completion rate
- PDF generation:
  - Job Card
  - Warranty Claim Report
  - Technician Expense Report
  - Workshop Summary
  - Technician Performance Report
- JSON local file storage — **no database**
- Data backup/download page

## Why JSON instead of a database?

The application intentionally does not use MySQL, PostgreSQL, SQLite, MongoDB, etc. Records are stored in:

`data/*.json`

This makes the project simple to deploy on a single workshop computer. For multi-user production use, a database should eventually be introduced.

## Project structure

```text
ashok_leyland_workshop_management/
│
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── technicians.json
│   ├── job_cards.json
│   ├── warranty_claims.json
│   ├── expenses.json
│   ├── customers.json
│   └── vehicles.json
│
├── utils/
│   ├── __init__.py
│   ├── storage.py
│   └── pdf_reports.py
│
└── generated_reports/
```

## Installation

### Windows

```bash
cd ashok_leyland_workshop_management
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### Linux / macOS

```bash
cd ashok_leyland_workshop_management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Real-world workflow

1. Add customers and vehicles.
2. Add active technicians.
3. Create a job card from a customer complaint.
4. Allocate the job card to a technician.
5. Technician completes diagnosis/repair.
6. Update job status.
7. If applicable, register a warranty claim.
8. Record technician travel/tool/food/other expenses.
9. Approve or reject expenses.
10. Generate PDF reports for workshop records.
11. Download JSON backups regularly.

## Important

This is an offline/local-file architecture. Avoid running multiple simultaneous writers against the same JSON files. For a multi-user workshop network, add authentication and a proper database in the next version.
