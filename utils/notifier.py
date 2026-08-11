"""
Email Notification Engine.
Sends HTML and Plaintext email alerts whenever a new trade signal is detected.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class EmailNotifier:
    def __init__(self):
        self.enabled = os.getenv("ENABLE_EMAIL_ALERTS", "false").lower() == "true"
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL", "")

    def send_trade_signal_email(self, rec: Dict) -> bool:
        """
        Sends an email alert with trade setup details and duration guidance.
        Returns True if sent successfully, False otherwise.
        """
        if not self.enabled:
            # Email alerts disabled in config/env
            return False

        if not self.sender_email or not self.sender_password or not self.recipient_email:
            print("[!] Email notification skipped: Sender/Recipient credentials missing in environment.")
            return False

        subject = f"🔥 [TRADE SIGNAL] {rec['action']} {rec['pair']} - MT5 Execution Alert"
        dur = rec.get("duration", {})
        
        # Plaintext Email Body
        text_body = f"""
============================================================
 NEW TRADING SIGNAL DETECTED: {rec['pair']}
============================================================
 Pair / Asset        : {rec['pair']} ({rec['tier']})
 MT5 Ticker          : {rec['ticker']}
 Action              : {rec['action']} LIMIT / MARKET
 Entry Price         : {rec['entry']:.5f}
 Stop Loss           : {rec['stop_loss']:.5f} ({rec['sl_pips']:.1f} pips)
 Take Profit         : {rec['take_profit']:.5f} (1:3 R:R Target)
 Max Risk (1%)       : ${rec['dollar_risk']:.2f}
 Recommended Lots    : {rec['lot_size']} Lots
 Signal Rationale    : {rec['reason']}

------------------------------------------------------------
 DURATION & HOLDING TIME GUIDANCE
------------------------------------------------------------
 Trade Style        : {dur.get('style', 'Day Trade')}
 Estimated Duration : {dur.get('estimated_duration', '4 to 8 Hours')}
 Max Expiry Limit   : {dur.get('max_expiry', '24 Hours')}
============================================================
"""

        # HTML Email Body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f6f8; padding: 20px;">
          <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #e0e0e0;">
            <div style="background-color: #1a237e; color: #ffffff; padding: 20px; text-align: center;">
              <h2 style="margin: 0;">🔥 Trade Signal Recommendation</h2>
              <p style="margin: 5px 0 0 0; font-size: 14px;">Automated Forex & MT5 Execution Alert</p>
            </div>
            <div style="padding: 20px;">
              <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Pair / Asset:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{rec['pair']} ({rec['tier']})</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Action:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee; color: {'#2e7d32' if rec['action'] == 'BUY' else '#c62828'}; font-weight: bold;">{rec['action']}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Entry Price:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{rec['entry']:.5f}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Stop Loss:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{rec['stop_loss']:.5f} ({rec['sl_pips']:.1f} pips)</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Take Profit:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{rec['take_profit']:.5f} (1:3 Target)</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Max Risk (1%):</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">${rec['dollar_risk']:.2f}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Recommended Lots:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>{rec['lot_size']} Lots</b></td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Rationale:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{rec['reason']}</td></tr>
              </table>
              
              <div style="margin-top: 20px; padding: 15px; background: #e8eaf6; border-radius: 6px;">
                <h4 style="margin: 0 0 10px 0; color: #1a237e;">⏱️ Duration & Holding Guidance</h4>
                <p style="margin: 3px 0;"><b>Trade Style:</b> {dur.get('style', 'Day Trade')}</p>
                <p style="margin: 3px 0;"><b>Estimated Duration:</b> {dur.get('estimated_duration', '4 to 8 Hours')}</p>
                <p style="margin: 3px 0;"><b>Max Expiry Limit:</b> {dur.get('max_expiry', '24 Hours')}</p>
              </div>
            </div>
          </div>
        </body>
        </html>
        """

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = self.recipient_email
            
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, msg.as_string())
                
            print(f"  [📧 EMAIL ALERT SENT] Pushed signal for {rec['pair']} to {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"  [!] Failed to send email alert: {e}")
            return False
