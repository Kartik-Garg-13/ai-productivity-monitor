from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

from app.models.employee import Employee
from app.models.salary import SalarySlip

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "salary"
UPLOADS_BASE = Path(__file__).resolve().parents[2] / "uploads"


def _fmt(amount) -> str:
    return f"₹{float(amount):,.2f}"


def generate_salary_pdf(slip: SalarySlip, employee: Employee) -> str:
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    filename = f"salary_{employee.id}_{slip.month.strftime('%Y_%m')}.pdf"
    path = UPLOAD_ROOT / filename

    try:
        doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm, topMargin=15 * mm, bottomMargin=15 * mm)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("Title", parent=styles["Heading1"], fontSize=14, alignment=1)
        sub_style = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=9, alignment=1, textColor=colors.grey)
        normal = styles["Normal"]
        elements = []

        company = slip.company_snapshot or {}
        emp = slip.employee_snapshot or {}
        cname = company.get("company_name") or "Goldilocks Tech"
        elements.append(Paragraph(cname, title_style))
        if company.get("company_address"):
            elements.append(Paragraph(company["company_address"], sub_style))
        if company.get("gst_number"):
            elements.append(Paragraph(f"GST: {company['gst_number']}", sub_style))
        elements.append(Spacer(1, 8))

        logo_path = company.get("company_logo_path")
        if logo_path:
            full_logo = Path(__file__).resolve().parents[2] / logo_path.replace("\\", "/")
            if full_logo.exists():
                try:
                    elements.insert(0, Image(str(full_logo), width=40 * mm, height=15 * mm))
                except Exception:
                    pass

        elements.append(Paragraph("<b>Salary Slip</b>", styles["Heading2"]))
        meta = [
            ["Payroll Month", slip.month.strftime("%B %Y")],
            ["Payroll Year", str(slip.payroll_year or slip.month.year)],
            ["Generated On", (slip.generated_at or slip.created_at).strftime("%d-%b-%Y") if slip.generated_at or slip.created_at else "—"],
        ]
        elements.append(Table(meta, colWidths=[120, 300]))
        elements.append(Spacer(1, 10))

        emp_rows = [
            ["Employee Name", emp.get("name") or employee.full_name, "Employee ID", emp.get("employee_id") or employee.employee_code],
            ["Designation", emp.get("designation") or employee.designation, "Department", emp.get("department") or employee.department],
            ["Date of Joining", emp.get("joining_date") or str(employee.joining_date), "Work Location", emp.get("work_location") or "—"],
            ["PAN", emp.get("pan_number") or "—", "UAN", emp.get("uan_number") or "—"],
            ["PF Number", emp.get("pf_number") or "—", "Bank", (slip.bank_snapshot or {}).get("bank_name") or "—"],
            ["Account No.", (slip.bank_snapshot or {}).get("account_number") or "—", "IFSC", (slip.bank_snapshot or {}).get("ifsc_code") or "—"],
        ]
        emp_table = Table(emp_rows, colWidths=[90, 150, 90, 150])
        emp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ]))
        elements.append(emp_table)
        elements.append(Spacer(1, 12))

        earn_data = [["Earnings", "Amount (₹)"]]
        for label, amt in slip.earnings_fields():
            if float(amt) > 0:
                earn_data.append([label, f"{float(amt):,.2f}"])
        earn_data.append(["Total Earnings", f"{float(slip.total_earnings or 0):,.2f}"])
        ded_data = [["Deductions", "Amount (₹)"]]
        for label, amt in slip.deduction_fields():
            if float(amt) > 0:
                ded_data.append([label, f"{float(amt):,.2f}"])
        ded_data.append(["Total Deductions", f"{float(slip.total_deductions or slip.deductions or 0):,.2f}"])

        earn_t = Table(earn_data, colWidths=[170, 80])
        ded_t = Table(ded_data, colWidths=[170, 80])
        for t in (earn_t, ded_t):
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eef2ff")),
            ]))
        elements.append(Table([[earn_t, ded_t]], colWidths=[260, 260]))
        elements.append(Spacer(1, 12))

        att = slip.attendance_snapshot or {}
        if att:
            att_rows = [
                ["Working Days", att.get("working_days", "—"), "Present Days", att.get("present_days", "—")],
                ["Casual Leave", att.get("casual_leave_days", 0), "Sick Leave", att.get("sick_leave_days", 0)],
                ["Paid Leave", att.get("paid_leave_days", 0), "Unpaid Leave", att.get("unpaid_leave_days", 0)],
                ["Overtime Hours", att.get("overtime_hours", 0), "Late Days", att.get("late_days", 0)],
            ]
            att_t = Table(att_rows, colWidths=[90, 60, 90, 60])
            att_t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey), ("FONTSIZE", (0, 0), (-1, -1), 8)]))
            elements.append(Paragraph("<b>Attendance & Leave Summary</b>", normal))
            elements.append(att_t)
            elements.append(Spacer(1, 10))

        summary = [
            ["Gross Salary", _fmt(slip.gross_salary or slip.total_earnings or 0)],
            ["Total Deductions", _fmt(slip.total_deductions or slip.deductions or 0)],
            ["Net Salary", _fmt(slip.net_salary)],
            ["In-Hand Salary", _fmt(slip.in_hand_salary or slip.net_salary)],
        ]
        sum_t = Table(summary, colWidths=[200, 120])
        sum_t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("FONTNAME", (0, -2), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, -2), (-1, -1), colors.HexColor("#ecfdf5")),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        elements.append(sum_t)
        if slip.amount_in_words:
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"<b>Amount in Words:</b> {slip.amount_in_words}", normal))
        elements.append(Spacer(1, 30))
        sig = Table([["Authorized Signatory", "HR Signatory"]], colWidths=[250, 250])
        sig.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 1, colors.black), ("FONTSIZE", (0, 0), (-1, -1), 8), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        elements.append(sig)

        doc.build(elements)
    except ImportError:
        path.write_text(
            "\n".join([
                company.get("company_name", "Goldilocks Tech") + " - Salary Slip",
                f"Employee: {employee.full_name}",
                f"Month: {slip.month}",
                f"Net: {slip.net_salary}",
            ]),
            encoding="utf-8",
        )
        filename = filename.replace(".pdf", ".txt")

    return f"uploads/salary/{path.name}"
