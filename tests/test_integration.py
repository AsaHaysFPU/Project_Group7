import pytest
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from tools.compute_dosage_tool import compute_dosage
from memory.persistent_memory import PersistentMemory
from rag.rag_pipeline import MedicalRAGPipeline, MEDICAL_KNOWLEDGE_BASE
import tempfile
import json
import os


class TestIntegration:
    """Integration tests for full system workflow"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary directory for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def memory_system(self, temp_data_dir):
        """Initialize memory system with temp directory"""
        return PersistentMemory(temp_data_dir)
    
    @pytest.fixture
    def rag_pipeline(self, temp_data_dir):
        """Initialize RAG pipeline"""
        rag = MedicalRAGPipeline(persist_dir=os.path.join(temp_data_dir, "chroma"))
        rag.add_documents(MEDICAL_KNOWLEDGE_BASE)
        return rag
    
    def test_dosage_calculation_and_storage(self, memory_system):
        """Test compute dosage and verify storage in memory"""
        # Calculate dosage
        result = compute_dosage(70, 5, 500)
        
        # Store in memory
        memory_system.add_dosage_record(
            patient_weight=70,
            drug_mg_per_kg=5,
            max_dose=500,
            calculated_dose=result['result']
        )
        
        # Retrieve from history
        history = memory_system.get_dosage_history()
        assert len(history) > 0
        assert history[-1]['patient_weight_kg'] == 70
        assert history[-1]['calculated_dose_mg'] == 350
    
    def test_rag_knowledge_retrieval(self, rag_pipeline):
        """Test RAG retrieval of medical knowledge"""
        results = rag_pipeline.retrieve("acetaminophen dosing")
        assert len(results) > 0
        assert all('content' in r for r in results)
        assert all('metadata' in r for r in results)
    
    def test_conversation_persistence(self, memory_system):
        """Test conversation storage and retrieval"""
        # Add conversations
        memory_system.add_conversation(
            user_message="What is the dosage?",
            assistant_response="The safe dosage is 350mg.",
            metadata={"patient_id": "P001"}
        )
        
        memory_system.add_conversation(
            user_message="Any contraindications?",
            assistant_response="No known contraindications for this patient.",
            metadata={"patient_id": "P001"}
        )
        
        # Retrieve
        history = memory_system.get_conversation_history()
        assert len(history) >= 2
        assert history[-1]['user_message'] == "Any contraindications?"
    
    def test_audit_log_compliance(self, memory_system):
        """Test audit logging for compliance"""
        # Generate audit trail
        memory_system.audit_log_entry("system_start", {"timestamp": "2026-04-21"})
        memory_system.add_dosage_record(75, 5, 500, 375)
        memory_system.audit_log_entry("system_stop", {"duration": "5min"})
        
        # Verify audit log
        audit = memory_system.get_audit_log()
        assert len(audit) >= 3
        actions = [a['action'] for a in audit]
        assert "system_start" in actions
        assert "dosage_calculated" in actions
        assert "system_stop" in actions
    
    def test_search_conversation_history(self, memory_system):
        """Test searching conversation history"""
        # Add conversations with different topics
        memory_system.add_conversation("dosage for acetaminophen", "Calculate based on weight")
        memory_system.add_conversation("patient allergies", "No known allergies")
        memory_system.add_conversation("dosage for ibuprofen", "Calculate based on age")
        
        # Search
        results = memory_system.search_conversations("dosage")
        assert len(results) == 2
        
        results = memory_system.search_conversations("allergies")
        assert len(results) == 1
    
    def test_memory_statistics(self, memory_system):
        """Test memory statistics"""
        # Add some data
        for i in range(5):
            memory_system.add_conversation(f"Q{i}", f"A{i}")
            memory_system.add_dosage_record(50 + i, 5, 500, 300)
        
        stats = memory_system.get_statistics()
        assert stats['total_conversations'] == 5
        assert stats['total_dosage_records'] == 5
        assert stats['oldest_data'] is not None
    
    def test_full_workflow(self, memory_system, rag_pipeline):
        """Test complete workflow: input -> calculation -> storage -> retrieval"""
        # User asks for dosage
        patient_weight = 80
        drug_dose = 5
        max_dose = 500
        
        # Step 1: Search knowledge base
        kb_results = rag_pipeline.retrieve("amoxicillin pediatric dosing")
        assert len(kb_results) > 0
        
        # Step 2: Calculate dosage
        dosage_result = compute_dosage(patient_weight, drug_dose, max_dose)
        assert dosage_result['result'] == 400  # min(80*5, 500) = 400
        
        # Step 3: Store everything
        memory_system.add_dosage_record(
            patient_weight=patient_weight,
            drug_mg_per_kg=drug_dose,
            max_dose=max_dose,
            calculated_dose=dosage_result['result'],
            metadata={"knowledge_consulted": len(kb_results)}
        )
        
        memory_system.add_conversation(
            user_message=f"Calculate dosage for {patient_weight}kg patient",
            assistant_response=f"Safe dosage: {dosage_result['result']}mg",
            metadata={"drug": "amoxicillin"}
        )
        
        # Step 4: Verify in memory
        dosage_hist = memory_system.get_dosage_history()
        conv_hist = memory_system.get_conversation_history()
        
        assert dosage_hist[-1]['patient_weight_kg'] == patient_weight
        assert dosage_hist[-1]['calculated_dose_mg'] == dosage_result['result']
        assert conv_hist[-1]['metadata']['drug'] == "amoxicillin"


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_rag_query(self):
        """Test RAG with empty query"""
        rag = MedicalRAGPipeline()
        results = rag.retrieve("", k=1)
        assert isinstance(results, list)
    
    def test_memory_file_corruption_recovery(self):
        """Test memory system recovery from corrupted file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = PersistentMemory(tmpdir)
            
            # Create corrupted file
            bad_file = os.path.join(tmpdir, "conversations.json")
            with open(bad_file, 'w') as f:
                f.write("{ invalid json }")
            
            # Should recover gracefully
            memory._load_json(bad_file, [])
            assert True  # No exception raised
    
    def test_concurrent_dosage_calculations(self):
        """Test concurrent dosage calculations"""
        import threading
        results = []
        
        def calc_dosage(weight):
            result = compute_dosage(weight, 5, 500)
            results.append(result)
        
        threads = []
        for weight in range(50, 150, 10):
            t = threading.Thread(target=calc_dosage, args=(weight,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(results) == 10
        for r in results:
            assert 'result' in r


class TestPerformance:
    """Performance and load tests"""
    
    def test_memory_persistence_performance(self):
        """Test memory persistence doesn't slow down operations"""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = PersistentMemory(tmpdir)
            
            start = time.time()
            for i in range(100):
                memory.add_dosage_record(70, 5, 500, 350)
            elapsed = time.time() - start
            
            avg_time_ms = (elapsed / 100) * 1000
            # Should be reasonably fast (< 50ms per operation)
            assert avg_time_ms < 50, f"Too slow: {avg_time_ms}ms per operation"
    
    def test_rag_retrieval_performance(self):
        """Test RAG retrieval speed"""
        rag = MedicalRAGPipeline()
        rag.add_documents(MEDICAL_KNOWLEDGE_BASE)
        
        start = time.time()
        for _ in range(20):
            rag.retrieve("dosage guidelines", k=3)
        elapsed = time.time() - start
        
        avg_time_ms = (elapsed / 20) * 1000
        # RAG should complete in reasonable time
        assert avg_time_ms < 500, f"RAG too slow: {avg_time_ms}ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
