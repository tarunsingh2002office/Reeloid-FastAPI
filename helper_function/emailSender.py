import aiosmtplib
from email.mime.text import MIMEText
from core.config import email_settings
from email.mime.multipart import MIMEMultipart

async def emailSender(data):
    name = data.get("name", "user")
    recipient_email = data.get("email")
    if not name:
        raise ValueError("Error: Missing name")
    if not recipient_email:
        raise ValueError("Error: no email found")
    try:
        subject = "Reeloid : Account Registration Successful"
        from_email = email_settings.EMAIL_HOST_USER  # Replace with your Gmail

        # Plain text version (fallback)
        text_content = "Welcome to Reeloid! Your account registration was successful."
        # HTML content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);">
                <h2 style="color: #D4AF37; text-align: center;">Welcome to <span style="font-weight: bold;">Reeloid</span>: Naye Zamane Ka Vertical Content Provider!</h2>
                <p style="font-size: 16px; color: #333;">Dear {name},</p>
                
                <p style="font-size: 16px; color: #333;">
                    We are excited to inform you that you have been successfully 
                    <b style="color: #D4AF37;">registered</b> with us.
                </p>
                
                <p style="font-size: 16px; color: #333;">
                    Now you can use your credentials to <b style="color: #D4AF37;">log in</b> and enjoy 
                    high-quality <b style="color: #D4AF37;">entertainment videos</b> anytime, anywhere.
                </p>

                <div style="text-align: center; margin: 20px 0;">
                    <a href="https://demo.reeloid.app/" 
                    style="background: #D4AF37; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold;">
                    Login Now
                    </a>
                </div>

                <p style="font-size: 16px; color: #333; text-align: center;">
                    <b>- Rohit Gupta (C.E.O)</b><br>
                    <i style="color: #D4AF37;">Reeloid: Vertical Movies and Series on the Go</i>
                </p>
            </div>
        </body>
        </html>
        """
        # Create the email message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = from_email
        message["To"] = recipient_email
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
        return f"Failed to send email: {err}"
