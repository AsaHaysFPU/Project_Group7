"""Memory persistence system for data that survives application restarts"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class PersistentMemory:
    """
    Persistent memory system that survives application restarts.
    Stores conversation history, dosage calculations, and audit logs.
    """
    
    def __init__(self, data_dir: str = "data/memory"):
        """
        Initialize persistent memory.
        
        Args:
            data_dir: Directory to store persistent data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.conversation_file = os.path.join(data_dir, "conversations.json")
        self.dosage_history_file = os.path.join(data_dir, "dosage_history.json")
        self.audit_log_file = os.path.join(data_dir, "audit_log.json")
        
        self._load_all()
    
    def _load_all(self):
        """Load all persistent data from disk"""
        self.conversations = self._load_json(self.conversation_file, [])
        self.dosage_history = self._load_json(self.dosage_history_file, [])
        self.audit_log = self._load_json(self.audit_log_file, [])
        logger.info(f"Loaded {len(self.conversations)} conversations from memory")
    
    def _load_json(self, filepath: str, default: Any = None) -> Any:
        """Load JSON file or return default"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
        return default if default is not None else {}
    
    def _save_json(self, filepath: str, data: Any):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving to {filepath}: {e}")
    
    def add_conversation(self, user_message: str, assistant_response: str, metadata: Dict = None):
        """
        Add a conversation exchange to memory.
        
        Args:
            user_message: User input
            assistant_response: Agent response
            metadata: Additional context (e.g., patient ID, drug name)
        """
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "assistant_response": assistant_response,
            "metadata": metadata or {}
        }
        self.conversations.append(conversation)
        self._save_json(self.conversation_file, self.conversations)
        self.audit_log_entry("conversation_added", conversation)
    
    def add_dosage_record(self, patient_weight: float, drug_mg_per_kg: float, 
                         max_dose: float, calculated_dose: float, metadata: Dict = None):
        """
        Record a dosage calculation in persistent memory.
        
        Args:
            patient_weight: Patient weight in kg
            drug_mg_per_kg: Drug dose per kg
            max_dose: Maximum allowed dose
            calculated_dose: Calculated safe dose
            metadata: Additional context
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "patient_weight_kg": patient_weight,
            "drug_mg_per_kg": drug_mg_per_kg,
            "max_dose_mg": max_dose,
            "calculated_dose_mg": calculated_dose,
            "metadata": metadata or {}
        }
        self.dosage_history.append(record)
        self._save_json(self.dosage_history_file, self.dosage_history)
        self.audit_log_entry("dosage_calculated", record)
    
    def audit_log_entry(self, action: str, data: Dict = None):
        """
        Record an audit log entry for compliance.
        
        Args:
            action: Type of action (e.g., "dosage_calculated", "conversation_added")
            data: Associated data
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "data": data or {}
        }
        self.audit_log.append(entry)
        self._save_json(self.audit_log_file, self.audit_log)
    
    def get_conversation_history(self, limit: int = 50) -> List[Dict]:
        """Retrieve conversation history"""
        return self.conversations[-limit:]
    
    def get_dosage_history(self, limit: int = 50) -> List[Dict]:
        """Retrieve dosage calculation history"""
        return self.dosage_history[-limit:]
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Retrieve audit log"""
        return self.audit_log[-limit:]
    
    def search_conversations(self, query: str) -> List[Dict]:
        """Search conversations by keyword"""
        results = []
        query_lower = query.lower()
        for conv in self.conversations:
            if (query_lower in conv.get("user_message", "").lower() or 
                query_lower in conv.get("assistant_response", "").lower()):
                results.append(conv)
        return results
    
    def clear_memory(self):
        """Clear all persisted data"""
        self.conversations = []
        self.dosage_history = []
        self.audit_log = []
        self._save_json(self.conversation_file, [])
        self._save_json(self.dosage_history_file, [])
        self._save_json(self.audit_log_file, [])
        logger.info("All memory cleared")
    
    def get_statistics(self) -> Dict:
        """Get statistics about stored data"""
        return {
            "total_conversations": len(self.conversations),
            "total_dosage_records": len(self.dosage_history),
            "total_audit_entries": len(self.audit_log),
            "oldest_data": self.conversations[0]["timestamp"] if self.conversations else None,
            "newest_data": self.conversations[-1]["timestamp"] if self.conversations else None
        }
