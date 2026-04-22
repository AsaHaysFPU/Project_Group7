"""Streamlit UI for Medical Dosage Agentic System"""
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.compute_dosage_tool import compute_dosage
from agents.medical_dosage_agent import MedicalDosageAgent
from rag.rag_pipeline import MedicalRAGPipeline, MEDICAL_KNOWLEDGE_BASE
from memory.persistent_memory import PersistentMemory

# Configure page
st.set_page_config(
    page_title="Medical Dosage Agent | SNAP",
    page_icon="Rx",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
    }
    .error-box {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent' not in st.session_state:
    with st.spinner("Initializing Medical Dosage Agent..."):
        # Initialize RAG
        rag = MedicalRAGPipeline()
        rag.add_documents(MEDICAL_KNOWLEDGE_BASE)
        
        # Initialize memory
        memory = PersistentMemory()
        
        # Initialize agent
        st.session_state.agent = MedicalDosageAgent(rag_pipeline=rag, memory_system=memory)
        st.session_state.rag = rag
        st.session_state.memory = memory

if 'dosage_history' not in st.session_state:
    st.session_state.dosage_history = []

# Sidebar
with st.sidebar:
    st.title("Configuration")
    
    menu_choice = st.radio(
        "Select View",
        ["Agent Dashboard", "Dosage Calculator", "Knowledge Base", "History & Audit", "About"]
    )
    
    st.divider()
    st.subheader("System Status")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Agent Status", "Ready" if st.session_state.agent else "Error")
    with col2:
        stats = st.session_state.memory.get_statistics()
        st.metric("Stored Records", stats['total_dosage_records'])
    
    st.divider()
    if st.button("Refresh System"):
        st.rerun()
    
    if st.button("Clear History"):
        st.session_state.memory.clear_memory()
        st.session_state.dosage_history = []
        st.success("History cleared!")

# Main content
st.markdown("""
<div class="main-header">
    <h1>Medical Dosage Agentic System</h1>
    <p>Safe, evidence-based medication dosing powered by AI</p>
</div>
""", unsafe_allow_html=True)

# TAB 1: Agent Dashboard
if menu_choice == "Agent Dashboard":
    st.header("Agent Dashboard")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Conversations", st.session_state.memory.get_statistics()['total_conversations'])
    with col2:
        st.metric("Dosage Calculations", st.session_state.memory.get_statistics()['total_dosage_records'])
    with col3:
        st.metric("Audit Entries", st.session_state.memory.get_statistics()['total_audit_entries'])
    
    st.divider()
    st.subheader("Agent Interaction")
    
    user_input = st.text_area(
        "Ask the medical dosage agent a question:",
        placeholder="e.g., 'Calculate safe dosage for an 85kg patient on Amoxicillin at 25 mg/kg with max 500mg'",
        height=100
    )
    
    col1, col2 = st.columns([4, 1])
    with col2:
        submit = st.button("Send", type="primary", use_container_width=True)
    
    if submit and user_input:
        with st.spinner("Agent is thinking..."):
            response = st.session_state.agent.process_request(user_input)
        
        if response['success']:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown(f"**Agent Response:**\n\n{response['response']}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.markdown(f"**Error:** {response['error']}")
            st.markdown('</div>', unsafe_allow_html=True)

# TAB 2: Dosage Calculator
elif menu_choice == "Dosage Calculator":
    st.header("Direct Dosage Calculator")
    st.write("Calculate safe medication dosage based on patient weight and drug parameters.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        weight_kg = st.number_input("Patient Weight (kg)", min_value=0.1, max_value=300.0, value=70.0, step=0.1)
    
    with col2:
        drug_dose = st.number_input("Drug Dose (mg/kg)", min_value=0.1, max_value=100.0, value=5.0, step=0.1)
    
    with col3:
        max_dose = st.number_input("Maximum Dose (mg)", min_value=0.1, max_value=5000.0, value=500.0, step=5.0)
    
    calculate_btn = st.button("Calculate Safe Dosage", type="primary", use_container_width=True)
    
    if calculate_btn:
        try:
            result = compute_dosage(weight_kg, drug_dose, max_dose)
            
            # Store in history
            st.session_state.dosage_history.append({
                "timestamp": datetime.now(),
                "weight_kg": weight_kg,
                "drug_mg_per_kg": drug_dose,
                "max_dose_mg": max_dose,
                "result_mg": result['result']
            })
            
            # Store in persistent memory
            st.session_state.memory.add_dosage_record(
                weight_kg, drug_dose, max_dose, result['result'],
                {"source": "calculator_ui"}
            )
            
            # Display result
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                st.markdown(f"### Safe Dosage: **{result['result']:.2f} {result['unit']}**")
                st.markdown(f"\n**Calculation Details:**\n\n{result['detail']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f"**Weight:** {weight_kg} kg\n\n**Drug Dose:** {drug_dose} mg/kg\n\n**Max Dose:** {max_dose} mg")
                st.markdown('</div>', unsafe_allow_html=True)
        
        except ValueError as e:
            st.markdown(f'<div class="error-box">**Error:** {str(e)}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">**Unexpected Error:** {str(e)}</div>', unsafe_allow_html=True)

# TAB 3: Knowledge Base
elif menu_choice == "Knowledge Base":
    st.header("Medical Knowledge Base")
    st.write("Search the integrated medical knowledge base for drug guidelines and dosing information.")
    
    search_query = st.text_input("Search medical knowledge:", placeholder="e.g., acetaminophen, ibuprofen, dosing")
    
    if search_query:
        with st.spinner("Searching knowledge base..."):
            results = st.session_state.rag.retrieve(search_query, k=5)
        
        if results:
            st.success(f"Found {len(results)} relevant documents")
            for i, doc in enumerate(results, 1):
                with st.expander(f"{doc['metadata'].get('title', 'Untitled')} (Relevance: {doc['relevance_score']:.2%})"):
                    st.write(doc['content'])
                    st.caption(f"Source: {doc['metadata'].get('source', 'Unknown')}")
        else:
            st.info("No matching documents found. Try different search terms.")

# TAB 4: History & Audit
elif menu_choice == "History & Audit":
    st.header("History & Audit Logs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dosage Calculation History")
        dosage_hist = st.session_state.memory.get_dosage_history(limit=20)
        if dosage_hist:
            df = pd.DataFrame([
                {
                    "Time": d.get('timestamp', ''),
                    "Weight (kg)": d.get('patient_weight_kg', ''),
                    "Dose (mg/kg)": d.get('drug_mg_per_kg', ''),
                    "Max (mg)": d.get('max_dose_mg', ''),
                    "Result (mg)": d.get('calculated_dose_mg', '')
                }
                for d in dosage_hist
            ])
            st.dataframe(df, use_container_width=True)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button("Download History as CSV", csv, "dosage_history.csv", "text/csv")
        else:
            st.info("No dosage history yet.")
    
    with col2:
        st.subheader("Audit Log")
        audit_log = st.session_state.memory.get_audit_log(limit=20)
        if audit_log:
            df_audit = pd.DataFrame([
                {
                    "Timestamp": a.get('timestamp', ''),
                    "Action": a.get('action', '')
                }
                for a in audit_log
            ])
            st.dataframe(df_audit, use_container_width=True)
        else:
            st.info("No audit entries yet.")

# TAB 5: About
else:  # About
    st.header("About SNAP")
    st.markdown("""
    ### Systems for Niche Agentic Programming
    
    **Medical Dosage Calculation Agent**
    
    This application demonstrates an agentic AI system designed for medical logistics.
    It combines:
    
    - **LLM Orchestration**: Google Gemini for intelligent reasoning
    - **Deterministic Tools**: Safe dosage calculations using pure Python logic
    - **Knowledge Retrieval**: RAG with medical guidelines and drug information
    - **Data Persistence**: Audit-ready memory system for compliance
    - **Interactive UI**: Streamlit dashboard for medical professionals
    
    #### Key Features:

    [*] **Accurate Calculations**: Non-LLM tool ensures mathematical precision
    [*] **Evidence-Based**: RAG integrates current medical guidelines
    [*] **Audit Trail**: Complete history of all calculations and interactions
    [*] **Persistent Memory**: Data survives application restarts
    ✅ **Multi-Modal Interface**: Both agentic requests and direct calculator\n
    
    #### Technology Stack:
    
    - **Framework**: Python + Streamlit
    - **Orchestration**: LangChain + Google Gemini
    - **Vector DB**: ChromaDB for medical knowledge
    - **Memory**: JSON-based persistent storage
    
    #### Student Team:
    - Sutton Wilterdink (compute_dosage_tool.py)
    - [Additional team members]
    
    ---
    
    Developed for COP2080: CS Problem Solving and Solution
    """)
