import logging
import firebase_admin
from firebase_admin import credentials, firestore
from src.config import settings

log = logging.getLogger(__name__)

def initialize_firebase():
    """
    Initializes the Firebase Admin SDK once.
    """
    try:
        # Check if Firebase is already initialized to avoid hot-reload errors
        if not firebase_admin._apps:
            cred_path = settings.GOOGLE_APPLICATION_CREDENTIALS
            
            if not str(cred_path).endswith(".json"):
                log.warning(f"Credentials path does not look like a JSON file: {cred_path}")

            log.info(f"Attempting Firebase connection with: {cred_path}")
            
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            log.info("✅ Firebase Admin SDK initialized successfully.")
        else:
            log.info("Firebase is already initialized.")

    except Exception as e:
        log.error(f"❌ Critical failure initializing Firebase: {e}")
        # In production, we might want to raise this to stop the server
        raise e

def get_db():
    """
    Returns the Firestore client.
    Use this in services to interact with the DB.
    """
    return firestore.client()