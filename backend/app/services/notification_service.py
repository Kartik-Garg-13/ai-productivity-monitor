from app.services.email_service import send_email


class NotificationService:
    @staticmethod
    def employee_created(recipient: str, name: str) -> None:
        send_email(
            subject="Welcome to Goldilocks Tech",
            recipient=recipient,
            body=f"Hi {name}, your employee account has been created. You can now log in to the HRMS portal.",
        )

    @staticmethod
    def leave_approved(recipient: str, start_date: str, end_date: str) -> None:
        send_email(
            subject="Leave Request Approved",
            recipient=recipient,
            body=f"Your leave request from {start_date} to {end_date} has been approved.",
        )

    @staticmethod
    def leave_rejected(recipient: str, remarks: str | None = None) -> None:
        send_email(
            subject="Leave Request Rejected",
            recipient=recipient,
            body=f"Your leave request was rejected.{f' Remarks: {remarks}' if remarks else ''}",
        )

    @staticmethod
    def expense_approved(recipient: str, amount: str) -> None:
        send_email(
            subject="Expense Approved",
            recipient=recipient,
            body=f"Your expense claim of ₹{amount} has been approved.",
        )

    @staticmethod
    def expense_rejected(recipient: str, remarks: str | None = None) -> None:
        send_email(
            subject="Expense Rejected",
            recipient=recipient,
            body=f"Your expense claim was rejected.{f' Remarks: {remarks}' if remarks else ''}",
        )

    @staticmethod
    def salary_paid(recipient: str, month: str, net_salary: str) -> None:
        send_email(
            subject=f"Salary Paid - {month}",
            recipient=recipient,
            body=f"Your salary for {month} has been processed. Net salary: ₹{net_salary}.",
        )

    @staticmethod
    def new_announcement(recipient: str, title: str) -> None:
        send_email(
            subject=f"New Announcement: {title}",
            recipient=recipient,
            body=f"A new announcement has been published: {title}. Please check the HRMS portal.",
        )

    @staticmethod
    def project_assigned(recipient: str, project_name: str) -> None:
        send_email(
            subject=f"Project Assignment: {project_name}",
            recipient=recipient,
            body=f"You have been assigned to project '{project_name}'.",
        )

    @staticmethod
    def task_assigned(recipient: str, task_title: str, project_name: str) -> None:
        send_email(
            subject=f"New Task: {task_title}",
            recipient=recipient,
            body=f"You have been assigned task '{task_title}' on project '{project_name}'.",
        )

    @staticmethod
    def salary_slip_generated(recipient: str, month: str) -> None:
        send_email(
            subject=f"Salary Slip - {month}",
            recipient=recipient,
            body=f"Your salary slip for {month} is ready for download in the HRMS portal.",
        )
