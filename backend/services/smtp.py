# Send the OTP email to user's registered email
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List, Dict
from backend.config.settings import settings
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# Find the definite path to the template
# Why capitalize? Indicates "BASE_DIR" is constant and shall not be changed
BASE_DIR = Path(__file__).parent.parent.parent

# Config the connection, all information from the .env/settings
conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=settings.mail_starttls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=settings.use_credentials,
    VALIDATE_CERTS=settings.validate_certs,
    TEMPLATE_FOLDER=str(BASE_DIR / 'backend' / 'templates' / 'emails')
)

# Initiate a jinja2 template environment
env = Environment(loader=FileSystemLoader(conf.TEMPLATE_FOLDER))


# Config the basic info, including templates/emails/opt.html
async def send_otp_email(
    subject: str,           # email title
    recipients: List[str],  # send-to email, have to be plural
    template_name: str,     # html template name
    context: Dict = {},     # variables shared for template use
):
    try:
        # Craete the template
        template = env.get_template(template_name)
        html_context = template.render(**context)  # ** Unpack dict: k-v pair

        # Prepare the actual email message for sending
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=html_context,
            subtype="html",
        )

        # Initialize the FastMAil
        fastmail = FastMail(conf)

        # Send the email
        await fastmail.send_message(message)

        return True, "Email sent successfully."
    except Exception as e:
        print(f"Error message: {e}")
        return False, str(e)
