import hmac, hashlib, time, requests
from urllib.parse import urlencode
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv('BINANCE_API_KEY')
secret = os.getenv('BINANCE_API_SECRET')

params = {'timestamp': int(time.time() * 1000)}
query = urlencode(params)
sig = hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()
params['signature'] = sig

print('Key:', repr(key))
print('Secret:', repr(secret))

r = requests.get(
    'https://testnet.binancefuture.com/fapi/v2/account',
    params=params,
    headers={'X-MBX-APIKEY': key}
)
print('Status:', r.status_code)
print('Response:', r.text)