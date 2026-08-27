"""
Automated MetaTrader 5 (MT5) Execution Bridge.
Supports Native MT5 Terminal API and MT5 Web REST Gateway for 100% automated order execution.
"""
import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Attempt to import Windows-native MetaTrader5 package if available
try:
    import MetaTrader5 as mt5
    HAS_MT5_NATIVE = True
except ImportError:
    HAS_MT5_NATIVE = False

class MT5ExecutionBridge:
    def __init__(self):
        self.enabled = os.getenv("MT5_DEMO_ENABLED", "false").lower() == "true"
        self.login = int(os.getenv("MT5_LOGIN", "0")) if os.getenv("MT5_LOGIN", "").isdigit() else None
        self.password = os.getenv("MT5_PASSWORD", "")
        self.server = os.getenv("MT5_SERVER", "MetaQuotes-Demo")
        self.web_api_url = os.getenv("MT5_WEB_API_URL", "https://trade.mql5.com/trade")
        self.metaapi_token = os.getenv("METAAPI_TOKEN", "")
        self.metaapi_account_id = os.getenv("METAAPI_ACCOUNT_ID", "")
        self.metaapi_url = os.getenv("METAAPI_URL", "https://mt-client-api-v1.new-york.agiliumtrade.ai")

    def connect(self) -> bool:
        """
        Initializes connection to the MT5 terminal session using credentials from .env.
        """
        if not self.enabled:
            return False

        if HAS_MT5_NATIVE:
            if not mt5.initialize():
                print(f"[!] MT5 Initialization failed: {mt5.last_error()}")
                return False

            if self.login and self.password:
                authorized = mt5.login(login=self.login, password=self.password, server=self.server)
                if not authorized:
                    print(f"[!] Failed to log into MT5 Account {self.login} on {self.server}: {mt5.last_error()}")
                    return False
                print(f"[+] Successfully connected to Native MT5 Account {self.login} on {self.server}")
                return True
        else:
            print(f"[+] MT5 Web Gateway active for Account {self.login} on {self.server}")
            return True

        return False

    def place_automated_order(self, rec: Dict) -> Optional[Dict]:
        """
        Pushes automated BUY/SELL order request to MT5 Demo account.
        """
        if not self.enabled:
            return None

        symbol = rec['pair'].replace("/", "").replace("=X", "").replace("GC=F", "XAUUSD")

        # 1. Try Native MT5 API first if running on Windows / Wine
        if HAS_MT5_NATIVE:
            if self.connect():
                if not mt5.symbol_select(symbol, True):
                    print(f"[!] Symbol {symbol} not found in MT5 Market Watch.")
                    return None

                order_type = mt5.ORDER_TYPE_BUY if rec['action'] == 'BUY' else mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(symbol).ask if rec['action'] == 'BUY' else mt5.symbol_info_tick(symbol).bid

                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": symbol,
                    "volume": float(rec['lot_size']),
                    "type": order_type,
                    "price": price,
                    "sl": float(rec['stop_loss']),
                    "tp": float(rec['take_profit']),
                    "deviation": 20,
                    "magic": 100200,
                    "comment": "Python Quant Bot Auto Order",
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }

                result = mt5.order_send(request)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(f"[-] MT5 Order Send Failed for {symbol}: Code {result.retcode} ({result.comment})")
                    return None

                print(f"[🚀 NATIVE MT5 ORDER EXECUTED] Ticket #{result.order} | Symbol: {symbol} | Lots: {rec['lot_size']} | Entry: {price:.5f}")
                return {
                    "order_ticket": result.order,
                    "symbol": symbol,
                    "price": price,
                    "status": "EXECUTED"
                }

        # 2. MT5 Web REST Gateway Fallback (Linux / Multi-Platform)
        return self._send_web_api_order(symbol, rec)

    def _send_web_api_order(self, symbol: str, rec: Dict) -> Optional[Dict]:
        """
        Sends order request via MetaAPI Cloud REST API (Linux / Multi-Platform fallback).
        """
        if not self.metaapi_token or not self.metaapi_account_id:
            print("[!] MetaAPI Gateway skipped: METAAPI_TOKEN or METAAPI_ACCOUNT_ID missing in .env")
            return None

        endpoint = f"{self.metaapi_url}/users/current/accounts/{self.metaapi_account_id}/trade"
        headers = {
            "auth-token": self.metaapi_token,
            "Content-Type": "application/json"
        }
        
        # MetaAPI expects ORDER_TYPE_BUY or ORDER_TYPE_SELL
        action_type = "ORDER_TYPE_BUY" if rec['action'] == 'BUY' else "ORDER_TYPE_SELL"

        payload = {
            "actionType": action_type,
            "symbol": symbol,
            "volume": float(rec['lot_size']),
            "stopLoss": float(rec['stop_loss']),
            "takeProfit": float(rec['take_profit']),
            "stopLossUnits": "ABSOLUTE_PRICE",
            "takeProfitUnits": "ABSOLUTE_PRICE",
            "comment": "Python Quant MetaAPI Auto Order"
        }

        try:
            print(f"[⏳ METAAPI DISPATCHING] Account: {self.metaapi_account_id} | Symbol: {symbol} | Action: {action_type} | Lots: {rec['lot_size']} | SL: {rec['stop_loss']:.5f} | TP: {rec['take_profit']:.5f}")
            response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            print(f"[🚀 METAAPI ORDER EXECUTED] Result: {result}")
            return {
                "status": "EXECUTED_VIA_METAAPI",
                "symbol": symbol,
                "metaapi_response": result
            }
        except Exception as e:
            print(f"[!] MetaAPI Execution Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[!] MetaAPI Error Details: {e.response.text}")
            return None

    def shutdown(self):
        """Closes MT5 connection cleanly."""
        if HAS_MT5_NATIVE:
            mt5.shutdown()
