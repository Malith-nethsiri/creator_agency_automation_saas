from fastapi import APIRouter
from services.email_service import email_service

router = APIRouter()

@router.get("/send-test-email")
def send_test_email():
    test_email = "your_email@gmail.com"  # Change to your email
    subject = "✅ Test Email from Creator Agency SaaS"
    body = "This is a test email. Your SMTP works perfectly!"

    email_service.send_email(test_email, subject, body)
    return {"status": "success", "message": f"Email sent to {test_email}"}
