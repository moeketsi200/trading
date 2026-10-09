"""
Email Notification Engine.
Sends HTML and Plaintext email alerts whenever a new trade signal is detected.
"""
import os
import smtplib
import requests
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
        rr = rec.get("reward_risk_ratio", 3)
        
        # Plaintext Email Body
        text_body = f"""
============================================================
 NEW TRADING SIGNAL DETECTED: {rec['pair']}
============================================================
 Pair / Asset        : {rec['pair']} ({rec['tier']})
 MT5 Symbol          : {rec.get('mt5_symbol', rec['ticker'])}
 Action              : {rec['action']} LIMIT / MARKET
 Entry Price         : {rec['entry']:.5f}
 Stop Loss           : {rec['stop_loss']:.5f} ({rec['sl_pips']:.1f} pips)
 Take Profit         : {rec['take_profit']:.5f} (1:{rr:g} R:R Target)
 Max Risk (1%)       : ${rec['dollar_risk']:.2f}
 Recommended Lots    : {rec['lot_size']} Lots
 Signal Rationale    : {rec['reason']}
 Fundamental Bias    : {rec.get('fundamental_bias', 'N/A')}

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
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>MT5 Symbol:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{rec.get('mt5_symbol', rec['ticker'])}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Action:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee; color: {'#2e7d32' if rec['action'] == 'BUY' else '#c62828'}; font-weight: bold;">{rec['action']}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Entry Price:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{rec['entry']:.5f}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Stop Loss:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{rec['stop_loss']:.5f} ({rec['sl_pips']:.1f} pips)</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Take Profit:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{rec['take_profit']:.5f} (1:{rr:g} Target)</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Max Risk (1%):</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">${rec['dollar_risk']:.2f}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Recommended Lots:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>{rec['lot_size']} Lots</b></td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Rationale:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{rec['reason']}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #eee;"><b>Fundamental Bias:</b></td><td style="padding: 8px; border-bottom: 1px solid #eee;">{rec.get('fundamental_bias', 'N/A')}</td></tr>
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

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        alert_flag = os.getenv("ENABLE_TELEGRAM_ALERTS", "").lower()
        if alert_flag == "false":
            self.enabled = False
        else:
            self.enabled = bool(self.bot_token) and bool(self.chat_id)

    def send_test_message(self, text: str = "✅ Telegram notifications are active.") -> bool:
        if not self.enabled:
            return False

        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                },
                timeout=10,
            )
            if response.status_code == 200:
                print("  [📲 TELEGRAM TEST SENT]")
                return True
            print(f"  [!] Telegram test error: {response.text}")
            return False
        except Exception as e:
            print(f"  [!] Failed to send Telegram test message: {e}")
            return False

    def send_trade_signal(self, rec: Dict) -> bool:
        if not self.enabled:
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        action_emoji = "🟢" if rec['action'] == "BUY" else "🔴"
        action_badge = f"{rec['action']} LIMIT / MARKET"
        rr = rec.get("reward_risk_ratio", 3)
        rr_label = f"1:{rr:g} R:R Runner" if rec.get("break_even_trigger") else f"1:{rr:g} R:R Target"
        dur = rec.get("duration", {})
        mt5_sym = rec.get('mt5_symbol', rec['ticker'])
        sl_pips = rec.get('sl_pips', 0.0)

        lines = [
            f"🔥 <b>[TRADE RECOMMENDATION: {rec['pair']}]</b>",
            f"<i>{rec['tier']}</i>",
            "━━━━━━━━━━━━━━━━━━━━━━",
            f"🔹 <b>MT5 Symbol:</b> <code>{mt5_sym}</code>",
            f"{action_emoji} <b>Action:</b> <b>{action_badge}</b>",
            f"📍 <b>Entry Price:</b> <code>{rec['entry']:.5f}</code>",
            f"🛑 <b>Stop Loss:</b> <code>{rec['stop_loss']:.5f}</code> ({sl_pips:.1f} pips)",
            f"🎯 <b>Take Profit:</b> <code>{rec['take_profit']:.5f}</code> ({rr_label})",
        ]

        if rec.get("break_even_trigger"):
            lines.extend([
                f"🛡️ <b>Trade Management:</b> Move SL to BE at <code>{rec['break_even_trigger']:.5f}</code>",
                f"📈 <b>Trailing Stop:</b> Trail SL behind 1H EMA 50 after BE",
            ])

        lines.extend([
            f"💰 <b>Max Risk (1%):</b> ${rec['dollar_risk']:.2f}",
            f"📊 <b>Recommended Lots:</b> <b>{rec['lot_size']} Lots</b>",
            f"💡 <b>Signal Rationale:</b> {rec['reason']}",
            f"⚖️ <b>Fundamental Bias:</b> {rec.get('fundamental_bias', 'N/A')}",
            "━━━━━━━━━━━━━━━━━━━━━━",
            "⏱️ <b>DURATION & HOLDING GUIDANCE:</b>",
            f"• <b>Trade Style:</b> {dur.get('style', 'Day Trade')}",
            f"• <b>Estimated Duration:</b> {dur.get('estimated_duration', '4 to 8 Hours')}",
            f"• <b>Max Expiry Limit:</b> {dur.get('max_expiry', '24 Hours')}",
        ])

        text = "\n".join(lines)

        try:
            response = requests.post(url, json={
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML"
            }, timeout=10)
            if response.status_code == 200:
                print(f"  [📲 TELEGRAM ALERT SENT] Pushed signal for {rec['pair']}")
                return True
            else:
                print(f"  [!] Telegram error: {response.text}")
                return False
        except Exception as e:
            print(f"  [!] Failed to send Telegram alert: {e}")
            return False
