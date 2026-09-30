# SmartClean AI - Prototype V1

AI-Assisted Customer Data Validation and Import System.
Chi tiết mô tả ở file đặc tả

## Principles
- **No auto-modification:** AI outputs are suggestions. HITL is required.
- **Model Abstraction:** Core system relies on `BaseLLMValidator`, making model swaps trivial.
- **Traceability:** SQLite logs `original_data`, `final_data`, and `action_taken`.

## Setup
1. `python -m venv venv`
2. `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
3. `pip install -r requirements.txt`
4. Configure `.env` (Optional for V1 Mock, required for V2).

## Run
`streamlit run app.py`