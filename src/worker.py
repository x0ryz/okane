from faststream import FastStream
import resend

from src.config import settings
from src.mq import broker

app = FastStream(broker)

resend.api_key = settings.RESEND_API


@broker.subscriber("verification")
async def verify_email(msg: dict):
    params = {
        "from": "onboarding@resend.dev",
        "to": msg["email"],
        "subject": "Your Verification Code",
        "html": f"<p>Code: <strong>{msg['code']}</strong></p>"
    }

    try:
        email = resend.Emails.send(params)
        print(f"Email sent to {msg['email']}: {email}")
    except Exception as e:
        print(f"Error sending email: {e}")
