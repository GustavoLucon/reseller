from flask import Flask, request, jsonify
import re

app = Flask(__name__)

resellers = {}
next_reseller_id = 1

def is_valid_cnpj(cnpj):
    return bool(re.match(r"^\d{14}$", cnpj))

def is_valid_business_name(name):
    return bool(name and len(name.strip()) > 0)

def is_valid_trade_name(name):
    return bool(name and len(name.strip()) > 0)

def is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def is_valid_phone(phone):
    return bool(re.match(r"^\d{8,15}$", phone))

def is_valid_contact_name(name):
    return bool(name and len(name.strip()) > 0)

def is_valid_address(address):
    return bool(address and len(address.strip()) > 0)

@app.route('/resellers', methods=['POST'])
def register_reseller():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    cnpj_num = data.get('cnpj')
    bussiness_name = data.get('business_name')
    trade_namee = data.get('trade_name')
    emial = data.get('email')
    phonnes = data.get('phone', [])
    contact_names = data.get('contact_name', [])
    delivery_addrs = data.get('delivery_address', [])

    if not cnpj_num or not is_valid_cnpj(cnpj_num):
        return jsonify({"error": "CNPJ is required and must be valid"}), 400
    if not bussiness_name or not is_valid_business_name(bussiness_name):
        return jsonify({"error": "Business Name is required and must be valid"}), 400
    if not trade_namee or not is_valid_trade_name(trade_namee):
        return jsonify({"error": "Trade Name is required and must be valid"}), 400
    if not emial or not is_valid_email(emial):
        return jsonify({"error": "Email is required and must be valid"}), 400
    for ph in phonnes:
        if not is_valid_phone(ph):
            return jsonify({"error": "Invalid phone number provided"}), 400
    if not contact_names or not any(is_valid_contact_name(name) for name in contact_names):
        return jsonify({"error": "At least one valid Contact Name is required"}), 400
    if not delivery_addrs or not all(is_valid_address(addr) for addr in delivery_addrs):
        return jsonify({"error": "At least one valid Delivery Address is required"}), 400

    global next_reseller_id
    reseller_id = next_reseller_id
    next_reseller_id += 1

    resellers[reseller_id] = {
        'cnpj': cnpj_num,
        'business_name': bussiness_name,
        'trade_name': trade_namee,
        'email': emial,
        'phone': phonnes,
        'contact_name': contact_names,
        'delivery_address': delivery_addrs
    }

    return jsonify({"reseller_id": reseller_id}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)