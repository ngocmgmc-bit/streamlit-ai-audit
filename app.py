import streamlit as st
import pdfplumber
import docx
import tempfile
import os
from docx import Document
import google.generativeai as genai

# ================== CẤU HÌNH ==================
st.set_page_config(
    page_title="CHẤM THẦU CHUYÊN GIA",
    layout="wide"
)

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
MODEL_NAME = "models/gemini-1.5-pro"

# ================== HÀM TIỆN ÍCH ==================
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def read_docx(file):
    doc = docx.Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def read_files(files):
    full_text = ""
    for f in files:
        if f.name.lower().endswith(".pdf"):
            full_text += read_pdf(f)
        elif f.name.lower().endswith(".docx"):
            full_text += read_docx(f)
    return full_text.strip()

def ai_call(prompt):
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text

def export_word(content):
    doc = Document()
    doc.add_heading("BÁO CÁO ĐÁNH GIÁ HỒ SƠ DỰ THẦU", level=1)
    doc.add_paragraph(content)
    temp_path = tempfile.mktemp(suffix=".docx")
    doc.save(temp_path)
    return temp_path

# ================== GIAO DIỆN ==================
st.title("⚖️ HỆ THỐNG CHẤM THẦU CHUYÊN GIA")

with st.sidebar:
    st.header("📌 CHỌN CHỨC NĂNG")
    mode = st.radio(
        "",
        ["AI CHẤM THẦU & XUẤT WORD"]
    )

# ================== CHỨC NĂNG CHẤM THẦU ==================
if mode == "AI CHẤM THẦU & XUẤT WORD":

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📂 Upload HSMT (nhiều file)")
        hsmt_files = st.file_uploader(
            "",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            key="hsmt"
        )

    with col2:
        st.subheader("📂 Upload HSDT (1 nhà thầu – nhiều file)")
        hsdt_files = st.file_uploader(
            "",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            key="hsdt"
        )

    if hsmt_files and hsdt_files:
        if st.button("⚖️ AI CHẤM THẦU"):
            with st.spinner("AI đang phân tích hồ sơ..."):
                hsmt_text = read_files(hsmt_files)
                hsdt_text = read_files(hsdt_files)

                prompt = f"""
Bạn là chuyên gia đấu thầu theo Luật Đấu thầu Việt Nam và Thông tư 08/2022/TT-BKHĐT.

NHIỆM VỤ:
- Đánh giá HSDT so với HSMT
- Kết luận đạt / không đạt
- Nêu rõ lý do
- Trình bày theo văn phong báo cáo thẩm định chính thức

=== HSMT ===
{hsmt_text}

=== HSDT ===
{hsdt_text}
"""

                result = ai_call(prompt)
                st.success("✅ Chấm thầu hoàn tất")
                st.text_area("📄 KẾT QUẢ", result, height=400)

                word_path = export_word(result)
                with open(word_path, "rb") as f:
                    st.download_button(
                        "⬇️ TẢI BÁO CÁO WORD",
                        f,
                        file_name="Bao_cao_cham_thau.docx"
                    )
