import aiosmtplib
from email.mime.text import MIMEText
from core.config import email_settings
from email.mime.multipart import MIMEMultipart

async def verifycodeEmailSender(data):
    name = data.get("name", "User")
    otp = data.get("otp")  # Ensure OTP is passed in the data
    to_email = data.get("email")
    
    if not otp:
        raise ValueError("Error: Missing OTP")
    if not to_email:
        raise ValueError("Error: No email found")
    
    try:
        subject = "Reeloid: Email Verification Code"
        from_email = email_settings.EMAIL_HOST_USER  # Sender email

        # Plain text version (fallback)
        text_content = f"""
        Hi {name},

        We received a request to verify your account. Please use the verification code below (valid for 15 minutes only):

        {otp}

        If you did not request this, please ignore this email.

        Regards,
        Reeloid Support Team
        """

        # HTML Content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #D4AF37; text-align: center;">Email Verification</h2>
                <p style="font-size: 16px; color: #333;">Dear {name},</p>
                
                <p style="font-size: 16px; color: #333;">
                    We received a request to verify your account. Please use the verification code below (valid for 15 minutes only):
                </p>

                <div style="text-align: center; margin: 20px 0;">
                    <a  
                    style="background: #D4AF37; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold;">
                    {otp}
                    </a>
                </div>

                <p style="font-size: 16px; color: #333;">
                    If you did not request this, you can safely ignore this email.
                </p>

                <p style="font-size: 16px; color: #333; text-align: center;">
                    <b>- Reeloid Support Team</b>
                </p>
            </div>
        </body>
        </html>
        """

        # Create the email message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = from_email
        message["To"] = to_email

        # Attach plain text and HTML content
        message.attach(MIMEText(text_content, "plain"))
        message.attach(MIMEText(html_content, "html"))

        # Connect to the SMTP server
        await aiosmtplib.send(
            message,
            hostname=email_settings.EMAIL_HOST,
            port=email_settings.EMAIL_PORT,
            start_tls=True,
            username=email_settings.EMAIL_HOST_USER,
            password=email_settings.EMAIL_HOST_PASSWORD,
        )

        return "Email sent successfully"

    except Exception as err:
        raise ValueError(f"Error sending email: {str(err)}")