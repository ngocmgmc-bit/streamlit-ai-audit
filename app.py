import streamlit as st
import pdfplumber
import google.generativeai as genai
import os
from docx import Document
from datetime import datetime

# =========================
# CẤU HÌNH
# =========================
st.set_page_config(
    page_title="CHẤM THẦU – TỔ CHUYÊN GIA",
    layout="wide"
)

st.title("📑 HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA")

# =========================
# API KEY
# =========================
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("❌ Chưa cấu hình GEMINI_API_KEY")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

# =========================
# HÀM DÙNG CHUNG
# =========================
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            if p.extract_text():
                text += p.extract_text() + "\n"
    return text.strip()

def ai(prompt):
    return model.generate_content(prompt).text

def export_word(content):
    doc = Document()
    doc.add_heading("BÁO CÁO ĐÁNH GIÁ HỒ SƠ DỰ THẦU", level=1)

    doc.add_paragraph(
        "Căn cứ Luật Đấu thầu số 22/2023/QH15 và "
        "Thông tư số 08/2022/TT-BKHĐT của Bộ Kế hoạch và Đầu tư.\n"
    )

    for line in content.split("\n"):
        doc.add_paragraph(line)

    filename = f"Bao_cao_cham_thau_{datetime.now().strftime('%Y%m%d_%H%M')}.docx"
    doc.save(filename)
    return filename

# =========================
# SIDEBAR
# =========================
tool = st.sidebar.radio(
    "🧠 CHỌN CHỨC NĂNG",
    [
        "📌 Trích xuất tiêu chí HSMT",
        "⚖️ Chấm HSDT (01 nhà thầu)",
        "🔍 AI rà soát & xuất báo cáo Word"
    ]
)

# =========================
# UPLOAD HSMT – NHIỀU FILE
# =========================
st.subheader("📥 Upload HSMT (có thể nhiều file)")
hsmt_files = st.file_uploader(
    "HSMT (PDF)",
    type="pdf",
    accept_multiple_files=True
)

hsmt_text = ""
if hsmt_files:
    for f in hsmt_files:
        hsmt_text += f"\n--- HSMT: {f.name} ---\n"
        hsmt_text += read_pdf(f)
    st.success(f"✅ Đã nạp {len(hsmt_files)} file HSMT")

# =========================
# UPLOAD HSDT – 1 NHÀ THẦU, NHIỀU FILE
# =========================
st.subheader("📥 Upload HSDT (01 nhà thầu – nhiều file)")
hsdt_files = st.file_uploader(
    "HSDT (PDF)",
    type="pdf",
    accept_multiple_files=True
)

hsdt_text = ""
if hsdt_files:
    for f in hsdt_files:
        hsdt_text += f"\n--- HSDT: {f.name} ---\n"
        hsdt_text += read_pdf(f)
    st.success(f"✅ Đã nạp {len(hsdt_files)} file HSDT")

# =========================
# TOOL 1 – TRÍCH XUẤT HSMT
# =========================
if tool == "📌 Trích xuất tiêu chí HSMT":
    if st.button("🤖 AI trích xuất"):
        prompt = f"""
Trích xuất tiêu chí đánh giá theo Thông tư 08/2022/TT-BKHĐT:
- Năng lực, kinh nghiệm
- Kỹ thuật
- Tài chính
- Điều kiện loại trực tiếp
- Nguyên tắc đánh giá đạt/không đạt

HSMT:
{hsmt_text}
"""
        st.text_area("📊 KẾT QUẢ", ai(prompt), height=450)

# =========================
# TOOL 2 – CHẤM HSDT
# =========================
if tool == "⚖️ Chấm HSDT (01 nhà thầu)":
    if st.button("⚖️ AI CHẤM THẦU"):
        prompt = f"""
Bạn là TỔ CHUYÊN GIA.

Hãy đánh giá HSDT theo HSMT, đúng Thông tư 08/2022/TT-BKHĐT:
1. Đánh giá năng lực & kinh nghiệm
2. Đánh giá kỹ thuật
3. Đánh giá tài chính
4. Kết luận đạt/không đạt
5. Kiến nghị

HSMT:
{hsmt_text}

HSDT:
{hsdt_text}
"""
        st.session_state["ket_qua"] = ai(prompt)
        st.text_area("📋 KẾT QUẢ CHẤM", st.session_state["ket_qua"], height=450)

# =========================
# TOOL 3 – RÀ SOÁT + WORD
# =========================
if tool == "🔍 AI rà soát & xuất báo cáo Word":
    if st.button("🔍 AI RÀ SOÁT & XUẤT WORD"):
        prompt = f"""
Rà soát HSDT theo HSMT và pháp luật đấu thầu:
- Thiếu / sai tài liệu?
- Nguy cơ bị loại?
- Rủi ro pháp lý?
- Kết luận cuối cùng cho Tổ chuyên gia

HSMT:
{hsmt_text}

HSDT:
{hsdt_text}
"""
        report = ai(prompt)
        filename = export_word(report)

        st.success("✅ Đã tạo báo cáo Word")
        with open(filename, "rb") as f:
            st.download_button(
                "📄 Tải báo cáo Word",
                f,
                file_name=filename
            )
