# LegalEase

LegalEase is an AI-powered legal document drafting application built with Python, FastAPI, and Streamlit. It creates structured legal drafts for common document types and supports export to TXT, DOCX, and PDF.

> LegalEase provides AI-assisted document drafts and is not a substitute for professional legal advice. Users should review generated documents with a qualified legal professional before relying on them.

## Features

- AI document generation through the Google Gemini API
- Multi-page Streamlit SaaS-style interface
- Document templates for common legal forms
- Editable generated document preview
- TXT, DOCX, and PDF download support
- Local session-based document history
- FastAPI backend with health and generation endpoints

## Project Structure

```text
LegalEase/
├── backend/
│   ├── ai_core/
│   │   ├── __init__.py
│   │   └── gemini_generator.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── document_formatter.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── text_utils.py
│   ├── __init__.py
│   ├── config.py
│   └── main.py
├── frontend/
│   ├── __init__.py
│   ├── app.py
│   ├── components.py
│   ├── state.py
│   ├── styles.py
│   └── assets/
├── assets/
│   └── logo.svg
├── tests/
│   ├── test_api.py
│   ├── test_formatter.py
│   └── test_text_utils.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── pytest.ini
└── README.md
```

## Installation

### Windows PowerShell

```powershell
cd "C:\Users\ADMIN\OneDrive\Desktop\LegalEase\LegalEase"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file from `.env.example` and set your values:

```env
GEMINI_API_KEY=YOUR_API_KEY
GEMINI_MODEL=gemini-3.8-flash
BACKEND_URL=http://127.0.0.1:8000
APP_NAME=LegalEase
LOG_LEVEL=INFO
```

## Start the Backend

```powershell
cd "C:\Users\ADMIN\OneDrive\Desktop\LegalEase\LegalEase"
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

## Start the Frontend

Open a second terminal and run:

```powershell
cd "C:\Users\ADMIN\OneDrive\Desktop\LegalEase\LegalEase"
.\.venv\Scripts\Activate.ps1
streamlit run frontend/app.py
```

Open:

- Frontend: http://localhost:8501
- Backend: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

## Run Tests

```powershell
cd "C:\Users\ADMIN\OneDrive\Desktop\LegalEase\LegalEase"
.\.venv\Scripts\Activate.ps1
pytest -q
```

## Common Issues

### ModuleNotFoundError: No module named 'backend'

Run the command from the project root and ensure the project root is available on `sys.path`. The project is configured to insert the root when the frontend is launched from the root folder.

### Backend not running

Check the FastAPI process and confirm the backend is running on port 8000.

### Missing Gemini API key

Ensure `GEMINI_API_KEY` exists in `.env` and is not hard-coded in source files.

### Invalid document request

Make sure document type, parties and terms are present before generating.

## Output Formats

- TXT: plain text draft
- DOCX: structured Word document export
- PDF: branded generated PDF
- HTML preview: in-app formatted preview

## Disclaimer

LegalEase uses AI to draft documents for review. It does not guarantee legal validity and should not replace the advice of a qualified legal professional.
