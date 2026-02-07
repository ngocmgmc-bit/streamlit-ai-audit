import streamlit as st
import pdfplumber
import docx

st.set_page_config(page_title="AI AUDIT – Chấm thầu", layout="centered")

st.title("📑 AI AUDIT – Chấm thầu hồ sơ")
st.write("Upload hồ sơ dự thầu (PDF / Word) để kiểm tra theo tiêu chí")

uploaded_file = st.file_uploader(
    "Chọn hồ sơ dự thầu",
    type=["pdf", "docx"]
)

def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.lower()

def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs]).lower()

# ===== TIÊU CHÍ CHẤM THẦU (CÓ THỂ ĐỔI SAU) =====
criteria = {
    "Bảo lãnh dự thầu": ["bảo lãnh dự thầu"],
    "Thời gian hiệu lực hồ sơ": ["hiệu lực hồ sơ", "thời gian hiệu lực"],
    "Năng lực tài chính": ["báo cáo tài chính", "doanh thu"],
    "Nhân sự chủ chốt": ["chỉ huy trưởng", "nhân sự chủ chốt"],
}

if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        content = read_pdf(uploaded_file)
    else:
        content = read_docx(uploaded_file)

    st.subheader("📊 Kết quả chấm thầu")

    for item, keywords in criteria.items():
        if any(k in content for k in keywords):
            st.success(f"✅ {item}: ĐẠT")
        else:
            st.error(f"❌ {item}: KHÔNG ĐẠT")
