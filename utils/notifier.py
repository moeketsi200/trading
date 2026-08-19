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

    def send_heartbeat_email(self, scan_summary: dict) -> bool:
        """
        Sends a 30-minute heartbeat status report email.
        Sent at the end of every scan cycle, with or without signals.
        """
        if not self.enabled:
            return False

        if not self.sender_email or not self.sender_password or not self.recipient_email:
            return False

        signals_found = scan_summary.get("signals_found", 0)
        pairs_scanned = scan_summary.get("pairs_scanned", 0)
        cycle_number = scan_summary.get("cycle_number", 1)
        next_scan_at = scan_summary.get("next_scan_at", "N/A")
        market_snapshot = scan_summary.get("market_snapshot", [])
        mode = scan_summary.get("mode", "NORMAL")

        status_emoji = "🔥" if signals_found > 0 else "✅"
        status_label = f"{signals_found} SIGNAL(S) FOUND" if signals_found > 0 else "No Signals — Market Watching"

        subject = f"{status_emoji} [STATUS REPORT #{cycle_number}] {status_label} | Next Scan: {next_scan_at}"

        # Build market snapshot rows for HTML
        rows_html = ""
        rows_text = ""
        for item in market_snapshot:
            trend_color = "#2e7d32" if "UP" in item.get("trend", "") else "#c62828"
            rows_html += f"""
            <tr>
              <td style="padding:6px 8px; border-bottom:1px solid #eee;">{item.get('pair','')}</td>
              <td style="padding:6px 8px; border-bottom:1px solid #eee; color:{trend_color}; font-weight:bold;">{item.get('trend','')}</td>
              <td style="padding:6px 8px; border-bottom:1px solid #eee;">{item.get('price','')}</td>
              <td style="padding:6px 8px; border-bottom:1px solid #eee;">{item.get('proximity','')}</td>
            </tr>"""
            rows_text += f"  {item.get('pair',''):<20} | {item.get('trend',''):<10} | {item.get('price','')} | {item.get('proximity','')}\n"

        text_body = f"""
============================================================
 TRADING BOT — 30-MIN STATUS REPORT #{cycle_number}
============================================================
 Execution Mode   : {mode}
 Pairs Scanned    : {pairs_scanned}
 Signals Found    : {signals_found}
 Next Scan At     : {next_scan_at}
============================================================
 MARKET SNAPSHOT
------------------------------------------------------------
  {'Pair':<20} | {'Trend':<10} | Price       | Proximity
------------------------------------------------------------
{rows_text}
============================================================
"""

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background:#f4f6f8; padding:20px;">
          <div style="max-width:680px; margin:0 auto; background:#fff; border-radius:8px; overflow:hidden; border:1px solid #e0e0e0;">
            <div style="background:{'#1b5e20' if signals_found > 0 else '#1a237e'}; color:#fff; padding:20px; text-align:center;">
              <h2 style="margin:0;">{status_emoji} 30-Min Status Report #{cycle_number}</h2>
              <p style="margin:5px 0 0 0; font-size:14px;">{status_label}</p>
            </div>
            <div style="padding:20px;">
              <table style="width:100%; border-collapse:collapse; margin-bottom:20px;">
                <tr><td style="padding:8px; border-bottom:1px solid #eee;"><b>Execution Mode:</b></td><td style="padding:8px; border-bottom:1px solid #eee;">{mode}</td></tr>
                <tr><td style="padding:8px; border-bottom:1px solid #eee;"><b>Pairs Scanned:</b></td><td style="padding:8px; border-bottom:1px solid #eee;">{pairs_scanned}</td></tr>
                <tr><td style="padding:8px; border-bottom:1px solid #eee;"><b>Signals Found:</b></td><td style="padding:8px; border-bottom:1px solid #eee; font-weight:bold; color:{'#2e7d32' if signals_found > 0 else '#555'};">{signals_found}</td></tr>
                <tr><td style="padding:8px; border-bottom:1px solid #eee;"><b>Next Scan At:</b></td><td style="padding:8px; border-bottom:1px solid #eee;">{next_scan_at}</td></tr>
              </table>

              <h4 style="margin:0 0 10px 0; color:#1a237e;">📊 Market Snapshot</h4>
              <table style="width:100%; border-collapse:collapse; font-size:13px;">
                <thead>
                  <tr style="background:#e8eaf6;">
                    <th style="padding:8px; text-align:left;">Pair</th>
                    <th style="padding:8px; text-align:left;">Trend</th>
                    <th style="padding:8px; text-align:left;">Price</th>
                    <th style="padding:8px; text-align:left;">Proximity</th>
                  </tr>
                </thead>
                <tbody>{rows_html}</tbody>
              </table>
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

            print(f"  [📧 HEARTBEAT SENT] Status report #{cycle_number} delivered to {self.recipient_email}")
            return True

        except Exception as e:
            print(f"  [!] Failed to send heartbeat email: {e}")
            return False

    def send_startup_email(self) -> bool:
        """
        Sends a one-time notification when the background bot comes online.
        """
        if not self.enabled:
            return False

        if not self.sender_email or not self.sender_password or not self.recipient_email:
            return False

        subject = "🚀 [BOT ONLINE] Trading Scanner Started — Watching Markets Every 30 Minutes"
        text_body = """
============================================================
 TRADING BOT IS NOW LIVE
============================================================
 Your automated scanner has started successfully.
 It will scan all watchlist pairs every 30 minutes.
 You will receive:
   ✅ An instant email the moment a trade signal fires.
   ✅ A 30-min status report with market conditions.

 To stop the bot: run  kill $(cat bot.pid)  in terminal.
============================================================
"""
        html_body = """
        <html>
        <body style="font-family: Arial, sans-serif; background:#f4f6f8; padding:20px;">
          <div style="max-width:600px; margin:0 auto; background:#fff; border-radius:8px; overflow:hidden; border:1px solid #e0e0e0;">
            <div style="background:#1a237e; color:#fff; padding:20px; text-align:center;">
              <h2 style="margin:0;">🚀 Trading Bot Is Live</h2>
              <p style="margin:5px 0 0 0; font-size:14px;">Market Scanner Started Successfully</p>
            </div>
            <div style="padding:20px;">
              <p>Your automated forex scanner is now running in the background.</p>
              <ul>
                <li>Scans all watchlist pairs <b>every 30 minutes</b></li>
                <li>Emails you <b>instantly</b> when a trade signal fires</li>
                <li>Sends a <b>30-min status report</b> with market conditions</li>
              </ul>
              <p style="margin-top:20px; padding:12px; background:#e8eaf6; border-radius:6px; font-size:13px;">
                To stop the bot, run: <code>kill $(cat bot.pid)</code> in your terminal.
              </p>
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

            print(f"  [📧 STARTUP EMAIL SENT] Bot online notification delivered to {self.recipient_email}")
            return True

        except Exception as e:
            print(f"  [!] Failed to send startup email: {e}")
            return False
