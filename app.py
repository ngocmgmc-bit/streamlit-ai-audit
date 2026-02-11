import streamlit as st
import os
import google.generativeai as genai
import PyPDF2
import docx

# ==============================
# CẤU HÌNH TRANG
# ==============================
st.set_page_config(
    page_title="HỆ THỐNG CHẤM THẦU CHUYÊN GIA",
    layout="wide"
)

st.title("HỆ THỐNG CHẤM THẦU CHUYÊN GIA")
st.caption("Chuẩn hóa theo Luật Đấu thầu & Thông tư 08/2022/TT-BKHĐT")

# ==============================
# KẾT NỐI GEMINI (ỔN ĐỊNH V1BETA)
# ==============================
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-pro")
    AI_READY = True
except Exception as e:
    AI_READY = False
    st.error("Không kết nối được Gemini API.")

# ==============================
# HÀM ĐỌC FILE
# ==============================
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def read_uploaded_files(uploaded_files):
    combined_text = ""
    for file in uploaded_files:
        if file.name.lower().endswith(".pdf"):
            combined_text += extract_text_from_pdf(file)
        elif file.name.lower().endswith(".docx"):
            combined_text += extract_text_from_docx(file)
    return combined_text

# ==============================
# GIAO DIỆN UPLOAD
# ==============================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload HSMT (nhiều file)")
    hsmt_files = st.file_uploader(
        "Chọn file HSMT",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

with col2:
    st.subheader("Upload HSDT (1 nhà thầu – nhiều file)")
    hsdt_files = st.file_uploader(
        "Chọn file HSDT",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

# ==============================
# CHẤM THẦU
# ==============================
if st.button("CHẤM THẦU CHUYÊN SÂU"):

    if not AI_READY:
        st.stop()

    if not hsmt_files or not hsdt_files:
        st.warning("Vui lòng upload đầy đủ HSMT và HSDT.")
        st.stop()

    with st.spinner("Đang phân tích và đối chiếu chi tiết..."):

        hsmt_text = read_uploaded_files(hsmt_files)
        hsdt_text = read_uploaded_files(hsdt_files)

        prompt = f"""
Bạn là chuyên gia kiểm toán đấu thầu cao cấp.

Nhiệm vụ:
1. Trích xuất toàn bộ tiêu chí, tiêu chuẩn đánh giá từ HSMT.
2. Đối chiếu từng tiêu chí với HSDT.
3. Không được bỏ sót.
4. Trình bày dạng bảng gồm:
   - Tiêu chí HSMT
   - Nội dung HSDT tương ứng
   - Đánh giá: Đạt / Không đạt / Thiếu / Cần làm rõ
   - Trích dẫn đối chiếu cụ thể

===== HSMT =====
{hsmt_text[:25000]}

===== HSDT =====
{hsdt_text[:25000]}
"""

        try:
            response = model.generate_content(prompt)
            result = response.text

            st.success("Hoàn tất chấm thầu.")
            st.markdown(result)

        except Exception as e:
            st.error(f"Lỗi khi gọi AI: {e}")
