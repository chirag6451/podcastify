import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Email configuration
SMTP_HOST = "smtp.maileroo.com"
SMTP_PORT = 587
SMTP_USERNAME = "info@indapoint.org"
SMTP_PASSWORD = "65495cbbe550dd802a4de262"

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        self.smtp_host = SMTP_HOST
        self.smtp_port = SMTP_PORT
        self.username = SMTP_USERNAME
        self.password = SMTP_PASSWORD

    def send_video_upload_notification(self, video_title: str, video_url: str, recipient_email: str) -> bool:
        """
        Send an email notification when a video is successfully uploaded
        
        Args:
            video_title: Title of the uploaded video
            video_url: URL of the uploaded video
            recipient_email: Email address of the recipient
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = recipient_email
            msg['Subject'] = f"Video Upload Success: {video_title}"

            body = f"""
            Hello,

            Your video "{video_title}" has been successfully uploaded.
            You can view it here: {video_url}

            Best regards,
            Your Video Platform Team
            """

            msg.attach(MIMEText(body, 'plain'))

            # Create SMTP connection
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"Successfully sent upload notification email for video: {video_title}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False
