from faststream import FastStream
import resend

from src.config import settings
from src.mq import broker

app = FastStream(broker)

resend.api_key = settings.RESEND_API


@broker.subscriber("verification")
async def handle_email(msg: dict):
    if "code" in msg:
        params = {
            "from": "noreply@x0ryz.cc",
            "to": msg["email"],
            "subject": "Your Verification Code",
            "html": f"<p>Code: <strong>{msg['code']}</strong></p>"
        }

    elif "token" in msg:
        reset_link = f"https://x0ryz.cc/reset?token={msg['token']}"

        params = {
            "from": "noreply@x0ryz.cc",
            "to": [msg["email"]],
            "subject": "Reset Your Password",
            "html": f"""
                        <p>Click the link below to reset your password:</p>
                        <a href="{reset_link}">Reset Password</a>
                        <p>Link expires in 15 minutes.</p>
                    """
        }

    try:
        email = resend.Emails.send(params)
        print(f"Email sent to {msg['email']}: {email}")
    except Exception as e:
        print(f"Error sending email: {e}")
