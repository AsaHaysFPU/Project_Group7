# Deployment Guide - SNAP Medical Dosage Agent

## Streamlit Community Cloud (Recommended)

### 1. Prerequisites
- GitHub account with project repository
- Streamlit account (free at [streamlit.io/cloud](https://streamlit.io/cloud))
- Google Generative AI API key

### 2. Prepare Repository

Ensure your GitHub repository has:
- ✅ `requirements.txt` with all dependencies
- ✅ `src/ui/app.py` as the main Streamlit app
- ✅ `.env.example` with template variables
- ✅ `.gitignore` to prevent committing secrets

### 3. Deploy to Streamlit Cloud

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "feat: ready for deployment"
   git push origin main
   ```

2. **Go to [streamlit.io/cloud](https://streamlit.io/cloud)**

3. **Click "New app"**
   - Select your GitHub account
   - Select `HayatoR28/Final-Project` repository
   - Select branch: `main`
   - Select file path: `src/ui/app.py`

4. **Add Secrets**
   - In the Streamlit Cloud dashboard, go to your app settings
   - Under "Secrets", add:
     ```
     [secrets]
     GOOGLE_API_KEY = "your_actual_api_key_here"
     ```

5. **Deploy!**
   - Click "Deploy"
   - Wait for the app to build and deploy
   - Share the public URL

### IMPORTANT: Secrets Management in Streamlit Cloud

**Never** commit `.env` file. Instead:

1. Create `.streamlit/secrets.toml` locally (git-ignored):
   ```toml
   GOOGLE_API_KEY = "your_key_here"
   ```

2. In Streamlit Cloud app settings, add the same secrets

3. Access in code:
   ```python
   import streamlit as st
   api_key = st.secrets["GOOGLE_API_KEY"]
   ```

## Google Cloud Platform Deployment

### Using Cloud Run (Containerized)

```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Deploy
gcloud run deploy medical-dosage-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$YOUR_API_KEY \
  --memory 2Gi
```

## Hugging Face Spaces Deployment

1. Create new Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Select "Docker" as the SDK
3. Clone and push to the Space repository
4. Add `HF_TOKEN` secret if needed
5. Space auto-deploys on push

## Docker Local Testing

```bash
# Build
docker build -t medical-dosage-agent .

# Run
docker run -p 8501:8501 \
  -e GOOGLE_API_KEY=$YOUR_API_KEY \
  medical-dosage-agent

# Visit http://localhost:8501
```

## Monitoring & Debugging

### Streamlit Cloud Logs
1. Go to app settings in Streamlit Cloud
2. Click "Manage app"
3. View logs in "Logs" section

### Common Issues

**Issue: "API key not found"**
- Verify secrets are set in Streamlit Cloud dashboard
- Check `.env` is in `.gitignore`
- Use `st.secrets["GOOGLE_API_KEY"]` not `os.getenv()`

**Issue: "ChromaDB not persisting"**
- Streamlit Cloud has ephemeral storage
- Add to app for first-run initialization:
  ```python
  if not os.path.exists("data/chroma_db"):
      rag.add_documents(MEDICAL_KNOWLEDGE_BASE)
  ```

**Issue: "Timeout during deployment"**
- Check `requirements.txt` for heavyweight dependencies
- Streamlit Cloud has 3GB RAM limit
- Consider removing unused dependencies

## Performance Optimization

### For Streamlit Cloud
```python
# Cache expensive operations
@st.cache_resource
def init_agent():
    return MedicalDosageAgent(...)

@st.cache_data
def get_kb_results(_rag, query):
    return _rag.retrieve(query)
```

### Reduce Startup Time
- Lazy-load RAG pipeline on first use
- Cache embedding model
- Use Streamlit's built-in caching

## Compliance & Security

✅ Never commit `.env` files\
✅ Use Streamlit Secrets for API keys\
✅ Enable HTTPS (automatic on Streamlit Cloud)\
✅ Review data access logs\
✅ Use audit trail for compliance

## Troubleshooting Deployment

Run this script to verify setup:

```python
# test_deployment.py
import os
from google.generativeai import configure
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY not found")
    exit(1)

try:
    configure(api_key=api_key)
    print("✅ API key valid")
except Exception as e:
    print(f"❌ API configuration failed: {e}")
    exit(1)

print("✅ All checks passed!")
```

Run: `python test_deployment.py`

## Getting Help

- Review Streamlit docs: https://docs.streamlit.io/
- Check Google Generative AI docs: https://ai.google.dev/
- Open GitHub issue if problems persist
