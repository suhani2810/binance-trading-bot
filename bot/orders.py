"""Order placement logic — sits between the CLI and the raw API client."""

from typing import Any

from .client import BinanceClient, BinanceAPIError
from .logging_config import setup_logger
from .validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
    ValidationError,
)

logger = setup_logger("trading_bot.orders")


def _build_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
    stop_price: float | None = None,
) -> dict:
    params: dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "type": order_type if order_type != "STOP_LIMIT" else "STOP",
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        params["price"] = price
        params["timeInForce"] = "GTC"

    elif order_type == "STOP_LIMIT":
        params["price"] = price          # limit price (execution price)
        params["stopPrice"] = stop_price  # trigger price
        params["timeInForce"] = "GTC"

    return params


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
    stop_price: str | None = None,
) -> dict:
    """Validate inputs, place an order, and return the API response."""

    # validation
    try:
        symbol = validate_symbol(symbol)
        side = validate_side(side)
        order_type = validate_order_type(order_type)
        qty = validate_quantity(quantity)
        lmt_price = validate_price(price, order_type)
        stp_price = validate_stop_price(stop_price, order_type)
    except ValidationError as exc:
        logger.error("Validation failed: %s", exc)
        raise

    params = _build_order_params(symbol, side, order_type, qty, lmt_price, stp_price)

    logger.info(
        "Placing %s %s order | symbol=%s qty=%s%s",
        side,
        order_type,
        symbol,
        qty,
        f" price={lmt_price}" if lmt_price else "",
    )

    try:
        response = client.place_order(**params)
    except BinanceAPIError as exc:
        logger.error("API error placing order: %s", exc)
        raise
    except (ConnectionError, TimeoutError) as exc:
        logger.error("Network error: %s", exc)
        raise

    logger.info(
        "Order placed successfully | orderId=%s status=%s executedQty=%s",
        response.get("orderId"),
        response.get("status"),
        response.get("executedQty"),
    )
    return response
