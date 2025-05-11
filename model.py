import json

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


class FraudDetectionModel:
    def __init__(self):
        self.scaler = StandardScaler()
        self.cancellation_model = LogisticRegression()
        self.fraud_model = LogisticRegression()
        self.feature_columns = []
        self.is_fitted = False
        self.metadata = {
            "max_order_value": 20000,
            "max_cart_items": 20,
            "phone_prefixes": ["013", "015", "016", "017", "018", "019"],
            "browsers": ["Chrome", "Opera", "Firefox", "Safari", "Edge"],
            "os_list": ["Windows", "Android", "iOS", "Mac OS X"],
            "devices": ["phone", "desktop", "tablet"],
            "districts": [d["en"] for d in BANGLADESH_DISTRICTS]  # From your app
        }
        
    def preprocess_data(self, data):
        """Convert raw JSON data into standardized features"""
        processed = []
        
        for order in data['orders']:
            features = {}
            
            # Standardize continuous variables (0-1)
            features['order_value'] = min(order.get('order_value', 0), self.metadata['max_order_value'])
            features['order_value'] = min(order.get('order_value', 0), self.metadata['max_order_value'])
            features['cart_item_count'] = min(order.get('cart_item_count', 0), self.metadata['max_cart_items'])

        
            features['cart_item_count'] = min(order.get('cart_item_count', 0), self.metadata['max_cart_items'])
            features['cart_item_count'] = features['cart_item_count'][0] / features['cart_item_count'][1]
            
            # Product categories
            product_cat = order.get('product_category', '').lower()
            for cat in ['clothing', 'cosmetics', 'electronics', 'groceries']:
                features[f'is_product_{cat}'] = 1 if product_cat == cat else 0
                
            # Time features
            features['is_sunday'] = 1 if order.get('order_day', '').lower() == 'sunday' else 0
            order_hour = order.get('order_hour', 0)
            features['is_h00'] = 1 if order_hour == 0 else 0
            
            # Customer info
            phone_prefix = str(order.get('customer_phone_prefix', ''))
            for prefix in self.metadata['phone_prefixes']:
                features[f'is_{prefix}'] = 1 if phone_prefix == prefix else 0
                
            # ASN features
            asn = order.get('asn', {}).get('asn', '')
            features['asn_known'] = 1 if asn and asn.startswith('AS') else 0
            features['asn_bd'] = 1 if order.get('is_bangladesh', False) else 0
            
            # Browser, OS, Device
            browser = (order.get('browser') or '').lower()
            for br in self.metadata['browsers']:
                features[f'is_browser_{br.lower()}'] = 1 if browser == br.lower() else 0
                
            os = (order.get('os') or '').lower()
            for operating_system in self.metadata['os_list']:
                features[f'is_os_{operating_system.lower()}'] = 1 if os == operating_system.lower() else 0
                
            device_type = (order.get('device_type') or '').lower()
            for dev in self.metadata['devices']:
                features[f'is_device_{dev.lower()}'] = 1 if device_type == dev.lower() else 0
                
            # Location
            district = (order.get('district') or '').lower()
            for dist in self.metadata['districts']:
                features[f'is_district_{dist.lower()}'] = 1 if district == dist.lower() else 0
                
            # Misc
            features['is_coupon_used'] = 1 if order.get('coupon_used', False) else 0
            
            # Labels
            features['was_cancelled'] = 1 if order.get('was_cancelled', False) else 0
            features['is_fraud'] = 1 if order.get('is_fraud', False) else 0
            
            processed.append(features)
            
        return pd.DataFrame(processed)
    
    def train(self, data_path='test_data.json'):
        """Train models using data from JSON file"""
        with open(data_path) as f:
            data = json.load(f)
            
        df = self.preprocess_data(data)
        self.feature_columns = [col for col in df.columns if col not in ['was_cancelled', 'is_fraud']]
        
        X = df[self.feature_columns]
        y_cancel = df['was_cancelled']
        y_fraud = df['is_fraud']
        
        X_scaled = self.scaler.fit_transform(X)
        
        if len(df) > 50:
            X_train, X_test, y_cancel_train, y_cancel_test, y_fraud_train, y_fraud_test = train_test_split(
                X_scaled, y_cancel, y_fraud, test_size=0.2, random_state=42)
        else:
            X_train, y_cancel_train, y_fraud_train = X_scaled, y_cancel, y_fraud
            X_test, y_cancel_test, y_fraud_test = None, None, None
        
        self.cancellation_model.fit(X_train, y_cancel_train)
        self.fraud_model.fit(X_train, y_fraud_train)
        self.is_fitted = True
        
        if X_test is not None:
            print("Model Evaluation Results:")
            self.evaluate(X_test, y_cancel_test, y_fraud_test)
    
    def evaluate(self, X_test, y_cancel_test, y_fraud_test):
        cancel_pred = self.cancellation_model.predict(X_test)
        print("\nCancellation Model:")
        print(classification_report(y_cancel_test, cancel_pred))
        
        fraud_pred = self.fraud_model.predict(X_test)
        print("\nFraud Detection Model:")
        print(classification_report(y_fraud_test, fraud_pred))
    
    def predict_from_api(self, order_data, api_url='http://localhost:5000/order'):
        """Enrich order data with ASN/device info from your API"""
        import requests

        # Call your existing API to get ASN/device info
        try:
            response = requests.post(api_url, json=order_data)
            api_data = response.json()
            
            # Merge the data
            enriched_data = {
                **order_data,
                'asn': api_data.get('asn', {}),
                'browser': api_data.get('device_info', {}).get('browser', ''),
                'os': api_data.get('device_info', {}).get('os', ''),
                'device_type': self._determine_device_type(api_data.get('device_info', {})),
                'district': api_data.get('district_detected', ''),
                'is_bangladesh': self._is_bangladesh_asn(api_data.get('asn', {}).get('org', ''))
            }
            return self.predict(enriched_data)
        except Exception as e:
            print(f"API Error: {e}")
            return self.predict(order_data)  # Fallback to basic prediction
    
    def _determine_device_type(self, device_info):
        if device_info.get('is_mobile'):
            return 'phone'
        elif device_info.get('is_tablet'):
            return 'tablet'
        elif device_info.get('is_pc'):
            return 'desktop'
        return 'unknown'
    
    def _is_bangladesh_asn(self, asn_org):
        return 'Bangladesh' in asn_org or 'BD' in asn_org
    
    def predict(self, order_data):
        if not self.is_fitted:
            self.train()
            
        input_data = {"orders": [order_data], "metadata": self.metadata}
        df = self.preprocess_data(input_data)
        X = df[self.feature_columns]
        X_scaled = self.scaler.transform(X)
        
        cancel_prob = self.cancellation_model.predict_proba(X_scaled)[0][1]
        fraud_prob = self.fraud_model.predict_proba(X_scaled)[0][1]
        
        return {
            'cancellation_probability': float(cancel_prob),
            'fraud_probability': float(fraud_prob),
            'likely_cancelled': cancel_prob > 0.5,
            'likely_fraud': fraud_prob > 0.5
        }

# Bangladesh districts from your app
BANGLADESH_DISTRICTS = [
    {"en": "Bagerhat", "bn": "বাগেরহাট"},
    {"en": "Bandarban", "bn": "বান্দরবান"},
    {"en": "Barguna", "bn": "বরগুনা"},
    {"en": "Barisal", "bn": "বরিশাল"},
    {"en": "Bhola", "bn": "ভোলা"},
    {"en": "Bogra", "bn": "বগুড়া"},
    {"en": "Brahmanbaria", "bn": "ব্রাহ্মণবাড়িয়া"},
    {"en": "Chandpur", "bn": "চাঁদপুর"},
    {"en": "Chapai Nawabganj", "bn": "চাঁপাইনবাবগঞ্জ"},
    {"en": "Chattogram", "bn": "চট্টগ্রাম"},
    {"en": "Chuadanga", "bn": "চুয়াডাঙ্গা"},
    {"en": "Comilla", "bn": "কুমিল্লা"},
    {"en": "Cox's Bazar", "bn": "কক্সবাজার"},
    {"en": "Dhaka", "bn": "ঢাকা"},
    {"en": "Dinajpur", "bn": "দিনাজপুর"},
    {"en": "Faridpur", "bn": "ফরিদপুর"},
    {"en": "Feni", "bn": "ফেনী"},
    {"en": "Gaibandha", "bn": "গাইবান্ধা"},
    {"en": "Gazipur", "bn": "গাজীপুর"},
    {"en": "Gopalganj", "bn": "গোপালগঞ্জ"},
    {"en": "Habiganj", "bn": "হবিগঞ্জ"},
    {"en": "Jamalpur", "bn": "জামালপুর"},
    {"en": "Jashore", "bn": "যশোর"},
    {"en": "Jhalokathi", "bn": "ঝালকাঠি"},
    {"en": "Jhenaidah", "bn": "ঝিনাইদহ"},
    {"en": "Joypurhat", "bn": "জয়পুরহাট"},
    {"en": "Khagrachhari", "bn": "খাগড়াছড়ি"},
    {"en": "Khulna", "bn": "খুলনা"},
    {"en": "Kishoreganj", "bn": "কিশোরগঞ্জ"},
    {"en": "Kurigram", "bn": "কুড়িগ্রাম"},
    {"en": "Kushtia", "bn": "কুষ্টিয়া"},
    {"en": "Lakshmipur", "bn": "লক্ষ্মীপুর"},
    {"en": "Lalmonirhat", "bn": "লালমনিরহাট"},
    {"en": "Madaripur", "bn": "মাদারীপুর"},
    {"en": "Magura", "bn": "মাগুরা"},
    {"en": "Manikganj", "bn": "মানিকগঞ্জ"},
    {"en": "Meherpur", "bn": "মেহেরপুর"},
    {"en": "Moulvibazar", "bn": "মৌলভীবাজার"},
    {"en": "Munshiganj", "bn": "মুন্সীগঞ্জ"},
    {"en": "Mymensingh", "bn": "ময়মনসিংহ"},
    {"en": "Naogaon", "bn": "নওগাঁ"},
    {"en": "Narail", "bn": "নড়াইল"},
    {"en": "Narayanganj", "bn": "নারায়ণগঞ্জ"},
    {"en": "Narsingdi", "bn": "নরসিংদী"},
    {"en": "Natore", "bn": "নাটোর"},
    {"en": "Netrokona", "bn": "নেত্রকোনা"},
    {"en": "Nilphamari", "bn": "নীলফামারী"},
    {"en": "Noakhali", "bn": "নোয়াখালী"},
    {"en": "Pabna", "bn": "পাবনা"},
    {"en": "Panchagarh", "bn": "পঞ্চগড়"},
    {"en": "Patuakhali", "bn": "পটুয়াখালী"},
    {"en": "Pirojpur", "bn": "পিরোজপুর"},
    {"en": "Rajbari", "bn": "রাজবাড়ী"},
    {"en": "Rajshahi", "bn": "রাজশাহী"},
    {"en": "Rangamati", "bn": "রাঙ্গামাটি"},
    {"en": "Rangpur", "bn": "রংপুর"},
    {"en": "Satkhira", "bn": "সাতক্ষীরা"},
    {"en": "Shariatpur", "bn": "শরীয়তপুর"},
    {"en": "Sherpur", "bn": "শেরপুর"},
    {"en": "Sirajganj", "bn": "সিরাজগঞ্জ"},
    {"en": "Sunamganj", "bn": "সুনামগঞ্জ"},
    {"en": "Sylhet", "bn": "সিলেট"},
    {"en": "Tangail", "bn": "টাঙ্গাইল"},
    {"en": "Thakurgaon", "bn": "ঠাকুরগাঁও"}
]
