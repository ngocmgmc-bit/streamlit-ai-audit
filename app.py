import streamlit as st
import pdfplumber
import google.generativeai as genai
import os

# =========================
# CẤU HÌNH TRANG
# =========================
st.set_page_config(
    page_title="CHẤM THẦU CHUYÊN GIA",
    layout="wide"
)

st.title("📑 CHẤM THẦU CHUYÊN GIA (AI)")
st.caption("Phiên bản chuyên gia – phân tích HSMT & chấm HSDT")

# =========================
# CẤU HÌNH GEMINI
# =========================
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets")
    st.stop()

genai.configure(api_key=API_KEY)

# =========================
# HÀM ĐỌC PDF
# =========================
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text.strip()

# =========================
# HÀM GỌI GEMINI
# =========================
def call_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[LỖI AI] {str(e)}"

# =========================
# GIAO DIỆN
# =========================
tab1, tab2 = st.tabs(["📥 Upload HSMT", "📥 Upload HSDT"])

# -------- TAB HSMT --------
with tab1:
    st.subheader("📄 Upload Hồ sơ mời thầu (HSMT)")
    hsmt_file = st.file_uploader("Chọn file HSMT (PDF)", type=["pdf"])

    if hsmt_file:
        with st.spinner("Đang đọc HSMT..."):
            hsmt_text = extract_text_from_pdf(hsmt_file)
            st.success("✅ Đã đọc HSMT")

        if st.button("🤖 AI trích xuất tiêu chí chấm thầu"):
            prompt = f"""
Bạn là chuyên gia đấu thầu.
Từ nội dung HSMT sau, hãy trích xuất:
- Tiêu chí kỹ thuật
- Tiêu chí tài chính
- Điều kiện đạt / không đạt
- Thang điểm (nếu có)

HSMT:
{hsmt_text}
"""
            with st.spinner("AI đang phân tích..."):
                result = call_gemini(prompt)
                st.text_area("📌 Kết quả AI", result, height=400)

# -------- TAB HSDT --------
with tab2:
    st.subheader("📄 Upload Hồ sơ dự thầu (HSDT)")
    hsdt_file = st.file_uploader("Chọn file HSDT (PDF)", type=["pdf"])

    if hsdt_file:
        with st.spinner("Đang đọc HSDT..."):
            hsdt_text = extract_text_from_pdf(hsdt_file)
            st.success("✅ Đã đọc HSDT")

        if st.button("⚖️ AI đánh giá HSDT theo HSMT"):
            prompt = f"""
Bạn là chuyên gia chấm thầu.
Hãy đánh giá HSDT dưới đây dựa trên các tiêu chí trong HSMT.
Kết luận rõ: ĐẠT / KHÔNG ĐẠT và nhận xét chi tiết.

HSDT:
{hsdt_text}
"""
            with st.spinner("AI đang chấm thầu..."):
                result = call_gemini(prompt)
                st.text_area("📊 Kết quả chấm thầu", result, height=400)
