from flask import Flask, request, jsonify
import time
import random

app = Flask(__name__)

beer_seller_orders = {}
next_beer_seller_order_number = 1000

@app.route('/beer_seller/orders', methods=['POST'])
def receive_beer_seller_order():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No order data received"}), 400

    reseller_cnpj = data.get('reseller_cnpj')
    items = data.get('items')

    if not reseller_cnpj:
        return jsonify({"error": "Reseller CNPJ is required"}), 400
    if not items or not isinstance(items, list):
        return jsonify({"error": "Order items are required"}), 400

    if random.random() < 0.3:
        time.sleep(random.uniform(1, 5))
        return jsonify({"error": "Beer Seller API is temporarily unavailable"}), 503

    global next_beer_seller_order_number
    order_number = next_beer_seller_order_number
    next_beer_seller_order_number += 1

    beer_seller_orders[order_number] = {
        'reseller_cnpj': reseller_cnpj,
        'items': items
    }

    return jsonify({"order_number": order_number, "items_accepted": items}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5001)