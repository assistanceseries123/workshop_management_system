
from pathlib import Path
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import mm
import os

OUT = Path("generated_reports")
OUT.mkdir(exist_ok=True)

styles = getSampleStyleSheet()
TITLE = ParagraphStyle("TitleCustom", parent=styles["Title"], alignment=TA_CENTER, fontSize=17, leading=21, spaceAfter=8)
SUB = ParagraphStyle("Sub", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9, textColor=colors.grey)
SMALL = ParagraphStyle("Small", parent=styles["Normal"], fontSize=8, leading=10)
RIGHT = ParagraphStyle("Right", parent=SMALL, alignment=TA_RIGHT)

def header(story, title):
    story += [
        Paragraph("ASHOK LEYLAND WORKSHOP MANAGEMENT", TITLE),
        Paragraph(title, styles["Heading2"]),
        Paragraph("Author: Aklesh  |  Generated: " + datetime.now().strftime("%d-%m-%Y %H:%M"), SUB),
        Spacer(1, 8),
    ]

def make_pdf(filename, story):
    path = OUT / filename
    doc = SimpleDocTemplate(
        str(path), pagesize=A4, rightMargin=12*mm, leftMargin=12*mm,
        topMargin=12*mm, bottomMargin=12*mm
    )
    doc.build(story)
    return str(path)

def table(data, widths=None):
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#222222")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 7.5),
        ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f2f2f2")]),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    return t

def job_card_pdf(job):
    story = []
    header(story, f"JOB CARD — {job.get('job_card_no','')}")
    info = [
        ["Date", job.get("date",""), "Vehicle", job.get("vehicle_no","")],
        ["Customer", job.get("customer",""), "Model", job.get("model","")],
        ["Odometer", str(job.get("odometer","")), "Job Type", job.get("job_type","")],
        ["Technician", job.get("technician",""), "Priority", job.get("priority","")],
        ["Status", job.get("status",""), "Est. Hours", str(job.get("estimated_hours",""))],
    ]
    t = Table(info, colWidths=[28*mm, 67*mm, 28*mm, 67*mm])
    t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.grey),("FONTNAME",(0,0),(-1,-1),"Helvetica"),
                           ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),
                           ("VALIGN",(0,0),(-1,-1),"TOP"),("FONTSIZE",(0,0),(-1,-1),8)]))
    story += [t, Spacer(1,8)]
    story += [Paragraph("<b>Customer Complaint / Job Description</b>", styles["Heading4"]),
              Paragraph(job.get("complaint",""), SMALL), Spacer(1,6)]
    story += [Paragraph("<b>Parts / Materials Required</b>", styles["Heading4"]),
              Paragraph(job.get("parts_required","") or "—", SMALL), Spacer(1,6)]
    story += [Paragraph("<b>Workshop Remarks</b>", styles["Heading4"]),
              Paragraph(job.get("remarks","") or "—", SMALL), Spacer(1,15)]
    sign = Table([["Customer Signature", "Technician Signature", "Workshop In-charge"],
                  ["", "", ""], ["Date: __________", "Date: __________", "Date: __________"]],
                 colWidths=[63*mm]*3, rowHeights=[8*mm,18*mm,8*mm])
    sign.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.4,colors.grey),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                              ("FONTSIZE",(0,0),(-1,-1),8),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story.append(sign)
    return make_pdf(f"{job.get('job_card_no','job_card')}.pdf", story)

def warranty_report_pdf(claim):
    story = []
    header(story, f"WARRANTY CLAIM REPORT — {claim.get('claim_no','')}")
    info = [
        ["Claim No.", claim.get("claim_no",""), "Claim Date", claim.get("claim_date","")],
        ["Job Card", claim.get("job_card_no",""), "Vehicle", claim.get("vehicle_no","")],
        ["Customer", claim.get("customer",""), "Chassis", claim.get("chassis_no","")],
        ["Component", claim.get("component",""), "Failure Code", claim.get("failure_code","")],
        ["Odometer", str(claim.get("odometer","")), "Claim Amount", f"{claim.get('claim_amount',0):,.2f}"],
        ["Technician", claim.get("technician",""), "Status", claim.get("status","")],
    ]
    t = Table(info, colWidths=[30*mm,65*mm,30*mm,65*mm])
    t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.grey),("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),
                           ("FONTNAME",(2,0),(2,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8),
                           ("VALIGN",(0,0),(-1,-1),"TOP")]))
    story += [t, Spacer(1,8)]
    for title, key in [("Failure / Complaint","complaint"),("Diagnosis / Root Cause","diagnosis"),
                       ("Corrective Action / Parts Replaced","action"),("Warranty Remarks","remarks")]:
        story += [Paragraph(title, styles["Heading4"]), Paragraph(claim.get(key,"") or "—", SMALL), Spacer(1,5)]
    story += [Spacer(1,12), Paragraph("Prepared by: ____________________    Checked by: ____________________", SMALL)]
    return make_pdf(f"{claim.get('claim_no','warranty')}.pdf", story)

def technician_expense_pdf(name, expenses):
    story = []
    header(story, f"TECHNICIAN EXPENSE REPORT — {name}")
    rows = [["Date","Expense No.","Category","Job Card","Description","Amount","Status"]]
    total = 0
    for e in expenses:
        total += float(e.get("amount",0))
        rows.append([e.get("date",""),e.get("expense_no",""),e.get("category",""),e.get("job_card_no",""),
                     e.get("description","")[:35],f"{float(e.get('amount',0)):,.2f}",e.get("status","")])
    rows.append(["","","","","TOTAL",f"{total:,.2f}",""])
    story.append(table(rows, [22*mm,28*mm,27*mm,25*mm,48*mm,25*mm,27*mm]))
    return make_pdf(f"{name}_expenses.pdf".replace(" ","_"), story)

def workshop_summary_pdf(jobs, claims, expenses):
    story = []
    header(story, "WORKSHOP MONTHLY / OVERALL SUMMARY")
    total_exp = sum(float(e.get("amount",0)) for e in expenses)
    completed = sum(j.get("status") == "Completed" for j in jobs)
    open_jobs = sum(j.get("status") in ["Open","In Progress","Waiting for Parts"] for j in jobs)
    approved_claims = sum(c.get("status") in ["Approved","Paid"] for c in claims)
    metrics = [
        ["KPI","Value"],
        ["Total Job Cards",str(len(jobs))],
        ["Completed Job Cards",str(completed)],
        ["Open / WIP Job Cards",str(open_jobs)],
        ["Warranty Claims",str(len(claims))],
        ["Approved / Paid Claims",str(approved_claims)],
        ["Technician Expenses",f"{total_exp:,.2f}"],
    ]
    story.append(table(metrics, [100*mm,70*mm]))
    story.append(Spacer(1,10))
    if jobs:
        rows = [["Job Card","Date","Vehicle","Technician","Type","Status"]]
        for j in jobs[-30:]:
            rows.append([j.get("job_card_no",""),j.get("date",""),j.get("vehicle_no",""),
                         j.get("technician",""),j.get("job_type",""),j.get("status","")])
        story += [Paragraph("Recent Job Cards", styles["Heading3"]), table(rows, [28*mm,23*mm,31*mm,40*mm,35*mm,28*mm])]
    return make_pdf("workshop_summary.pdf", story)

def technician_performance_pdf(name, jobs):
    story = []
    header(story, f"TECHNICIAN PERFORMANCE — {name}")
    total = len(jobs)
    completed = sum(j.get("status") == "Completed" for j in jobs)
    rate = (completed/total*100) if total else 0
    story.append(table([
        ["Metric","Value"],["Technician",name],["Total Allocated Jobs",str(total)],
        ["Completed Jobs",str(completed)],["Completion Rate",f"{rate:.1f}%"]
    ], [80*mm,90*mm]))
    story.append(Spacer(1,10))
    rows = [["Job Card","Date","Vehicle","Type","Priority","Status"]]
    for j in jobs:
        rows.append([j.get("job_card_no",""),j.get("date",""),j.get("vehicle_no",""),
                     j.get("job_type",""),j.get("priority",""),j.get("status","")])
    story.append(table(rows, [30*mm,23*mm,31*mm,35*mm,27*mm,29*mm]))
    return make_pdf(f"{name}_performance.pdf".replace(" ","_"), story)
