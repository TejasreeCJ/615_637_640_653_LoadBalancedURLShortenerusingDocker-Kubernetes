import os
import redis
import hashlib
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

# Use environment variables for Redis connection
REDIS_HOST = os.getenv("REDIS_HOST", "redis")  # Docker network hostname
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")  # Change to service name or load balancer URL in production

# Connect to Redis
try:
    redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    redis_client.ping()  # Test connection
except redis.ConnectionError:
    print("Error: Unable to connect to Redis")
    exit(1)

@app.route('/')
def index():
    return '''
    <h2>Welcome to the URL Shortener</h2>
    <p>Use <code>POST /shorten</code> with JSON body: <code>{"url": "https://example.com"}</code> to get a short URL.</p>
    '''

@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get("url")

    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    # Generate a short hash for the URL
    short_hash = hashlib.md5(original_url.encode()).hexdigest()[:6]

    # Store in Redis with a 30-day expiry
    redis_client.setex(short_hash, 2592000, original_url)

    short_url = f"{BASE_URL}/{short_hash}"
    return jsonify({"short_url": short_url}), 201

@app.route('/<short_hash>')
def redirect_url(short_hash):
    original_url = redis_client.get(short_hash)
    
    if original_url:
        return redirect(original_url)
    
    return jsonify({"error": "URL not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
