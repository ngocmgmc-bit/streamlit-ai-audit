import streamlit as st
import os
from google import genai
import PyPDF2
import docx
from io import BytesIO

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
# KHỞI TẠO GEMINI (SDK MỚI)
# ==============================
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    AI_READY = True
except Exception as e:
    AI_READY = False
    st.error("Không kết nối được Gemini API. Kiểm tra lại API KEY trong Secrets.")

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
# NÚT CHẤM THẦU
# ==============================

if st.button("CHẤM THẦU CHUYÊN SÂU"):

    if not AI_READY:
        st.stop()

    if not hsmt_files or not hsdt_files:
        st.warning("Vui lòng upload đầy đủ HSMT và HSDT.")
        st.stop()

    with st.spinner("Đang phân tích và đối chiếu chi tiết từng tiêu chí..."):

        hsmt_text = read_uploaded_files(hsmt_files)
        hsdt_text = read_uploaded_files(hsdt_files)

        prompt = f"""
Bạn là chuyên gia kiểm toán đấu thầu cao cấp.

Nhiệm vụ:
1. Trích xuất toàn bộ tiêu chí, tiêu chuẩn đánh giá từ HSMT.
2. Đối chiếu từng tiêu chí với nội dung tương ứng trong HSDT.
3. Không được bỏ sót tiêu chí nào.
4. Phân tích chi tiết từng mục:
   - Tiêu chí HSMT
   - Nội dung HSDT tương ứng
   - Đánh giá: Đạt / Không đạt / Thiếu / Cần làm rõ
   - Trích dẫn đoạn liên quan
5. Trình bày dưới dạng bảng chi tiết rõ ràng.

===== HỒ SƠ MỜI THẦU =====
{hsmt_text[:30000]}

===== HỒ SƠ DỰ THẦU =====
{hsdt_text[:30000]}
"""

        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )

            result = response.text

            st.success("Hoàn tất chấm thầu.")
            st.markdown(result)

        except Exception as e:
            st.error(f"Lỗi khi gọi AI: {e}")
