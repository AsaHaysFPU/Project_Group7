# Contributing to SNAP

## Code of Conduct
Be respectful, inclusive, and professional. Focus on code quality and team collaboration.

## Getting Started

### 1. Fork & Clone
```bash
git clone https://github.com/yourusername/Final-Project.git
cd Final-Project
```

### 2. Create Development Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Set Up Development Environment
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

### 4. Make Changes
- Write clean, documented code
- Follow PEP 8 style guide
- Add tests for new functionality
- Update documentation

### 5. Test Locally
```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_compute_dosage_tool.py -v

# Check coverage
pytest tests/ --cov=src --cov-report=html

# Format code
black src/ tests/

# Lint
flake8 src/ tests/
```

### 6. Commit with Conventional Commits
```bash
# Feature
git commit -m "feature: add new drug guideline to RAG pipeline"

# Bug fix
git commit -m "fix: correct dosage calculation edge case"

# Documentation
git commit -m "docs: update deployment instructions"

# Tests
git commit -m "test: add load testing for 5000 concurrent requests"

# Refactoring
git commit -m "refactor: simplify memory persistence logic"

# Chore
git commit -m "chore: update dependencies"
```

### 7. Push & Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then on GitHub, create Pull Request with:
- Clear title
- Description of changes
- Related issues (if any)
- Screenshots if UI changes

## Commit Message Guidelines

Format: `type: description`

### Types
- `feature:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Test addition/modification
- `refactor:` Code refactoring
- `perf:` Performance improvement
- `chore:` Build/dependency updates

### Examples
```
feature: add new dosage validator function
fix: handle negative weight input validation
docs: update RAG pipeline documentation
test: add integration test for full workflow
refactor: simplify agent initialization
perf: optimize RAG retrieval caching
```

### Requirements per Week
- **Minimum 3 meaningful commits per person per week**
- No mega-commits (entire project at once = -20 points)
- Each commit should be logically complete

## Code Quality Standards

### Python Style
- Follow PEP 8
- Line length: 100 characters max
- Use type hints where possible
- Document functions with docstrings

### Example Function
```python
def compute_safe_dosage(
    patient_weight_kg: float,
    drug_dose_mg_per_kg: float,
    maximum_dose_mg: float
) -> Dict[str, Union[float, str]]:
    """
    Calculate safe medication dosage for patient.
    
    Args:
        patient_weight_kg: Patient weight in kilograms
        drug_dose_mg_per_kg: Recommended dose per kg
        maximum_dose_mg: Maximum allowed dose
    
    Returns:
        Dictionary with safe dose, unit, and explanation
    
    Raises:
        ValueError: If any parameter is invalid
        TypeError: If parameters are wrong type
    """
    # Implementation
    return result
```

### Testing Requirements
- Unit tests for new functions
- Integration tests for workflows
- Edge case coverage
- Load/performance tests where applicable

## PR Review Process

1. **Automated Checks**
   - Tests must pass
   - Code coverage shouldn't decrease
   - No hardcoded secrets

2. **Code Review**
   - At least one approval required
   - Address all review comments
   - Keep history (don't force-push)

3. **Merge**
   - Squash or rebase as appropriate
   - Delete feature branch after merge

## Working on Different Components

### Adding a Tool
1. Create new file in `src/tools/`
2. Write tests in `tests/`
3. Add to `src/agents/medical_dosage_agent.py` tool list
4. Test integration with agent

Example:
```python
# src/tools/my_new_tool.py
def my_dosage_tool(param1: float, param2: float) -> dict:
    """Tool description."""
    # Implementation
    return {"result": ..., "detail": ...}
```

### Adding RAG Knowledge
1. Add documents to `MEDICAL_KNOWLEDGE_BASE` in `src/rag/rag_pipeline.py`
2. Test retrieval with queries
3. Verify embedding quality

### Updating UI
1. Modify `src/ui/app.py`
2. Test locally with `streamlit run src/ui/app.py`
3. Test all tabs/features work
4. Verify responsive design

### Memory Persistence
1. Extend `PersistentMemory` class in `src/memory/persistent_memory.py`
2. Add load/save methods
3. Test persistence across restarts

## Documentation

### Update README if you:
- Add new features
- Change API
- Modify installation steps
- Add new dependencies

### Add docstrings for:
- All functions
- All classes
- Complex logic sections

### Keep updated:
- Installation instructions
- Architecture diagrams
- API examples
- Deployment steps

## Performance Considerations

- Keep tool functions fast (<100ms)
- Cache expensive operations
- Profile before optimizing
- Test with load scenarios

## Security

- ❌ Never commit API keys
- ❌ Never commit passwords
- ✅ Use environment variables
- ✅ Use `.env.example` template
- ✅ Review all inputs for validation

## Questions or Issues?

1. Check existing issues
2. Check documentation
3. Ask in pull request comments
4. Create new issue with clear description

## Acknowledgments

Thanks for contributing to SNAP! Your work helps create safer medical systems. 
