from flask import Flask, request, jsonify
import requests
from datetime import datetime
import base64
import os

app = Flask(__name__)

# Daraja API credentials. Ensure to place in .env file
CONSUMER_KEY = 'TLvW5Qv0tzAcOAz42yLIh4X6uA7Wyp8E0PBaPaiQMQjcW4AY'
CONSUMER_SECRET = 'sT1BfqnM8XwVJwxvxjMbXzOADqoE8F9xf439HvXV3xYCmOAqtivkZDhiBfzomfds'
BUSINESS_SHORTCODE = '174379'
PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
CALLBACK_URL = 'https://your-callback-url.com/callback'
#--------------Ensure to place in .env file----------------------#
# Function to get the access token
def get_access_token():
    auth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(auth_url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    response_json = response.json()
    return response_json['access_token']

# Function to generate the password
def generate_password():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = BUSINESS_SHORTCODE + PASSKEY + timestamp
    password = base64.b64encode(data_to_encode.encode()).decode('utf-8')
    return password, timestamp

# Endpoint
@app.route('/payment', methods=['POST'])
def payment():
    data = request.json
    phone_number = data.get('phone')
    amount = data.get('amount')
    
    if not phone_number or not amount:
        return jsonify({'error': 'Phone number and amount are required'}), 400

    access_token = get_access_token()
    password, timestamp = generate_password()

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'BusinessShortCode': BUSINESS_SHORTCODE,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': amount,
        'PartyA': phone_number,
        'PartyB': BUSINESS_SHORTCODE,
        'PhoneNumber': phone_number,
        'CallBackURL': CALLBACK_URL,
        'AccountReference': 'IanGtheDev',
        'TransactionDesc': 'Payment for order'
    }

    stk_push_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

    response = requests.post(stk_push_url, json=payload, headers=headers)
    response_json = response.json()

    # response
    if response.status_code == 200:
        return jsonify({
            'message': 'STK push sent successfully',
            'response': response_json
        }), 200
    else:
        return jsonify({
            'error': 'Failed to send STK push',
            'details': response_json
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
