#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet trading bot.

Usage examples:
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.001
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 95000
  python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --qty 0.001 --price 94000 --stop-price 94500
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logger
from bot.orders import place_order
from bot.validators import ValidationError

load_dotenv()
logger = setup_logger("trading_bot.cli")

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _print_separator(char: str = "─", width: int = 60) -> None:
    print(char * width)


def _print_request_summary(args: argparse.Namespace) -> None:
    _print_separator()
    print("  ORDER REQUEST SUMMARY")
    _print_separator()
    print(f"  Symbol     : {args.symbol.upper()}")
    print(f"  Side       : {args.side.upper()}")
    print(f"  Type       : {args.type.upper()}")
    print(f"  Quantity   : {args.qty}")
    if args.price:
        print(f"  Price      : {args.price}")
    if args.stop_price:
        print(f"  Stop Price : {args.stop_price}")
    _print_separator()
    print()


def _print_response(response: dict) -> None:
    _print_separator()
    print("  ORDER RESPONSE")
    _print_separator()
    fields = [
        ("Order ID",      "orderId"),
        ("Status",        "status"),
        ("Symbol",        "symbol"),
        ("Side",          "side"),
        ("Type",          "type"),
        ("Orig Qty",      "origQty"),
        ("Executed Qty",  "executedQty"),
        ("Avg Price",     "avgPrice"),
        ("Price",         "price"),
        ("Client OID",    "clientOrderId"),
        ("Update Time",   "updateTime"),
    ]
    for label, key in fields:
        value = response.get(key)
        if value is not None and value != "":
            print(f"  {label:<14}: {value}")
    _print_separator()


# ─────────────────────────────────────────────────────────────────────────────
# Argument parsing
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place orders on Binance Futures Testnet (USDT-M)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  Market buy:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.001

  Limit sell:
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 95000

  Stop-Limit buy:
    python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --qty 0.001 \\
      --price 94000 --stop-price 94500
        """,
    )
    parser.add_argument("--symbol",     required=True, help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--side",       required=True, choices=["BUY", "SELL", "buy", "sell"], help="Order side")
    parser.add_argument("--type",       required=True, dest="type",
                        choices=["MARKET", "LIMIT", "STOP_LIMIT", "market", "limit", "stop_limit"],
                        help="Order type")
    parser.add_argument("--qty",        required=True, help="Order quantity")
    parser.add_argument("--price",      default=None, help="Limit price (required for LIMIT / STOP_LIMIT)")
    parser.add_argument("--stop-price", default=None, dest="stop_price",
                        help="Stop trigger price (required for STOP_LIMIT)")
    return parser


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # Load credentials from environment
    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")

    if not api_key or not api_secret:
        logger.error(
            "Missing API credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET "
            "in your environment or in a .env file."
        )
        print("\n[ERROR] API credentials not found. See README for setup instructions.\n")
        return 1

    _print_request_summary(args)

    client = BinanceClient(api_key=api_key, api_secret=api_secret)

    try:
        response = place_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.type.upper(),
            quantity=args.qty,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValidationError as exc:
        print(f"\n[VALIDATION ERROR] {exc}\n")
        return 1
    except BinanceAPIError as exc:
        print(f"\n[API ERROR] {exc}\n")
        return 1
    except (ConnectionError, TimeoutError) as exc:
        print(f"\n[NETWORK ERROR] {exc}\n")
        return 1
    except Exception as exc:
        logger.exception("Unexpected error: %s", exc)
        print(f"\n[ERROR] Unexpected error: {exc}\n")
        return 1

    _print_response(response)
    print("\n  ✅  Order placed successfully!\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
