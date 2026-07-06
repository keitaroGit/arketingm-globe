import os, time, requests
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

ALPHA_KEY = os.environ.get('ALPHA_VANTAGE_KEY', '')

# ── Cache ─────────────────────────────────────────────────────────────────────
price_cache = {}   # { ticker: { price, change, change_pct, updated_at } }
CACHE_TTL = 900    # 15 minutes

TICKERS = [
    'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META',
    'JPM', 'V', 'MA', 'BRK.B',
    'LLY', 'UNH', 'JNJ', 'MRK',
    'XOM', 'CVX',
    'LMT', 'RTX', 'NOC',
    'TSLA', 'AVGO', 'ORCL', 'CRM', 'CSCO',
    'HD', 'WMT', 'COST', 'KO', 'PEP',
    'TSM',
]

def fetch_price(ticker):
    """Fetch single ticker from Alpha Vantage GLOBAL_QUOTE"""
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': ticker,
        'apikey': ALPHA_KEY,
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        data = r.json().get('Global Quote', {})
        if not data:
            return None
        return {
            'ticker': ticker,
            'price': float(data.get('05. price', 0)),
            'change': float(data.get('09. change', 0)),
            'change_pct': data.get('10. change percent', '0%').replace('%', ''),
            'updated_at': time.time(),
        }
    except Exception as e:
        print(f'Error fetching {ticker}: {e}')
        return None

def get_cached_price(ticker):
    """Return cached price or fetch fresh"""
    now = time.time()
    cached = price_cache.get(ticker)
    if cached and (now - cached['updated_at']) < CACHE_TTL:
        return cached
    result = fetch_price(ticker)
    if result:
        price_cache[ticker] = result
        return result
    return cached  # return stale if fetch failed

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('static', 'globe.html')

@app.route('/api/prices')
def api_prices():
    """Return prices for all tickers — uses cache, max 5 fresh fetches per call"""
    results = {}
    fetched = 0
    for ticker in TICKERS:
        now = time.time()
        cached = price_cache.get(ticker)
        if cached and (now - cached['updated_at']) < CACHE_TTL:
            results[ticker] = cached
        elif fetched < 5:
            # Alpha Vantage free = 5 req/min, fetch staggered
            result = fetch_price(ticker)
            if result:
                price_cache[ticker] = result
                results[ticker] = result
            fetched += 1
            if fetched < 5:
                time.sleep(0.5)
        else:
            # Return stale cache if over limit
            if cached:
                results[ticker] = cached
    return jsonify({'prices': results, 'cached_count': len(price_cache)})

@app.route('/api/price/<ticker>')
def api_single_price(ticker):
    """Single ticker price"""
    ticker = ticker.upper()
    data = get_cached_price(ticker)
    if data:
        return jsonify(data)
    return jsonify({'error': 'not found'}), 404

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'ok',
        'cached_tickers': len(price_cache),
        'alpha_key_set': bool(ALPHA_KEY),
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
