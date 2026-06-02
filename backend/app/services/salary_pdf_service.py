from pathlib import Path

from app.models.employee import Employee
from app.models.salary import SalarySlip

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "salary"


def generate_salary_pdf(slip: SalarySlip, employee: Employee) -> str:
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    filename = f"salary_{employee.id}_{slip.month.strftime('%Y_%m')}.pdf"
    path = UPLOAD_ROOT / filename

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(str(path), pagesize=A4)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 800, "Goldilocks Tech - Salary Slip")
        c.setFont("Helvetica", 11)
        y = 760
        lines = [
            f"Employee: {employee.full_name}",
            f"Code: {employee.employee_code}",
            f"Month: {slip.month.strftime('%B %Y')}",
            f"Basic Salary: {slip.basic_salary}",
            f"HRA: {slip.hra}",
            f"Bonus: {slip.bonus}",
            f"Deductions: {slip.deductions}",
            f"Net Salary: {slip.net_salary}",
            f"Status: {slip.status}",
        ]
        for line in lines:
            c.drawString(50, y, line)
            y -= 22
        c.save()
    except ImportError:
        path.write_text(
            "\n".join(
                [
                    "Goldilocks Tech - Salary Slip",
                    f"Employee: {employee.full_name}",
                    f"Month: {slip.month}",
                    f"Net: {slip.net_salary}",
                ]
            ),
            encoding="utf-8",
        )
        filename = filename.replace(".pdf", ".txt")

    rel = f"uploads/salary/{path.name}"
    return rel
