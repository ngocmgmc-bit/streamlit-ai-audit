import streamlit as st
from PyPDF2 import PdfReader
import docx

# =============================
# HÀM ĐỌC FILE
# =============================

def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


# =============================
# GIAO DIỆN APP
# =============================

st.set_page_config(page_title="AI Audit HSMT", layout="wide")
st.title("📊 AI Audit – Phân tích HSMT")

# =============================
# 1️⃣ UPLOAD HSMT (NHIỀU FILE)
# =============================

st.header("1️⃣ Upload Hồ sơ mời thầu (HSMT)")

hsmt_files = st.file_uploader(
    "Chọn file HSMT (PDF hoặc DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# =============================
# 2️⃣ TRÍCH XUẤT NỘI DUNG HSMT
# =============================

st.divider()
st.header("2️⃣ Nội dung trích xuất từ HSMT")

if hsmt_files:
    hsmt_texts = []

    for hsmt_file in hsmt_files:
        if hsmt_file.name.lower().endswith(".pdf"):
            text = read_pdf(hsmt_file)
        elif hsmt_file.name.lower().endswith(".docx"):
            text = read_docx(hsmt_file)
        else:
            text = ""

        if text.strip():
            hsmt_texts.append(
                f"===== FILE: {hsmt_file.name} =====\n{text}"
            )

    full_hsmt_text = "\n\n".join(hsmt_texts)

    st.text_area(
        "📄 Nội dung HSMT (đã trích xuất)",
        full_hsmt_text,
        height=500
    )
else:
    st.info("⬆️ Chưa upload file HSMT")

# =============================
# 3️⃣ (CHỪA CHỖ) CÁC BƯỚC SAU
# =============================

st.divider()
st.header("3️⃣ Phân tích & chấm thầu (sẽ triển khai tiếp)")
st.warning("Chưa triển khai – sẽ làm ở bước A2")
