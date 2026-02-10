import streamlit as st
import pdfplumber
import google.generativeai as genai
import os
from docx import Document
from docx.shared import Pt
from datetime import datetime

# ======================================================
# CẤU HÌNH GIAO DIỆN (GIỮ NGUYÊN LOGIC)
# ======================================================
st.set_page_config(
    page_title="HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA",
    layout="wide"
)

# ===== CSS GIAO DIỆN (BỔ SUNG – KHÔNG ẢNH HƯỞNG LOGIC) =====
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: "Segoe UI", Arial, sans-serif;
    background-color: #f6f8fb;
}

h1, h2, h3 {
    color: #0f172a;
    font-weight: 700;
}

.block-container {
    padding: 2rem 3rem;
}

.card {
    background: white;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.05);
}

.stButton > button {
    background-color: #1d4ed8;
    color: white;
    font-weight: 600;
    border-radius: 8px;
    padding: 0.55rem 1.4rem;
}

.stButton > button:hover {
    background-color: #1e40af;
}

section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

section[data-testid="stSidebar"] * {
    color: white;
}

hr {
    border: none;
    height: 1px;
    background: #e5e7eb;
    margin: 2.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# TIÊU ĐỀ
# ======================================================
st.markdown("""
<div class="card">
<h1>📑 HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA</h1>
<p style="color:#475569;font-size:15px;">
Áp dụng Luật Đấu thầu 2023 & Thông tư 08/2022/TT-BKHĐT – sử dụng nội bộ
</p>
</div>
""", unsafe_allow_html=True)

# ======================================================
# API KEY (GIỮ NGUYÊN)
# ======================================================
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("❌ Chưa cấu hình GEMINI_API_KEY")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

# ======================================================
# HÀM DÙNG CHUNG (GIỮ NGUYÊN)
# ======================================================
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            if p.extract_text():
                text += p.extract_text() + "\n"
    return text.strip()

def ai(prompt):
    return model.generate_content(prompt).text

def export_word(hsmt_files, hsdt_files, tech_result, fin_result, conclusion):
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(13)

    doc.add_heading("BÁO CÁO ĐÁNH GIÁ HỒ SƠ DỰ THẦU", level=1)

    doc.add_paragraph(
        "Căn cứ Luật Đấu thầu số 22/2023/QH15;\n"
        "Căn cứ Thông tư số 08/2022/TT-BKHĐT;\n"
        "Tổ chuyên gia lập báo cáo đánh giá HSDT như sau:\n"
    )

    doc.add_heading("I. DANH MỤC HỒ SƠ MỜI THẦU", level=2)
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'
    table.rows[0].cells[0].text = "STT"
    table.rows[0].cells[1].text = "Tên tài liệu"
    for i, f in enumerate(hsmt_files, 1):
        r = table.add_row().cells
        r[0].text = str(i)
        r[1].text = f.name

    doc.add_heading("II. DANH MỤC HỒ SƠ DỰ THẦU", level=2)
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'
    table.rows[0].cells[0].text = "STT"
    table.rows[0].cells[1].text = "Tên tài liệu"
    for i, f in enumerate(hsdt_files, 1):
        r = table.add_row().cells
        r[0].text = str(i)
        r[1].text = f.name

    doc.add_heading("III. ĐÁNH GIÁ KỸ THUẬT", level=2)
    doc.add_paragraph(tech_result)

    doc.add_heading("IV. ĐÁNH GIÁ TÀI CHÍNH", level=2)
    doc.add_paragraph(fin_result)

    doc.add_heading("V. KẾT LUẬN VÀ KIẾN NGHỊ", level=2)
    doc.add_paragraph(conclusion)

    filename = f"Bao_cao_cham_thau_TT08_{datetime.now().strftime('%Y%m%d_%H%M')}.docx"
    doc.save(filename)
    return filename

# ======================================================
# SIDEBAR (GIỮ NGUYÊN CHỨC NĂNG)
# ======================================================
tool = st.sidebar.radio(
    "🧠 CHỌN CHỨC NĂNG",
    [
        "📌 Trích xuất tiêu chí HSMT",
        "⚖️ Chấm HSDT & xuất Word"
    ]
)

# ======================================================
# KHỐI UPLOAD
# ======================================================
st.markdown('<div class="card"><h2>📥 HỒ SƠ MỜI THẦU (HSMT)</h2></div>', unsafe_allow_html=True)
hsmt_files = st.file_uploader("Upload HSMT (PDF – nhiều file)", type="pdf", accept_multiple_files=True)

hsmt_text = ""
if hsmt_files:
    for f in hsmt_files:
        hsmt_text += f"\n--- HSMT: {f.name} ---\n"
        hsmt_text += read_pdf(f)
    st.success(f"✅ Đã nạp {len(hsmt_files)} file HSMT")

st.markdown('<div class="card"><h2>📥 HỒ SƠ DỰ THẦU (HSDT – 01 nhà thầu)</h2></div>', unsafe_allow_html=True)
hsdt_files = st.file_uploader("Upload HSDT (PDF – nhiều file)", type="pdf", accept_multiple_files=True)

hsdt_text = ""
if hsdt_files:
    for f in hsdt_files:
        hsdt_text += f"\n--- HSDT: {f.name} ---\n"
        hsdt_text += read_pdf(f)
    st.success(f"✅ Đã nạp {len(hsdt_files)} file HSDT")

# ======================================================
# CHỨC NĂNG (GIỮ NGUYÊN LOGIC)
# ======================================================
if tool == "📌 Trích xuất tiêu chí HSMT":
    st.markdown('<div class="card"><h2>📌 TRÍCH XUẤT TIÊU CHÍ</h2></div>', unsafe_allow_html=True)
    if st.button("🤖 AI TRÍCH XUẤT"):
        result = ai(f"""
Trích xuất tiêu chí đánh giá theo Thông tư 08/2022/TT-BKHĐT:
- Năng lực & kinh nghiệm
- Kỹ thuật
- Tài chính
- Điều kiện loại trực tiếp

HSMT:
{hsmt_text}
""")
        st.text_area("KẾT QUẢ", result, height=450)

if tool == "⚖️ Chấm HSDT & xuất Word":
    st.markdown('<div class="card"><h2>⚖️ ĐÁNH GIÁ & XUẤT BÁO CÁO</h2></div>', unsafe_allow_html=True)
    if st.button("⚖️ AI CHẤM THẦU & XUẤT WORD"):
        tech = ai(f"Đánh giá kỹ thuật:\nHSMT:\n{hsmt_text}\nHSDT:\n{hsdt_text}")
        fin = ai(f"Đánh giá tài chính:\nHSMT:\n{hsmt_text}\nHSDT:\n{hsdt_text}")
        conclusion = ai("Kết luận cuối cùng cho Tổ chuyên gia")

        filename = export_word(hsmt_files, hsdt_files, tech, fin, conclusion)
        st.success("✅ Đã tạo báo cáo Word")
        with open(filename, "rb") as f:
            st.download_button("📄 Tải báo cáo Word", f, file_name=filename)
