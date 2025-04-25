import aiosmtplib
from core.config import email_settings
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Define templates for different email types
templates = {
    "registration": {
        "subject": "Reeloid : Account Registration Successful",
        "text": "Welcome to Reeloid! Your account registration was successful.",
        "html": lambda name: f"""
        <html>
        <body style=\"font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;\">
            <div style=\"max-width: 600px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);\">
                <h2 style=\"color: #D4AF37; text-align: center;\">Welcome to <span style=\"font-weight: bold;\">Reeloid</span>: Naye Zamane Ka Vertical Content Provider!</h2>
                <p style=\"font-size: 16px; color: #333;\">Dear {name},</p>
                <p style=\"font-size: 16px; color: #333;\">
                    We are excited to inform you that you have been successfully 
                    <b style=\"color: #D4AF37;\">registered</b> with us.
                </p>
                <p style=\"font-size: 16px; color: #333;\">
                    Now you can use your credentials to <b style=\"color: #D4AF37;\">log in</b> and enjoy 
                    high-quality <b style=\"color: #D4AF37;\">entertainment videos</b> anytime, anywhere.
                </p>
                <div style=\"text-align: center; margin: 20px 0;\">
                    <a href=\"https://demo.reeloid.app/\" 
                    style=\"background: #D4AF37; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold;\">
                    Login Now
                    </a>
                </div>
                <p style=\"font-size: 16px; color: #333; text-align: center;\">
                    <b>- Rohit Gupta (C.E.O)</b><br>
                    <i style=\"color: #D4AF37;\">Reeloid: Vertical Movies and Series on the Go</i>
                </p>
            </div>
        </body>
        </html>
        """
    },
    "verification": {
        "subject": "Reeloid: Email Verification Code",
        "text": lambda name, otp: f"Hi {name},\n\nWe received a request to verify your account. Your verification code (valid for 15 minutes):\n\n{otp}\n\nIf you did not request this, please ignore this email.\n\nRegards,\nReeloid Support Team",
        "html": lambda name, otp: f"""
        <html>
        <body style=\"font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;\">
            <div style=\"max-width: 600px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);\">
                <h2 style=\"color: #D4AF37; text-align: center;\">Email Verification</h2>
                <p style=\"font-size: 16px; color: #333;\">Dear {name},</p>
                <p style=\"font-size: 16px; color: #333;\">
                    We received a request to verify your account. Your verification code (valid for 15 minutes):
                </p>
                <div style=\"text-align: center; margin: 20px 0;\">
                    <span style=\"background: #D4AF37; color: white; padding: 12px 24px; border-radius: 5px; font-size: 16px; font-weight: bold; display: inline-block;\">{otp}</span>
                </div>
                <p style=\"font-size: 16px; color: #333;\">
                    If you did not request this, please ignore this email.
                </p>
                <p style=\"font-size: 16px; color: #333; text-align: center;\">
                    <b>- Reeloid Support Team</b>
                </p>
            </div>
        </body>
        </html>
        """
    },
    "forgot_password": {
        "subject": "Reeloid: Password Reset Request",
        "text": lambda name, otp: f"Hi {name},\n\nWe received a request to reset your password. Use the OTP below to reset your password (valid for 15 minutes):\n\n{otp}\n\nIf you did not request this, please ignore this email.\n\nRegards,\nReeloid Support Team",
        "html": lambda name, otp: f"""
        <html>
        <body style=\"font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;\">
            <div style=\"max-width: 600px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);\">
                <h2 style=\"color: #D4AF37; text-align: center;\">Reset Your Password</h2>
                <p style=\"font-size: 16px; color: #333;\">Dear {name},</p>
                <p style=\"font-size: 16px; color: #333;\">
                    We received a request to reset your password. Use the OTP below to reset your password (valid for 15 minutes):
                </p>
                <div style=\"text-align: center; margin: 20px 0;\">
                    <span style=\"background: #D4AF37; color: white; padding: 12px 24px; border-radius: 5px; font-size: 16px; font-weight: bold; display: inline-block;\">{otp}</span>
                </div>
                <p style=\"font-size: 16px; color: #333;\">
                    If you did not request this, please ignore this email.
                </p>
                <p style=\"font-size: 16px; color: #333; text-align: center;\">
                    <b>- Reeloid Support Team</b>
                </p>
            </div>
        </body>
        </html>
        """
    }
}

async def sendEmail(data: dict, template_type: str) -> str:
    try:
        if template_type not in templates:
            raise ValueError(f"Invalid template_type: {template_type}")

        tpl = templates[template_type]
        name = data.get("name", "User")
        recipient_email = data.get("email")
        if not name:
            raise ValueError("Error: Missing name in data")
        if not recipient_email:
            raise ValueError("Error: No email provided in data")

        plain= ""
        html= ""
        # For OTP templates, ensure otp is present
        if template_type in ["verification", "forgot_password"]:
            otp = data.get("otp")
            if not otp:
                raise ValueError("Error: Missing otp in data")
            plain = tpl["text"](name, otp)
            html = tpl["html"](name, otp)
        else:
            plain = tpl["text"]
            html = tpl["html"](name)
            

        # Prepare subject and contents
        subject = tpl["subject"]

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = email_settings.EMAIL_HOST_USER
        message["To"] = recipient_email
        message.attach(MIMEText(plain, "plain"))
        message.attach(MIMEText(html, "html"))

        # Send via SMTP
        await aiosmtplib.send(
            message,
            hostname=email_settings.EMAIL_HOST,
            port=email_settings.EMAIL_PORT,
            start_tls=True,
            username=email_settings.EMAIL_HOST_USER,
            password=email_settings.EMAIL_HOST_PASSWORD,
        )
        return "Email sent successfully"

    except Exception as e:
        return f"Error sending email: {str(e)}"
