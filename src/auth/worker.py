from faststream import FastStream
from faststream.rabbit import RabbitBroker
import resend

from src.config import settings

broker = RabbitBroker("amqp://guest:guest@localhost:5672/")
app = FastStream(broker)
resend.api_key = settings.RESEND_API

@broker.subscriber("verification")
async def verify_email(msg: dict):
    resend.Emails.SendParams = {
        "from": "onboarding@resend.dev",
        "to": msg["email"],
        "subject": "Your Verification Code",
        "html": f"<p>Code: <strong>{msg['code']}</strong></p>"
    }
