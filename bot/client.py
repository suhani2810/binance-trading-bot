"""Low-level Binance Futures Testnet REST client."""

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import requests

from .logging_config import setup_logger

BASE_URL = "https://testnet.binancefuture.com"
logger = setup_logger("trading_bot.client")


class BinanceAPIError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API error {code}: {message}")


class BinanceClient:
    """Thin wrapper around the Binance Futures Testnet REST API."""

    def __init__(self, api_key: str, api_secret: str, timeout: int = 10):
        if not api_key or not api_secret:
            raise ValueError("API key and secret must not be empty.")
        self._api_key = api_key
        self._api_secret = api_secret.encode()
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-MBX-APIKEY": self._api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )

    # ------------------------------------------------------------------ #
    # Internals                                                            
    # ------------------------------------------------------------------ #

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query = urlencode(params)
        signature = hmac.new(self._api_secret, query.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature
        return params

    def _request(self, method: str, path: str, params: dict | None = None, signed: bool = True) -> Any:
        params = params or {}
        if signed:
            params = self._sign(params)

        url = BASE_URL + path
        logger.debug("→ %s %s | params: %s", method.upper(), path, {k: v for k, v in params.items() if k != "signature"})

        try:
            resp = self._session.request(
                method,
                url,
                params=params if method.upper() == "GET" else None,
                data=params if method.upper() == "POST" else None,
                timeout=self._timeout,
            )
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network error: %s", exc)
            raise ConnectionError(f"Unable to reach Binance testnet: {exc}") from exc
        except requests.exceptions.Timeout:
            logger.error("Request timed out after %ss", self._timeout)
            raise TimeoutError(f"Request to {path} timed out.")

        logger.debug("← %s %s", resp.status_code, resp.text[:500])

        data = resp.json()
        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            raise BinanceAPIError(data["code"], data.get("msg", "Unknown error"))

        return data

    # ------------------------------------------------------------------ #
    # Public helpers                                                       
    # ------------------------------------------------------------------ #

    def get_account(self) -> dict:
        """Fetch futures account information."""
        return self._request("GET", "/fapi/v2/account")

    def place_order(self, **kwargs) -> dict:
        """Place an order. kwargs are forwarded directly to the API."""
        return self._request("POST", "/fapi/v1/order", params=kwargs)

    def get_order(self, symbol: str, order_id: int) -> dict:
        """Query a specific order by ID."""
        return self._request("GET", "/fapi/v1/order", params={"symbol": symbol, "orderId": order_id})
