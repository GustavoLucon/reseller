from flask import Flask, request, jsonify
import requests
import time
import random

app = Flask(__name__)

orders = {}
next_order_id = 1

resellers_data = {
    1: {'cnpj': '12345678901234'},
    2: {'cnpj': '98765432109876'}
}

BEER_SELLER_API_URL = "http://localhost:5001/beer_seller/orders"
MAX_RETRIES = 3
RETRY_DELAY = 5

def place_beer_seller_order(reseller_id, order_items):
    total_quantity = sum(item['quantity'] for item in order_items)
    if total_quantity < 1000:
        return {"error": "Minimum order quantity of 1000 units not met"}, 400

    beer_seller_payload = {
        'reseller_cnpj': resellers_data.get(reseller_id, {}).get('cnpj'),
        'items': [{'product_code': item['product_id'], 'amount': item['quantity']} for item in order_items]
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(BEER_SELLER_API_URL, json=beer_seller_payload)
            response.raise_for_status()
            return response.json(), response.status_code
        except requests.exceptions.RequestException as e:
            print(f"Error placing order with Beer Seller (attempt {attempt + 1}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                return {"error": "Failed to place order with Beer Seller after multiple retries"}, 500

@app.route('/resellers/<int:reseller_id>/orders', methods=['POST'])
def receive_customer_order(reseller_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "No order data provided"}), 400

    customer_id = data.get('customer_identification')
    products = data.get('products')

    if not customer_id:
        return jsonify({"error": "Customer identification is required"}), 400
    if not products or not isinstance(products, list):
        return jsonify({"error": "Products list is required"}), 400

    global next_order_id
    order_id = next_order_id
    next_order_id += 1

    orders[order_id] = {
        'reseller_id': reseller_id,
        'customer_id': customer_id,
        'items': products
    }

    return jsonify({"order_id": order_id, "items_requested": products}), 201

@app.route('/resellers/<int:reseller_id>/place_beer_seller_order', methods=['POST'])
def place_reseller_beer_seller_order(reseller_id):
    data = request.get_json()
    if not data or 'order_items' not in data:
        return jsonify({"error": "Order items are required"}), 400

    order_items = data['order_items']
    beer_seller_response, status_code = place_beer_seller_order(reseller_id, order_items)

    return jsonify(beer_seller_response), status_code

if __name__ == '__main__':
    app.run(debug=True, port=5002)