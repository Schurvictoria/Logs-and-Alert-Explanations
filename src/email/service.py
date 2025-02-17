import smtplib
from email.mime.text import MIMEText
from typing import List


def send_email(host: str, port: int, user: str, password: str, from_addr: str, to_addrs: List[str], subject: str, html: str) -> bool:
    try:
        msg = MIMEText(html, "html", "utf-8")
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = ", ".join(to_addrs)

        with smtplib.SMTP(host, port) as s:
            s.starttls()
            if user:
                s.login(user, password)
            s.sendmail(from_addr, to_addrs, msg.as_string())
        return True
    except Exception:
        return False


def build_anomaly_html(title: str, anomalies: List[str]) -> str:
    items = "".join(f"<li>{x}</li>" for x in anomalies[:20])
    return f"""
    <html><body>
    <h3>{title}</h3>
    <ul>{items}</ul>
    </body></html>
    """

