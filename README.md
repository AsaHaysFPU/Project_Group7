# Medical Dosage Agentic System - SNAP

**Systems for Niche Agentic Programming**

An AI-powered system for safe, evidence-based medical dosage calculations. This project shows how large language models can work alongside deterministic Python logic, knowledge retrieval, and persistent memory to support practical healthcare workflows.

## Project Overview

### The Problem
Medical professionals need to calculate doses safely while accounting for patient characteristics, drug-specific guidance, and maximum dose limits. Even small mistakes can have serious consequences.

### The Solution
SNAP brings together:
- **Gemini LLM** for intelligent reasoning and patient interaction
- **Deterministic Python Tool** (compute_dosage) for mathematically precise dose calculations
- **RAG System** with medical guidelines and drug information
- **Persistent Memory** for audit trails and compliance
- **Interactive Streamlit UI** for medical professionals

### Key Features
- Non-LLM tool for mathematically reliable dosage calculations
- RAG integration with FDA and clinical guidance
- Full audit trail support for compliance workflows
- Persistent memory across app restarts
- Multi-modal interface (agentic chat + direct calculator)
- Deployment-ready for common cloud platforms

## Project Structure

```
Final-Project/
├── src/
│   ├── __init__.py
│   ├── tools/
│   │   ├── __init__.py
│   │   └── compute_dosage_tool.py          # Non-LLM deterministic tool
│   ├── agents/
│   │   ├── __init__.py
│   │   └── medical_dosage_agent.py         # LangChain ReAct agent
│   ├── rag/
│   │   ├── __init__.py
│   │   └── rag_pipeline.py                 # ChromaDB RAG system
│   ├── memory/
│   │   ├── __init__.py
│   │   └── persistent_memory.py            # Data persistence system
│   └── ui/
│       └── app.py                          # Streamlit interface
├── tests/
│   ├── test_compute_dosage_tool.py        # Unit tests + load testing
│   └── test_integration.py                 # Integration tests
├── data/                                    # Data directory (created at runtime)
│   ├── chroma_db/                          # Vector database
│   └── memory/                             # Persistent storage
├── requirements.txt                        # Python dependencies
├── pyproject.toml                          # Project configuration
├── .env.example                            # Environment template
└── README.md                               # This file
```

## Quick Start

### Prerequisites
- Python 3.9+
- Google Generative AI API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HayatoR28/Final-Project.git
   cd Final-Project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Add your GOOGLE_API_KEY to .env
   ```

5. **Run tests**
   ```bash
   pytest tests/ -v
   ```

6. **Launch the application**
   ```bash
   streamlit run src/ui/app.py
   ```

The application will be available at `http://localhost:8501`

## Using the Application

### 1. Agent Dashboard
Ask the medical dosage agent questions in plain language:
- "Calculate safe dosage for an 85kg patient on Amoxicillin at 25 mg/kg with max 500mg"
- "What are the dosing guidelines for acetaminophen?"
- "I have a 15kg child, what's the safe ibuprofen dose?"

Behind the scenes, the agent uses:
- **Compute Dosage Tool**: For precise calculations
- **Knowledge Base**: For drug guidelines and safety info
- **Gemini LLM**: For reasoning and patient context

### 2. Direct Dosage Calculator
Enter patient weight, dose per kg, and maximum dose to get a safe dosage result right away.

### 3. Knowledge Base Search
Search medical guidance for drug information, interaction warnings, and dosing protocols.

### 4. History & Audit
Review past calculations and interactions, then export CSV records when needed.

## Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Unit Tests
```bash
pytest tests/test_compute_dosage_tool.py -v
```

### Load Testing (1000+ concurrent requests)
```bash
pytest tests/test_compute_dosage_tool.py::test_load_1000_requests -v -s
```

### Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html
```

## Architecture

### Core Components

#### 1. Deterministic Tool (`compute_dosage_tool.py`)
**Non-LLM Python function** for mathematical accuracy:
```python
def compute_dosage(weight_kg, drug_mg_per_kg, max_dose_mg) -> dict:
    # Input validation (type & range checking)
    # Calculation: min(weight * dose_per_kg, max_dose)
    # Returns: safe dose in mg with detailed explanation
```

#### 2. RAG Pipeline (`rag_pipeline.py`)
Retrieval-Augmented Generation with ChromaDB:
- Embeds medical documents with Google's embedding model
- Stores in vector database for similarity search
- Returns relevant drug guidelines for agent context

#### 3. LangChain Agent (`medical_dosage_agent.py`)
ReAct agent orchestrates:
- User input processing
- Tool selection (compute_dosage, search_medical_knowledge)
- LLM reasoning with Gemini
- Response synthesis

#### 4. Persistent Memory (`persistent_memory.py`)
Audit-ready storage:
- Conversation history
- Dosage calculation records
- Audit log for compliance
- Survives app restarts (JSON-based)

#### 5. Streamlit UI (`app.py`)
Interactive dashboard with:
- Agent chat interface
- Direct calculator
- Knowledge base search
- History and audit viewing

## API Reference

### Compute Dosage Function

```python
from src.tools.compute_dosage_tool import compute_dosage

result = compute_dosage(
    weight_kg=70.0,           # Patient weight
    drug_mg_per_kg=5.0,       # Drug dose per kg
    max_dose_mg=500.0         # Maximum allowed dose
)

# Returns:
# {
#     "result": 350.0,        # Safe dose in mg
#     "unit": "mg",
#     "detail": "explanation"
# }
```

### Medical Dosage Agent

```python
from src.agents.medical_dosage_agent import MedicalDosageAgent

agent = MedicalDosageAgent(rag_pipeline=rag, memory_system=memory)

response = agent.process_request(
    user_query="Calculate dosage for 85kg patient on Amoxicillin...",
    context={"patient_id": "P001", "drug_name": "Amoxicillin"}
)

# Returns:
# {
#     "success": True,
#     "response": "agent's answer",
#     "query": "original question",
#     "context": "provided context"
# }
```

## Security & Privacy

### Secrets Management
- ⚠️ Do not commit `.env` files that contain API keys
- Use environment variables: `GOOGLE_API_KEY`
- Example in `.env.example`

### Data Privacy
- Persistent memory stored locally
- No data sent to external services (except Google API)
- Audit logs for compliance tracking

## Deployment

### Streamlit Community Cloud (Recommended)

1. Push project to GitHub
2. Visit [streamlit.io/cloud](https://streamlit.io/cloud)
3. Create new app, select repository and `src/ui/app.py`
4. Add secrets in Streamlit dashboard:
   ```
   GOOGLE_API_KEY = "your_key_here"
   ```
5. Deploy and test the app from the hosted URL.

### Google Cloud Platform (GCP)

```bash
# Deploy with Cloud Run
gcloud run deploy medical-dosage-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$YOUR_API_KEY
```

### Docker

```bash
docker build -t medical-dosage-agent .
docker run -p 8501:8501 -e GOOGLE_API_KEY=$YOUR_API_KEY medical-dosage-agent
```

## Performance Benchmarks

### Load Testing Results
- **1000 dosage calculations**: ~500ms (0.5ms per calculation)
- **Tool integration latency**: <100ms
- **RAG retrieval**: 200-500ms depending on query complexity
- **Memory persistence**: <50ms (async)

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit your changes using conventional commit prefixes (examples below):
   ```bash
   git commit -m "feature: add new dosage guideline"
   git commit -m "fix: correct dosage validation logic"
   ```
3. Push and create Pull Request

### Commit Standards
- `feature:` New functionality
- `fix:` Bug fixes
- `docs:` Documentation
- `test:` Test additions
- `refactor:` Code restructuring

## Technical Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | Python 3.11, Streamlit |
| **LLM** | Google Generative AI (Gemini) |
| **Orchestration** | LangChain |
| **Vector DB** | ChromaDB |
| **Embeddings** | Google Generative AI Embeddings |
| **Testing** | pytest, pytest-cov |
| **Deployment** | Streamlit Cloud, GCP, Docker |

## Project Report

See [REPORT.md](REPORT.md) for:
- Detailed system architecture
- Test plan and results
- Performance analytics
- Team retrospective
- Lessons learned

## Support

If you run into issues or have questions:
1. Check [GitHub Issues](https://github.com/HayatoR28/Final-Project/issues)
2. Review documentation in `/docs`
3. Explore test examples in `/tests`

## License

MIT License - See LICENSE file

## Team

- **Sutton Wilterdink** - compute_dosage_tool.py
- **Asa Hayes** - RAG Pipeline & Agent
- **Randall Moses** - Streamlit UI & Deployment

---

**Project for COP2080: CS Problem Solving and Solution**
*Professor Navarro • Spring 2026*