import streamlit as st
import pdfplumber
from docx import Document

# ====== HÀM ĐỌC FILE ======
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def read_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

# ====== UI ======
st.title("AI Audit – Phân tích HSMT")

hsmt_files = st.file_uploader(
    "Upload Hồ sơ mời thầu (HSMT)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

st.divider()
st.subheader("Nội dung trích xuất từ HSMT (tách theo từng file)")

hsmt_docs = []

if hsmt_files:
    for file in hsmt_files:
        if file.name.lower().endswith(".pdf"):
            content = read_pdf(file)
        elif file.name.lower().endswith(".docx"):
            content = read_docx(file)
        else:
            content = ""

        if content.strip():
            hsmt_docs.append({
                "file_name": file.name,
                "content": content
            })

# ====== HIỂN THỊ TÁCH THEO FILE ======
if hsmt_docs:
    tabs = st.tabs([doc["file_name"] for doc in hsmt_docs])

    for tab, doc in zip(tabs, hsmt_docs):
        with tab:
            st.text_area(
                f"Nội dung file: {doc['file_name']}",
                doc["content"],
                height=400
            )
else:
    st.info("Chưa có nội dung HSMT để hiển thị")
