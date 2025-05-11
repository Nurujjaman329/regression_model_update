import json
import random
from datetime import datetime

import requests

from model import FraudDetectionModel

# Initialize model
model = FraudDetectionModel()

# Load or generate test data
def generate_test_order():
    products = ['clothing', 'cosmetics', 'electronics', 'groceries']
    days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    prefixes = ['013', '015', '016', '017', '018', '019']
    
    return {
        "order_value": random.randint(500, 20000),
        "cart_item_count": random.randint(1, 15),
        "product_category": random.choice(products),
        "order_day": random.choice(days),
        "order_hour": random.randint(0, 23),
        "customer_phone_prefix": random.choice(prefixes),
        "coupon_used": random.random() > 0.7,
        "address": random.choice([d['en'] for d in BANGLADESH_DISTRICTS]) if random.random() > 0.3 else ""
    }

def test_local_prediction():
    print("\nTesting Local Prediction:")
    test_order = generate_test_order()
    print("\nTest Order Data:")
    print(json.dumps(test_order, indent=2))
    
    prediction = model.predict(test_order)
    print("\nPrediction Results:")
    print(f"Cancellation Probability: {prediction['cancellation_probability']:.2f}")
    print(f"Fraud Probability: {prediction['fraud_probability']:.2f}")
    print(f"Likely Cancelled: {'Yes' if prediction['likely_cancelled'] else 'No'}")
    print(f"Likely Fraud: {'Yes' if prediction['likely_fraud'] else 'No'}")

def test_api_integration():
    print("\nTesting API Integration:")
    test_order = generate_test_order()
    print("\nTest Order Data (with IP/UA simulation):")
    test_order['ip'] = f"203.0.113.{random.randint(1, 255)}"
    test_order['user_agent'] = random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    ])
    print(json.dumps(test_order, indent=2))
    
    prediction = model.predict_from_api(test_order)
    print("\nPrediction Results with ASN/Device Data:")
    print(f"Cancellation Probability: {prediction['cancellation_probability']:.2f}")
    print(f"Fraud Probability: {prediction['fraud_probability']:.2f}")
    print(f"Likely Cancelled: {'Yes' if prediction['likely_cancelled'] else 'No'}")
    print(f"Likely Fraud: {'Yes' if prediction['likely_fraud'] else 'No'}")

if __name__ == "__main__":
    # First train the model
    print("Training model...")
    model.train()
    
    # Then run tests
    test_local_prediction()
    test_api_integration()
