from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

from backend.services.document_formatter import format_docx, format_html_preview, format_pdf, format_txt
from backend.utils.text_utils import slugify
from frontend.components import render_disclaimer, render_footer, render_top_nav
from frontend.state import DOCUMENT_TEMPLATES, add_document_to_history, ensure_session_state, reset_document_form
from frontend.styles import load_custom_css

st.set_page_config(page_title="LegalEase", page_icon="⚖️", layout="wide")
load_custom_css()
ensure_session_state()


def render_home_page() -> None:
    st.markdown(
        """
        <div class='hero'>
            <div style='display:flex; justify-content:space-between; align-items:center; gap:1rem; flex-wrap:wrap;'>
                <div>
                    <div class='tag' style='background:rgba(255,255,255,0.12); color:#fff;'>Legal AI Suite</div>
                    <h1>Create Legal Documents with AI</h1>
                    <p>Generate professional legal document drafts quickly with the power of Generative AI.</p>
                </div>
                <div>
                    <div style='display:flex; gap:0.5rem; flex-wrap: wrap;'> 
                        <button class='stButton' data-testid='home-create'>Create Your Document</button>
                        <button class='stButton' data-testid='home-templates'>Explore Templates</button>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Create Your Document", use_container_width=True):
        st.session_state.current_page = "Create Document"
        st.rerun()
    if st.button("Explore Templates", use_container_width=True):
        st.session_state.current_page = "Templates"
        st.rerun()

    st.markdown("<div class='section-header'><h2>Why LegalEase</h2></div>", unsafe_allow_html=True)
    render_disclaimer()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class='feature-card'>
                <div class='tag'>AI</div>
                <h3>AI-Powered Drafting</h3>
                <p>Turn your facts, parties and terms into structured legal drafts using Gemini.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class='feature-card'>
                <div class='tag'>Formats</div>
                <h3>Multiple Export Types</h3>
                <p>Download clean TXT, DOCX and PDF exports from the same generated draft.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class='feature-card'>
                <div class='tag'>Review</div>
                <h3>Editable Documents</h3>
                <p>Review, edit and tailor each document before final export and sign-off.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div class='section-header'><h2>Popular Documents</h2></div>", unsafe_allow_html=True)
    popular = [
        "Employment Contract",
        "Non-Disclosure Agreement",
        "Lease Agreement",
        "Service Agreement",
        "Freelance Agreement",
    ]
    for i in range(0, len(popular), 3):
        cols = st.columns(3)
        for j, item in enumerate(popular[i : i + 3]):
            with cols[j]:
                template = DOCUMENT_TEMPLATES[item]
                st.markdown(
                    f"""
                    <div class='template-card'>
                        <div class='tag'>Popular</div>
                        <h3>{item}</h3>
                        <p>{template['description']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Create", key=f"home_{slugify(item)}", use_container_width=True):
                    st.session_state.document_form = {
                        "document_type": item,
                        "parties": template["parties"],
                        "terms": template["starter_terms"],
                        "effective_date": "",
                        "additional_instructions": "",
                    }
                    st.session_state.current_page = "Create Document"
                    st.rerun()

    st.markdown("<div class='section-header'><h2>How LegalEase Works</h2></div>", unsafe_allow_html=True)
    steps = [
        "Choose a document type.",
        "Enter the parties and important terms.",
        "LegalEase sends the structured request to the FastAPI backend.",
        "Gemini generates an AI-assisted legal draft.",
        "Review and edit the document.",
        "Download as TXT, DOCX or PDF.",
    ]
    for idx, step in enumerate(steps, 1):
        st.markdown(f"**{idx}.** {step}")

    st.caption("LegalEase creates AI-assisted drafts for review and does not provide legal advice.")


def render_create_document_page() -> None:
    st.title("Create Your Legal Document")
    st.caption("Tell us what you need and LegalEase will generate an editable legal draft.")
    render_disclaimer()

    form_data = st.session_state.document_form
    document_type_options = [
        "Employment Contract",
        "Lease Agreement",
        "Non-Disclosure Agreement",
        "Service Agreement",
        "Freelance Agreement",
        "Custom Legal Document",
    ]

    with st.form("document_form"):
        col1, col2 = st.columns(2)
        with col1:
            selected_document_type = st.selectbox(
                "Document Type",
                options=document_type_options,
                index=document_type_options.index(form_data.get("document_type", "Employment Contract")),
            )
            custom_document = st.text_input(
                "Custom document title",
                value="" if selected_document_type != "Custom Legal Document" else form_data.get("document_type", ""),
                placeholder="Enter a custom document name",
            )
            parties = st.text_area(
                "Parties Involved",
                value=form_data.get("parties", ""),
                height=140,
                placeholder="ABC Technologies Pvt Ltd and Jane Doe",
            )
        with col2:
            effective_date = st.date_input(
                "Effective Date",
                value=date.today() if not form_data.get("effective_date") else date.fromisoformat(form_data["effective_date"]),
            )
            terms = st.text_area(
                "Terms & Conditions",
                value=form_data.get("terms", ""),
                height=140,
                placeholder="Salary: ₹50,000 per month; Working hours: 9 AM to 6 PM; Confidentiality required",
            )
            additional_instructions = st.text_area(
                "Additional Instructions",
                value=form_data.get("additional_instructions", ""),
                height=120,
                placeholder="Optional guidance for the draft",
            )
        submit = st.form_submit_button("Generate Document", type="primary", use_container_width=True)

    if submit:
        final_document_type = custom_document.strip() if selected_document_type == "Custom Legal Document" and custom_document.strip() else selected_document_type
        raw_terms = terms.strip()
        if additional_instructions.strip():
            raw_terms = f"{raw_terms}; {additional_instructions.strip()}" if raw_terms else additional_instructions.strip()
        if not final_document_type.strip():
            st.error("Please enter a document type.")
        elif not parties.strip():
            st.error("Please enter the parties involved.")
        elif not raw_terms:
            st.error("Please enter the key terms and conditions.")
        else:
            payload = {
                "document_type": final_document_type.strip(),
                "parties": parties.strip(),
                "terms": raw_terms,
                "effective_date": effective_date.isoformat(),
            }
            st.session_state.document_form = {
                "document_type": final_document_type,
                "parties": parties,
                "terms": raw_terms,
                "effective_date": effective_date.isoformat(),
                "additional_instructions": additional_instructions,
            }
            with st.spinner("LegalEase AI is drafting your document..."):
                try:
                    response = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=180)
                    if response.ok:
                        data = response.json()
                        st.session_state.generated_text = data["generated_text"]
                        st.session_state.document_status = "Document generated successfully."
                        st.success(st.session_state.document_status)
                        add_document_to_history(
                            {
                                "document_type": final_document_type,
                                "parties": parties,
                                "terms": raw_terms,
                                "effective_date": effective_date.isoformat(),
                                "additional_instructions": additional_instructions,
                                "content": data["generated_text"],
                                "created_at": date.today().strftime("%Y-%m-%d"),
                            }
                        )
                    else:
                        try:
                            detail = response.json().get("detail", response.text)
                        except ValueError:
                            detail = response.text
                        st.error(f"Unable to generate your document. {detail}")
                except requests.RequestException as exc:
                    st.error(f"Could not reach the backend at {BACKEND_URL}. Please start the FastAPI server first. Details: {exc}")

    if st.session_state.get("generated_text"):
        st.subheader("Document Preview")
        preview_text = st.text_area(
            "Editable document",
            value=st.session_state.generated_text,
            height=530,
            key="document_preview",
        )
        st.session_state.generated_text = preview_text

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.download_button(
                label="Download TXT",
                data=format_txt(st.session_state.generated_text),
                file_name=f"{slugify(st.session_state.document_form.get('document_type', 'legal-document'))}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                label="Download DOCX",
                data=format_docx(st.session_state.generated_text, st.session_state.document_form.get("document_type", "Legal Document"), st.session_state.document_form.get("terms", "")),
                file_name=f"{slugify(st.session_state.document_form.get('document_type', 'legal-document'))}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        with col3:
            st.download_button(
                label="Download PDF",
                data=format_pdf(st.session_state.generated_text, st.session_state.document_form.get("document_type", "Legal Document"), st.session_state.document_form.get("terms", "")),
                file_name=f"{slugify(st.session_state.document_form.get('document_type', 'legal-document'))}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with col4:
            if st.button("Generate Again", use_container_width=True):
                st.session_state.generated_text = ""
                st.rerun()

        st.write("Select the text in the editor above and use Ctrl+C to copy it.")
        if st.button("Start New Document"):
            reset_document_form()
            st.rerun()


def render_templates_page() -> None:
    st.title("Legal Document Templates")
    st.caption("Start with a professional template and tailor the details to your needs.")
    cols = st.columns(3)
    for idx, (name, template) in enumerate(DOCUMENT_TEMPLATES.items()):
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class='template-card'>
                    <div class='tag'>Template</div>
                    <h3>{name}</h3>
                    <p>{template['description']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Use {name}", key=f"template_page_{slugify(name)}", use_container_width=True):
                st.session_state.document_form = {
                    "document_type": name,
                    "parties": template["parties"],
                    "terms": template["starter_terms"],
                    "effective_date": "",
                    "additional_instructions": "",
                }
                st.session_state.current_page = "Create Document"
                st.rerun()


def render_documents_page() -> None:
    st.title("My Documents")
    st.caption("This version stores documents in your current Streamlit session. Refreshing the app clears local data.")
    docs = st.session_state.get("documents", [])
    if not docs:
        st.info("No documents generated yet. Visit Create Document to create your first draft.")
        return
    for idx, doc in enumerate(docs):
        st.markdown(
            """
            <div class='document-card'>
                <div class='tag'>Session document</div>
                <h3>{title}</h3>
                <p><strong>Type:</strong> {document_type}</p>
                <p><strong>Parties:</strong> {parties}</p>
                <p><strong>Created:</strong> {created}</p>
            </div>
            """.format(
                title=doc.get("document_type", "Legal Document"),
                document_type=doc.get("document_type", "Legal Document"),
                parties=doc.get("parties", "Not provided"),
                created=doc.get("created_at", "Recent"),
            ),
            unsafe_allow_html=True,
        )
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("View", key=f"history_view_{idx}", use_container_width=True):
                st.session_state.generated_text = doc.get("content", "")
                st.session_state.current_page = "Create Document"
                st.rerun()
        with col2:
            if st.button("Edit", key=f"history_edit_{idx}", use_container_width=True):
                st.session_state.document_form = {
                    "document_type": doc.get("document_type", "Legal Document"),
                    "parties": doc.get("parties", ""),
                    "terms": doc.get("terms", ""),
                    "effective_date": doc.get("effective_date", ""),
                    "additional_instructions": doc.get("additional_instructions", ""),
                }
                st.session_state.generated_text = doc.get("content", "")
                st.session_state.current_page = "Create Document"
                st.rerun()
        with col3:
            st.download_button(
                label="Download",
                data=(doc.get("content", "")).encode("utf-8"),
                file_name=f"{slugify(doc.get('document_type', 'document'))}.txt",
                mime="text/plain",
                key=f"history_download_{idx}",
                use_container_width=True,
            )
        with col4:
            if st.button("Delete", key=f"history_delete_{idx}", use_container_width=True):
                st.session_state.documents.pop(idx)
                st.rerun()
        st.divider()


def render_how_it_works_page() -> None:
    st.title("How LegalEase Works")
    steps = [
        "Choose a document type.",
        "Enter the parties and important terms.",
        "LegalEase sends the structured request to the FastAPI backend.",
        "Gemini generates an AI-assisted legal document draft.",
        "LegalEase formats the result.",
        "Review and edit the document.",
        "Download as TXT, DOCX or PDF.",
    ]
    for idx, step in enumerate(steps, 1):
        st.markdown(f"### {idx}. {step}")

    st.markdown(
        """
        <div class='feature-card'>
            <div class='tag'>Architecture</div>
            <p>USER → STREAMLIT → FASTAPI → GEMINI AI → DOCUMENT FORMATTER → TXT / DOCX / PDF</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_about_page() -> None:
    st.title("About LegalEase")
    st.write(
        "LegalEase is an AI-powered legal document drafting application designed to help users create structured legal document drafts more efficiently."
    )
    st.markdown(
        """
        <div class='feature-card'>
            <div class='tag'>Technology</div>
            <p>FastAPI • Streamlit • Google Gemini • Python • python-docx • ReportLab</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Why LegalEase?")
    bullets = [
        "Faster drafting",
        "Structured documents",
        "Easy editing",
        "Multiple export formats",
        "AI-assisted generation",
    ]
    for item in bullets:
        st.markdown(f"- {item}")
    render_disclaimer()


def render_help_page() -> None:
    st.title("Help & Frequently Asked Questions")
    faqs = {
        "What is LegalEase?": "LegalEase is an AI-powered legal drafting assistant that creates structured document drafts.",
        "How does AI generate my document?": "The Streamlit app sends the document requirements to the FastAPI backend, which calls the configured Gemini model.",
        "What document types can I create?": "Employment Contracts, Lease Agreements, NDAs, Service Agreements, Freelance Agreements and custom legal documents.",
        "Can I edit the generated document?": "Yes. The preview includes an editable text area before download.",
        "Can I download the document?": "Yes. Exports are available as TXT, DOCX and PDF.",
        "Does LegalEase provide legal advice?": "No. It provides AI-assisted drafts for review by qualified professionals.",
        "Where is my API key stored?": "In the project .env file, never in frontend code or source control.",
        "What should I do if generation fails?": "Confirm the backend is running, the Gemini API key is configured and the request is valid.",
    }
    for question, answer in faqs.items():
        with st.expander(question):
            st.write(answer)

    st.subheader("Troubleshooting")
    st.markdown(
        """
        - Backend not running: start uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
        - Missing Gemini API key: add GEMINI_API_KEY to .env
        - Connection refused: confirm the FastAPI server is running
        - ModuleNotFoundError: run from the project root and ensure the project root is on sys.path
        - Invalid request: make sure document type, parties and terms are supplied
        """
    )
    st.caption("Backend: http://127.0.0.1:8000")
    st.caption("API docs: http://127.0.0.1:8000/docs")
    st.caption("Frontend: http://localhost:8501")


def render_settings_page() -> None:
    st.title("Settings")
    settings = {
        "Application": "LegalEase",
        "Backend": "http://127.0.0.1:8000",
        "Model": os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
        "API key status": "Configured" if os.getenv("GEMINI_API_KEY") else "Not configured",
        "Python version": os.sys.version.split()[0],
        "Environment": "Local development",
    }
    for key, value in settings.items():
        st.write(f"**{key}:** {value}")

    if st.button("Test Health Endpoint"):
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=15)
            if response.ok:
                st.success(f"Backend health OK: {response.json()}")
            else:
                st.warning(f"Health check failed: {response.status_code} {response.text}")
        except requests.RequestException as exc:
            st.error(f"Could not reach backend: {exc}")

    if st.button("Test Backend Connection"):
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=15)
            if response.ok:
                st.success("Connected to backend successfully.")
            else:
                st.warning(f"Backend responded with {response.status_code}.")
        except requests.RequestException as exc:
            st.error(f"Disconnected from backend: {exc}")


def main() -> None:
    render_top_nav()
    page = st.session_state.get("current_page", "Home")

    if page == "Home":
        render_home_page()
    elif page == "Create Document":
        render_create_document_page()
    elif page == "Templates":
        render_templates_page()
    elif page == "My Documents":
        render_documents_page()
    elif page == "How It Works":
        render_how_it_works_page()
    elif page == "About":
        render_about_page()
    elif page == "Help":
        render_help_page()
    elif page == "Settings":
        render_settings_page()
    else:
        render_home_page()

    render_footer()


if __name__ == "__main__":
    main()
