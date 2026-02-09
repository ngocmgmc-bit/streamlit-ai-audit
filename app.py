import streamlit as st

st.set_page_config(page_title="Tool chấm thầu", layout="wide")

st.title("📑 HỆ THỐNG CHẤM THẦU – MODULE A1")

st.subheader("1️⃣ Upload Hồ sơ mời thầu (HSMT)")
hsmt_file = st.file_uploader(
    "Chọn file HSMT (PDF hoặc Word)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

st.subheader("2️⃣ Upload Hồ sơ dự thầu (HSDT)")
hsdt_files = st.file_uploader(
    "Chọn các file HSDT (PDF hoặc Word)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

st.divider()

if hsmt_file and hsdt_files:
    st.success(f"✅ Đã nhận {len(hsmt_file)} file HSMT và {len(hsdt_files)} file HSDT")

    st.markdown("### 📘 Danh sách HSMT")
    for i, f in enumerate(hsmt_file, start=1):
        st.write(f"{i}. {f.name}")

    st.markdown("### 📕 Danh sách HSDT")
    for i, f in enumerate(hsdt_files, start=1):
        st.write(f"{i}. {f.name}")
else:
    st.warning("⚠️ Vui lòng upload đủ ít nhất 1 HSMT và 1 HSDT")
import pdfplumber
from docx import Document
import io

def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def read_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

st.divider()
st.subheader("3️⃣ Nội dung trích xuất từ HSMT")

if hsmt_file:
    if hsmt_file.name.endswith(".pdf"):
        hsmt_text = read_pdf(hsmt_file)
    else:
        hsmt_text = read_docx(hsmt_file)

    st.text_area(
        "📄 Nội dung HSMT (đã trích xuất)",
        hsmt_text,
        height=400
    )
