
import streamlit as st
from pathlib import Path
from datetime import date, datetime
import pandas as pd
import json

from utils.storage import load_json, save_json, append_record, update_record, delete_record, next_id
from utils.pdf_reports import (
    warranty_report_pdf, technician_expense_pdf, job_card_pdf,
    workshop_summary_pdf, technician_performance_pdf
)

BASE = Path("data")
BASE.mkdir(exist_ok=True)

st.set_page_config(
    page_title="Workshop Management System",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Default master data ----------
DEFAULT_TECHNICIANS = [
    {"id": 1, "name": "Suraj Kumar Patel", "phone": "", "specialization": "Engine & Mechanical", "status": "Active"},
    {"id": 2, "name": "Dinesh Yadav", "phone": "", "specialization": "Engine & Mechanical", "status": "Active"},
    {"id": 3, "name": "Raj Narayan Kohar", "phone": "", "specialization": "Electrical", "status": "Active"},
    {"id": 4, "name": "Mukesh Kohar", "phone": "", "specialization": "AC & Electrical & Mechanical", "status": "Active"},
    {"id": 5, "name": "Durgesh yadav", "phone": "", "specialization": "Mechanical", "status": "Active"},
    {"id": 6, "name": "Surendra Rana", "phone": "", "specialization": "Mechanical", "status": "Active"},
    {"id": 6, "name": "Surya Bharati", "phone": "", "specialization": "Mechanical", "status": "Active"},
]

DEFAULT_JOB_CATEGORIES = [
    "Preventive Maintenance", "Breakdown", "Warranty", "PDI",
    "Electrical Diagnosis", "Engine", "Transmission", "AC",
    "Tyre & Suspension", "General Repair"
]

for name, default in [
    ("technicians.json", DEFAULT_TECHNICIANS),
    ("job_cards.json", []),
    ("warranty_claims.json", []),
    ("expenses.json", []),
    ("customers.json", []),
    ("vehicles.json", []),
]:
    if not (BASE / name).exists():
        save_json(BASE / name, default)

def records(name):
    return load_json(BASE / name)

# ---------- Sidebar ----------
st.sidebar.title("🔧 AL Workshop")
st.sidebar.caption("Workshop Management System")
st.sidebar.markdown("**Author:** Aklesh")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard", "Job Card Allocation", "Warranty Management",
        "Technician Expenses", "Technicians", "Customers & Vehicles",
        "Reports & PDF", "Data Backup"
    ]
)

st.sidebar.divider()
st.sidebar.info("No database required.\nData is stored locally in JSON files inside the `data/` folder.")

# ---------- Dashboard ----------
if page == "Dashboard":
    st.title("🏭 Ashok Leyland Workshop Management")
    st.caption("Real-world service workshop control panel • Author: Aklesh")

    jobs = records("job_cards.json")
    techs = records("technicians.json")
    warranties = records("warranty_claims.json")
    expenses = records("expenses.json")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Job Cards", len(jobs))
    c2.metric("Open Jobs", sum(j.get("status") in ["Open", "In Progress"] for j in jobs))
    c3.metric("Warranty Claims", len(warranties))
    c4.metric("Technicians", sum(t.get("status") == "Active" for t in techs))

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Job Card Status")
        if jobs:
            df = pd.DataFrame(jobs)
            st.bar_chart(df["status"].value_counts())
        else:
            st.info("No job cards yet.")

    with col2:
        st.subheader("Technician Workload")
        if jobs:
            workload = pd.DataFrame(jobs)["technician"].fillna("Unassigned").value_counts()
            st.bar_chart(workload)
        else:
            st.info("No technician allocation yet.")

    st.subheader("Recent Job Cards")
    if jobs:
        df = pd.DataFrame(jobs)
        cols = [c for c in ["job_card_no", "date", "vehicle_no", "customer", "technician", "job_type", "status"] if c in df]
        st.dataframe(df[cols].sort_values("date", ascending=False).head(10), use_container_width=True)
    else:
        st.info("Create your first job card from Job Card Allocation.")

# ---------- Job Cards ----------
elif page == "Job Card Allocation":
    st.title("🧾 Job Card Allocation")
    techs = [t for t in records("technicians.json") if t.get("status") == "Active"]

    tab1, tab2 = st.tabs(["Create / Allocate Job Card", "Job Card Register"])

    with tab1:
        with st.form("job_form", clear_on_submit=True):
            a, b, c = st.columns(3)
            jc_date = a.date_input("Job Card Date", date.today())
            vehicle_no = b.text_input("Vehicle Registration No. *")
            customer = c.text_input("Customer / Fleet Name *")

            d, e, f = st.columns(3)
            model = d.text_input("Vehicle Model")
            odometer = e.number_input("Odometer (km)", min_value=0, step=1)
            job_type = f.selectbox("Job Type", DEFAULT_JOB_CATEGORIES)

            g, h, i = st.columns(3)
            technician_names = [t["name"] for t in techs]
            technician = g.selectbox("Allocate Technician", ["Unassigned"] + technician_names)
            priority = h.selectbox("Priority", ["Normal", "High", "Critical"])
            estimated_hours = i.number_input("Estimated Labour Hours", min_value=0.0, step=0.5)

            complaint = st.text_area("Customer Complaint / Job Description *")
            parts_required = st.text_area("Parts / Materials Required")
            remarks = st.text_area("Workshop Remarks")

            submitted = st.form_submit_button("Create Job Card", type="primary")
            if submitted:
                if not vehicle_no or not customer or not complaint:
                    st.error("Vehicle number, customer and complaint are required.")
                else:
                    jobs = records("job_cards.json")
                    jc = {
                        "id": next_id(jobs),
                        "job_card_no": f"JC-{datetime.now().strftime('%Y%m')}-{next_id(jobs):04d}",
                        "date": str(jc_date),
                        "vehicle_no": vehicle_no.upper(),
                        "customer": customer,
                        "model": model,
                        "odometer": odometer,
                        "job_type": job_type,
                        "technician": technician,
                        "priority": priority,
                        "estimated_hours": estimated_hours,
                        "complaint": complaint,
                        "parts_required": parts_required,
                        "remarks": remarks,
                        "status": "Open",
                        "created_at": datetime.now().isoformat(timespec="seconds"),
                        "closed_at": ""
                    }
                    append_record(BASE / "job_cards.json", jc)
                    st.success(f"Job card {jc['job_card_no']} created and allocated to {technician}.")

    with tab2:
        jobs = records("job_cards.json")
        if jobs:
            df = pd.DataFrame(jobs)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.subheader("Update Job Status")
            jc_options = [j["job_card_no"] for j in jobs]
            selected = st.selectbox("Select Job Card", jc_options)
            selected_job = next(j for j in jobs if j["job_card_no"] == selected)
            new_status = st.selectbox(
                "Status",
                ["Open", "In Progress", "Waiting for Parts", "Completed", "Cancelled"],
                index=["Open", "In Progress", "Waiting for Parts", "Completed", "Cancelled"].index(selected_job["status"])
            )
            if st.button("Update Status"):
                selected_job["status"] = new_status
                selected_job["closed_at"] = datetime.now().isoformat(timespec="seconds") if new_status == "Completed" else ""
                update_record(BASE / "job_cards.json", selected_job["id"], selected_job)
                st.success("Job card status updated.")
                st.rerun()
        else:
            st.info("No job cards found.")

# ---------- Warranty ----------
elif page == "Warranty Management":
    st.title("🛡️ Warranty Management")
    jobs = records("job_cards.json")

    tab1, tab2 = st.tabs(["Register Warranty Claim", "Warranty Register"])

    with tab1:
        with st.form("warranty_form", clear_on_submit=True):
            a, b, c = st.columns(3)
            claim_date = a.date_input("Claim Date", date.today())
            job_card_no = b.text_input("Job Card No.")
            vehicle_no = c.text_input("Vehicle Registration No. *")

            d, e, f = st.columns(3)
            customer = d.text_input("Customer / Fleet")
            chassis_no = e.text_input("Chassis No.")
            component = f.text_input("Failed Component *")

            g, h, i = st.columns(3)
            failure_code = g.text_input("Failure Code")
            km = h.number_input("Failure Odometer (km)", min_value=0, step=1)
            claim_amount = i.number_input("Estimated Claim Amount", min_value=0.0, step=100.0)

            technician = st.text_input("Technician")
            complaint = st.text_area("Failure / Complaint *")
            diagnosis = st.text_area("Diagnosis / Root Cause")
            action = st.text_area("Corrective Action / Parts Replaced")
            remarks = st.text_area("Warranty Remarks")

            if st.form_submit_button("Register Warranty Claim", type="primary"):
                if not vehicle_no or not component or not complaint:
                    st.error("Vehicle, failed component and complaint are required.")
                else:
                    claims = records("warranty_claims.json")
                    claim = {
                        "id": next_id(claims),
                        "claim_no": f"W-{datetime.now().strftime('%Y%m')}-{next_id(claims):04d}",
                        "claim_date": str(claim_date),
                        "job_card_no": job_card_no,
                        "vehicle_no": vehicle_no.upper(),
                        "customer": customer,
                        "chassis_no": chassis_no,
                        "component": component,
                        "failure_code": failure_code,
                        "odometer": km,
                        "claim_amount": claim_amount,
                        "technician": technician,
                        "complaint": complaint,
                        "diagnosis": diagnosis,
                        "action": action,
                        "remarks": remarks,
                        "status": "Submitted"
                    }
                    append_record(BASE / "warranty_claims.json", claim)
                    st.success(f"Warranty claim {claim['claim_no']} registered.")

    with tab2:
        claims = records("warranty_claims.json")
        if claims:
            df = pd.DataFrame(claims)
            st.dataframe(df, use_container_width=True, hide_index=True)

            selected = st.selectbox("Select Claim", [c["claim_no"] for c in claims])
            claim = next(c for c in claims if c["claim_no"] == selected)
            status = st.selectbox(
                "Claim Status",
                ["Submitted", "Under Review", "Approved", "Rejected", "Paid"],
                index=["Submitted", "Under Review", "Approved", "Rejected", "Paid"].index(claim["status"])
            )
            if st.button("Update Claim Status"):
                claim["status"] = status
                update_record(BASE / "warranty_claims.json", claim["id"], claim)
                st.success("Warranty status updated.")
                st.rerun()
        else:
            st.info("No warranty claims found.")

# ---------- Expenses ----------
elif page == "Technician Expenses":
    st.title("💰 Technician Expense Tracker")

    techs = [t["name"] for t in records("technicians.json") if t.get("status") == "Active"]

    tab1, tab2 = st.tabs(["Add Expense", "Expense Register"])

    with tab1:
        with st.form("expense_form", clear_on_submit=True):
            a, b, c = st.columns(3)
            exp_date = a.date_input("Expense Date", date.today())
            technician = b.selectbox("Technician", techs if techs else ["No technician"])
            category = c.selectbox("Category", ["Travel", "Food", "Local Transport", "Accommodation", "Tools", "Other"])

            d, e = st.columns(2)
            amount = d.number_input("Amount", min_value=0.0, step=50.0)
            job_card_no = e.text_input("Related Job Card No.")

            description = st.text_area("Expense Description")
            receipt_no = st.text_input("Receipt / Voucher No.")

            if st.form_submit_button("Save Expense", type="primary"):
                if amount <= 0:
                    st.error("Enter an amount greater than zero.")
                else:
                    expenses = records("expenses.json")
                    exp = {
                        "id": next_id(expenses),
                        "expense_no": f"EXP-{datetime.now().strftime('%Y%m')}-{next_id(expenses):04d}",
                        "date": str(exp_date),
                        "technician": technician,
                        "category": category,
                        "amount": amount,
                        "job_card_no": job_card_no,
                        "description": description,
                        "receipt_no": receipt_no,
                        "status": "Pending Approval"
                    }
                    append_record(BASE / "expenses.json", exp)
                    st.success("Expense saved.")

    with tab2:
        expenses = records("expenses.json")
        if expenses:
            df = pd.DataFrame(expenses)
            st.metric("Total Expense", f"{df['amount'].sum():,.2f}")
            st.dataframe(df, use_container_width=True, hide_index=True)

            selected = st.selectbox("Expense", [e["expense_no"] for e in expenses])
            exp = next(e for e in expenses if e["expense_no"] == selected)
            status = st.selectbox("Approval Status", ["Pending Approval", "Approved", "Rejected"])
            if st.button("Update Expense Status"):
                exp["status"] = status
                update_record(BASE / "expenses.json", exp["id"], exp)
                st.success("Expense status updated.")
                st.rerun()
        else:
            st.info("No expenses found.")

# ---------- Technicians ----------
elif page == "Technicians":
    st.title("👨‍🔧 Technician Master & Workload")

    tab1, tab2 = st.tabs(["Technician Master", "Performance"])

    with tab1:
        with st.form("tech_form", clear_on_submit=True):
            a, b, c = st.columns(3)
            name = a.text_input("Technician Name *")
            phone = b.text_input("Phone")
            specialization = c.text_input("Specialization")
            if st.form_submit_button("Add Technician"):
                if not name:
                    st.error("Technician name is required.")
                else:
                    techs = records("technicians.json")
                    append_record(BASE / "technicians.json", {
                        "id": next_id(techs), "name": name, "phone": phone,
                        "specialization": specialization, "status": "Active"
                    })
                    st.success("Technician added.")
                    st.rerun()

        techs = records("technicians.json")
        st.dataframe(pd.DataFrame(techs), use_container_width=True, hide_index=True)

        if techs:
            selected = st.selectbox("Technician to deactivate/activate", [t["name"] for t in techs])
            tech = next(t for t in techs if t["name"] == selected)
            new_status = "Inactive" if tech["status"] == "Active" else "Active"
            if st.button(f"Set {new_status}"):
                tech["status"] = new_status
                update_record(BASE / "technicians.json", tech["id"], tech)
                st.rerun()

    with tab2:
        jobs = records("job_cards.json")
        if jobs:
            df = pd.DataFrame(jobs)
            perf = df.groupby("technician").agg(
                total_jobs=("job_card_no", "count"),
                completed=("status", lambda x: (x == "Completed").sum()),
                open_jobs=("status", lambda x: x.isin(["Open", "In Progress", "Waiting for Parts"]).sum())
            ).reset_index()
            perf["completion_rate_%"] = (perf["completed"] / perf["total_jobs"] * 100).round(1)
            st.dataframe(perf, use_container_width=True, hide_index=True)
        else:
            st.info("No job data available.")

# ---------- Customers ----------
elif page == "Customers & Vehicles":
    st.title("🚛 Customers & Vehicles")
    tab1, tab2 = st.tabs(["Customers", "Vehicles"])

    with tab1:
        with st.form("customer_form", clear_on_submit=True):
            name = st.text_input("Customer / Fleet Name *")
            contact = st.text_input("Contact")
            address = st.text_area("Address")
            if st.form_submit_button("Add Customer"):
                if name:
                    data = records("customers.json")
                    append_record(BASE / "customers.json", {
                        "id": next_id(data), "name": name, "contact": contact, "address": address
                    })
                    st.success("Customer saved.")
                    st.rerun()
                else:
                    st.error("Customer name required.")
        data = records("customers.json")
        st.dataframe(pd.DataFrame(data) if data else pd.DataFrame(), use_container_width=True, hide_index=True)

    with tab2:
        with st.form("vehicle_form", clear_on_submit=True):
            a, b, c = st.columns(3)
            reg = a.text_input("Registration No. *")
            model = b.text_input("Model")
            chassis = c.text_input("Chassis No.")
            d, e = st.columns(2)
            customer = d.text_input("Customer / Fleet")
            year = e.number_input("Model Year", min_value=1980, max_value=2100, value=date.today().year)
            if st.form_submit_button("Add Vehicle"):
                if reg:
                    data = records("vehicles.json")
                    append_record(BASE / "vehicles.json", {
                        "id": next_id(data), "registration_no": reg.upper(), "model": model,
                        "chassis_no": chassis, "customer": customer, "model_year": year
                    })
                    st.success("Vehicle saved.")
                    st.rerun()
                else:
                    st.error("Registration number required.")
        data = records("vehicles.json")
        st.dataframe(pd.DataFrame(data) if data else pd.DataFrame(), use_container_width=True, hide_index=True)

# ---------- Reports ----------
elif page == "Reports & PDF":
    st.title("📄 Reports & PDF Generation")
    st.caption("Generate printable workshop documents without a database.")

    report = st.selectbox("Report Type", [
        "Workshop Summary", "Warranty Claim Report",
        "Technician Expense Report", "Job Card Report",
        "Technician Performance Report"
    ])

    jobs = records("job_cards.json")
    claims = records("warranty_claims.json")
    expenses = records("expenses.json")

    if report == "Workshop Summary":
        st.write("Creates an overall workshop KPI report.")
        if st.button("Generate Workshop Summary PDF", type="primary"):
            path = workshop_summary_pdf(jobs, claims, expenses)
            with open(path, "rb") as f:
                st.download_button("⬇️ Download PDF", f, file_name="workshop_summary.pdf", mime="application/pdf")

    elif report == "Warranty Claim Report":
        if claims:
            selected = st.selectbox("Claim", [c["claim_no"] for c in claims])
            claim = next(c for c in claims if c["claim_no"] == selected)
            if st.button("Generate Warranty PDF", type="primary"):
                path = warranty_report_pdf(claim)
                with open(path, "rb") as f:
                    st.download_button("⬇️ Download Warranty Report", f, file_name=f"{claim['claim_no']}.pdf", mime="application/pdf")
        else:
            st.info("No claims available.")

    elif report == "Technician Expense Report":
        if expenses:
            names = sorted(set(e["technician"] for e in expenses))
            selected = st.selectbox("Technician", names)
            filtered = [e for e in expenses if e["technician"] == selected]
            if st.button("Generate Expense PDF", type="primary"):
                path = technician_expense_pdf(selected, filtered)
                with open(path, "rb") as f:
                    st.download_button("⬇️ Download Expense Report", f, file_name=f"{selected}_expenses.pdf", mime="application/pdf")
        else:
            st.info("No expenses available.")

    elif report == "Job Card Report":
        if jobs:
            selected = st.selectbox("Job Card", [j["job_card_no"] for j in jobs])
            job = next(j for j in jobs if j["job_card_no"] == selected)
            if st.button("Generate Job Card PDF", type="primary"):
                path = job_card_pdf(job)
                with open(path, "rb") as f:
                    st.download_button("⬇️ Download Job Card", f, file_name=f"{selected}.pdf", mime="application/pdf")
        else:
            st.info("No job cards available.")

    else:
        if jobs:
            names = sorted(set(j["technician"] for j in jobs))
            selected = st.selectbox("Technician", names)
            filtered = [j for j in jobs if j["technician"] == selected]
            if st.button("Generate Performance PDF", type="primary"):
                path = technician_performance_pdf(selected, filtered)
                with open(path, "rb") as f:
                    st.download_button("⬇️ Download Performance Report", f, file_name=f"{selected}_performance.pdf", mime="application/pdf")
        else:
            st.info("No jobs available.")

# ---------- Backup ----------
elif page == "Data Backup":
    st.title("💾 Data Backup & Export")

    data_files = ["job_cards.json", "warranty_claims.json", "expenses.json", "technicians.json", "customers.json", "vehicles.json"]
    for fn in data_files:
        data = records(fn)
        st.write(f"**{fn}** — {len(data)} records")
        st.download_button(
            f"Download {fn}",
            data=json.dumps(data, indent=2, ensure_ascii=False),
            file_name=fn,
            mime="application/json",
            key=fn
        )

    st.divider()
    st.success("Recommended practice: copy the entire `data/` folder daily to a backup drive/cloud folder.")
