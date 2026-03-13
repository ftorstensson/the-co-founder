import os
from google.cloud import firestore

class REGISTRY:
    _data = {}

    @classmethod
    def sync(cls):
        try:
            db = firestore.Client(project=os.environ.get("GCP_PROJECT", "vibe-agent-final"))
            doc = db.collection("_system_config").document("naming_registry").get()
            if not doc.exists: raise ValueError("Lion’s Mouth is Silent (Doc missing)")
            cls._data = doc.to_dict()
            # Dynamic Attribute Assignment
            for k, v in cls._data.items(): setattr(cls, k, v)
            print(f"💎 Registry Synced: {list(cls._data.keys())}")
        except Exception as e:
            print(f"❌ CRITICAL REGISTRY FAILURE: {e}")
            raise e

# Immediate Boot-Sync
REGISTRY.sync()
