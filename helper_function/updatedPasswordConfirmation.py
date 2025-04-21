import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from core.config import email_settings


async def updatedPasswordConfirmation(data):
    """
    Sends a password change confirmation email using SMTP.
    """
    name = data.get("name", "User")
    recipient_email = data.get("email")

    if not recipient_email:
        raise ValueError("Missing recipient email.")

    try:
        # Email details
        subject = "Reeloid: Your Password Was Successfully Changed"
        from_email = email_settings.EMAIL_HOST_USER  # Sender's email
        to_email = recipient_email  # Recipient's email

        # Plain text version (fallback)
        text_content = f"""
        Hi {name},

        This is a confirmation that your password has been successfully changed.

        If you did not make this change, please contact our support team immediately.

        Regards,
        Reeloid Support Team
        """

        # HTML version
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #4CAF50; text-align: center;">Password Changed Successfully</h2>
                <p style="font-size: 16px; color: #333;">Dear {name},</p>
                
                <p style="font-size: 16px; color: #333;">
                    This is a confirmation that your password was changed successfully.
                </p>

                <p style="font-size: 16px; color: #333;">
                    If you didn’t perform this action, please contact our support team immediately.
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
        with smtplib.SMTP(email_settings.EMAIL_HOST, email_settings.EMAIL_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(email_settings.EMAIL_HOST_USER, email_settings.EMAIL_HOST_PASSWORD)  # Login to the SMTP server
            server.sendmail(from_email, to_email, message.as_string())  # Send the email

        return "Password change confirmation email sent."

    except Exception as err:
        raise ValueError(f"Error sending email: {err}")