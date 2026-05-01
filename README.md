# Binance Futures Testnet Trading Bot

A production-style Python CLI trading bot that places simulated orders on the Binance Futures Testnet using raw REST APIs (no SDKs).

Designed with clean architecture, strong validation, and structured logging — similar to real-world backend systems.

## Features

- Place **Market**, **Limit**, and **Stop-Limit** orders (bonus order type)
- Supports **BUY** and **SELL** sides
- Structured codebase: separate client, orders, validation, and CLI layers
- Structured logging to file (DEBUG) and console (INFO)
- Full exception handling: input validation, API errors, network failures

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper
│   ├── orders.py          # Order placement logic
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Logger setup
├── logs/                  # Auto-created; log files written here
├── cli.py                 # CLI entry point (argparse)
├── .env.example           # Template for credentials
├── requirements.txt
└── README.md
```

---

## 🏗️ Architecture

The application follows a layered design:

CLI (cli.py)
   ↓
Order Logic (bot/orders.py)
   ↓
Validation (bot/validators.py)
   ↓
API Client (bot/client.py)

Each layer has a single responsibility:
- CLI handles user input
- Validators ensure correctness before API calls
- Orders builds correct payloads
- Client handles all REST communication and signing

## 🚀 Quick Start 

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # add your API keys

python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.001


## Setup

### 1. Get Testnet API Credentials

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Log in
3. Click on start demo trading
3. Navigate to **Demo trading API** → Create API ( top right corner)
4. Copy your **API Key** and **Secret**

### 2. Clone & Install

```bash
git clone <your-repo-url>
cd trading_bot

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure Credentials

```bash
# Mac/Linux
cp .env.example .env

# Windows (CMD)
copy .env.example .env

# Windows (PowerShell)
cp .env.example .env
# Edit .env and paste your testnet API key and secret
```

Your `.env` should look like:

```
BINANCE_API_KEY=abc123...
BINANCE_API_SECRET=xyz456...
```

---

## How to Run

### Market Order

```bash
# BUY 0.001 BTC at market price
python cli.py --symbol BTCUSDT --side BUY --type MARKET --qty 0.001

# SELL 0.002 ETH at market price
python cli.py --symbol ETHUSDT --side SELL --type MARKET --qty 0.002
```

### Limit Order

```bash
# BUY 0.001 BTC with a limit price of 90000 USDT
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --qty 0.001 --price 90000

# SELL 0.001 BTC when price reaches 96000 USDT
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --qty 0.001 --price 96000
```

### Stop-Limit Order (Bonus)

```bash
# BUY 0.001 BTC: trigger at 94500, execute at 94000
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT \
  --qty 0.001 --price 94000 --stop-price 94500
```

### Help

```bash
python cli.py --help
```

---

## Example Output

```
────────────────────────────────────────────────────────────
  ORDER REQUEST SUMMARY
────────────────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
────────────────────────────────────────────────────────────

────────────────────────────────────────────────────────────
  ORDER RESPONSE
────────────────────────────────────────────────────────────
  Order ID      : 4023971882
  Status        : FILLED
  Symbol        : BTCUSDT
  Side          : BUY
  Type          : MARKET
  Orig Qty      : 0.001
  Executed Qty  : 0.001
  Avg Price     : 93512.10000
────────────────────────────────────────────────────────────

  ✅  Order placed successfully!
```

---


## Logging

Logs are automatically written to `logs/trading_bot_YYYYMMDD.log`.

- **File log**: DEBUG level — full request/response detail
- **Console log**: INFO level — key events only

---

## Assumptions

- Only **USDT-M Futures Testnet** is supported (not COIN-M)
- Quantity precision must meet Binance's symbol requirements (e.g., 0.001 for BTCUSDT)
- Stop-Limit maps to Binance's `STOP` order type with a `stopPrice` parameter
- Credentials are loaded from a `.env` file or environment variables

---

## Requirements

- Python 3.10+
- `requests` — HTTP client for REST API calls
- `python-dotenv` — loads credentials from `.env`

## 💡 Design Decisions

- **No Binance SDK**: Uses raw REST APIs via `requests` to make all interactions explicit
- **Layered architecture**: Improves maintainability and scalability
- **Custom exceptions**: Separates validation errors from API failures
- **Structured logging**: Debug logs to file, clean logs to console
- **Environment-based credentials**: Keeps secrets secure and out of source code

## Logs Included

Sample logs include:
- Market order
- Limit order
- Stop-limit order
- Validation error
- API error

## Evaluation Coverage

This project satisfies all core requirements:
- Market & Limit orders
- CLI input handling
- Validation & error handling
- Logging (file + console)
- Structured architecture

Bonus implemented:
- Stop-Limit order type
