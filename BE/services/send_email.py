import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

load_dotenv()  # 환경 변수 로드

# 이메일 보내기 함수
def send_email(buyer_email, title, content, attachment=None):
    # 보내는 이메일 계정 설정
    sender_email = os.getenv("SENDER_EMAIL_ID")
    sender_password = os.getenv("SENDER_EMAIL_PASSWORD")

    # 이메일 서버 설정
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
   
    smpt = smtplib.SMTP_SSL(smtp_server, smtp_port)

    smpt.login(sender_email, sender_password)

    # 이메일 메시지 생성
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = buyer_email
    message['Subject'] = title

    # 이메일 본문 추가
    message.attach(MIMEText(content, 'plain'))

    # 첨부 파일 추가 (선택 사항)
    if attachment:
        with open(attachment, 'rb') as file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(attachment)}')
        message.attach(part)

    smpt.send_message(message)
