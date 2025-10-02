"""Email sending functionality."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

class EmailSender:
    def __init__(self, smtp_server: str, port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password
    
    def send_email(self, to: List[str], subject: str, body: str) -> bool:
        """Send email to recipients."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = ', '.join(to)
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
