import os
import requests
import json
import firebase_admin
from firebase_admin import credentials, db

# Firebase configuration using your app config
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyD7Hn3802C2S2TWchEJkUcJvCh_QxRWobs",
    "authDomain": "myexpenses-6e185.firebaseapp.com",
    "databaseURL": "https://myexpenses-6e185-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "myexpenses-6e185",
    "storageBucket": "myexpenses-6e185.firebasestorage.app",
    "messagingSenderId": "976505529382",
    "appId": "1:976505529382:web:8595b4ed5a588c334932e7"
}

# Firebase REST API Database class
class FirebaseRESTDatabase:
    """Firebase Realtime Database using REST API - no auth required for public databases"""
    
    def __init__(self, base_url, path=""):
        self.base_url = base_url.rstrip('/')
        self.path = path.strip('/')
    
    def child(self, path):
        new_path = f"{self.path}/{path}" if self.path else path
        return FirebaseRESTDatabase(self.base_url, new_path)
    
    def get(self):
        try:
            url = f"{self.base_url}/{self.path}.json" if self.path else f"{self.base_url}/.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return FirebaseSnapshot(data)
        except Exception as e:
            print(f"Firebase GET error: {e}")
            return FirebaseSnapshot(None)
    
    def set(self, data):
        try:
            url = f"{self.base_url}/{self.path}.json" if self.path else f"{self.base_url}/.json"
            response = requests.put(url, json=data, timeout=10)
            response.raise_for_status()
            print(f"Firebase SET success at {self.path}")
            return True
        except Exception as e:
            print(f"Firebase SET error at {self.path}: {e}")
            return False
    
    def delete(self):
        try:
            url = f"{self.base_url}/{self.path}.json" if self.path else f"{self.base_url}/.json"
            response = requests.delete(url, timeout=10)
            response.raise_for_status()
            print(f"Firebase DELETE success at {self.path}")
            return True
        except Exception as e:
            print(f"Firebase DELETE error at {self.path}: {e}")
            return False

class FirebaseSnapshot:
    def __init__(self, data):
        self._data = data
    
    def val(self):
        return self._data

# Initialize Firebase connection
def initialize_firebase():
    """Initialize Firebase connection"""
    try:
        # Try Firebase Admin SDK first (for service account)
        service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH', 'serviceAccountKey.json')
        
        if os.path.exists(service_account_path):
            try:
                firebase_admin.get_app()
                return True
            except ValueError:
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': FIREBASE_CONFIG['databaseURL']
                })
                print("✅ Firebase initialized with service account credentials")
                return True
        else:
            # Use REST API for public database access
            print("🔄 Using Firebase REST API (no auth required)")
            print("📊 Testing Firebase connection...")
            
            # Test connection
            test_db = FirebaseRESTDatabase(FIREBASE_CONFIG['databaseURL'])
            test_result = test_db.child('test').get()
            
            if test_result is not None:
                print("✅ Firebase REST API connection successful!")
                return True
            else:
                print("❌ Firebase connection failed")
                return False
                
    except Exception as e:
        print(f"Firebase initialization error: {e}")
        return False

# Initialize Firebase when module is imported
firebase_initialized = initialize_firebase()

# Admin database reference
def get_admin_db():
    """Get Firebase Admin database reference"""
    try:
        if firebase_initialized:
            return db.reference()
        else:
            print("Firebase not initialized")
            return None
    except Exception as e:
        print(f"Error getting database reference: {e}")
        return None

# For backwards compatibility, create a mock database object
class MockDatabase:
    """Mock database for when Firebase is not available"""
    _data = {}  # In-memory storage for development
    
    def __init__(self, path=""):
        self.path = path
    
    def child(self, path):
        new_path = f"{self.path}/{path}" if self.path else path
        return MockDatabase(new_path)
    
    def get(self):
        data = self._get_data_at_path(self.path)
        return MockSnapshot(data)
    
    def set(self, data):
        print(f"Mock set at {self.path}: {data}")
        self._set_data_at_path(self.path, data)
        return True
    
    def delete(self):
        print(f"Mock delete at {self.path}")
        self._delete_data_at_path(self.path)
        return True
    
    def _get_data_at_path(self, path):
        if not path:
            return MockDatabase._data
        
        keys = path.split('/')
        current = MockDatabase._data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _set_data_at_path(self, path, data):
        if not path:
            MockDatabase._data = data
            return
        
        keys = path.split('/')
        current = MockDatabase._data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = data
    
    def _delete_data_at_path(self, path):
        if not path:
            MockDatabase._data.clear()
            return
        
        keys = path.split('/')
        current = MockDatabase._data
        
        for key in keys[:-1]:
            if key in current:
                current = current[key]
            else:
                return  # Path doesn't exist
        
        if keys[-1] in current:
            del current[keys[-1]]

class MockSnapshot:
    def __init__(self, data):
        self._data = data
    
    def val(self):
        return self._data

# Create database instance
def get_database():
    """Get database reference, falling back to mock if Firebase not available"""
    if firebase_initialized:
        try:
            # Try Admin SDK first
            return db.reference()
        except Exception as admin_error:
            try:
                # Fall back to REST API
                print(f"Admin SDK failed ({admin_error}), using REST API")
                return FirebaseRESTDatabase(FIREBASE_CONFIG['databaseURL'])
            except Exception as rest_error:
                print(f"REST API also failed ({rest_error}), using mock database")
                return MockDatabase()
    else:
        print("Firebase not initialized, using mock database for development")
        return MockDatabase()

# Create database instance
database = get_database()
