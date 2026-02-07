import streamlit as st

st.set_page_config(page_title="Tool chấm thầu", layout="wide")

st.title("📑 HỆ THỐNG CHẤM THẦU – MODULE A1")

st.subheader("1️⃣ Upload Hồ sơ mời thầu (HSMT)")
hsmt_file = st.file_uploader(
    "Chọn file HSMT (PDF hoặc Word)",
    type=["pdf", "docx"],
    accept_multiple_files=False
)

st.subheader("2️⃣ Upload Hồ sơ dự thầu (HSDT)")
hsdt_files = st.file_uploader(
    "Chọn các file HSDT (PDF hoặc Word)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

st.divider()

if hsmt_file and hsdt_files:
    st.success("✅ Đã nhận đủ HSMT và HSDT")
    st.write(f"📄 HSMT: **{hsmt_file.name}**")
    st.write("📂 Danh sách HSDT:")
    for f in hsdt_files:
        st.write(f"– {f.name}")
else:
    st.warning("⚠️ Vui lòng upload đủ 1 HSMT và ít nhất 1 HSDT")
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
