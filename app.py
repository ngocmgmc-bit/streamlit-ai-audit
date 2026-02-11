import streamlit as st
import os
import tempfile
from PyPDF2 import PdfReader
from docx import Document
import google.generativeai as genai

# ================== CẤU HÌNH ==================
st.set_page_config(layout="wide")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
    AI_READY = True
except:
    AI_READY = False

# ================== HÀM ĐỌC FILE ==================
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def read_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text(uploaded_files):
    full_text = ""
    for file in uploaded_files:
        if file.name.endswith(".pdf"):
            full_text += read_pdf(file)
        elif file.name.endswith(".docx"):
            full_text += read_docx(file)
    return full_text


# ================== PROMPT CHUYÊN GIA ==================
AUDIT_PROMPT = """
Bạn là chuyên gia kiểm toán đấu thầu cấp cao...

(giữ nguyên nội dung prompt phần trên tôi đã cung cấp)
"""


# ================== GIAO DIỆN ==================
st.title("HỆ THỐNG CHẤM THẦU CHUYÊN GIA")
st.caption("Chuẩn hóa theo Luật Đấu thầu & Thông tư 08/2022/TT-BKHĐT")

if not AI_READY:
    st.warning("Gemini AI chưa sẵn sàng – App vẫn hoạt động bình thường")

# ================== UPLOAD ==================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload HSMT (nhiều file)")
    hsmt_files = st.file_uploader(
        "Chọn file HSMT",
        accept_multiple_files=True,
        type=["pdf", "docx"]
    )

with col2:
    st.subheader("Upload HSDT (1 nhà thầu – nhiều file)")
    hsdt_files = st.file_uploader(
        "Chọn file HSDT",
        accept_multiple_files=True,
        type=["pdf", "docx"]
    )

# ================== CHẤM THẦU ==================
if hsmt_files and hsdt_files:

    if st.button("CHẤM THẦU CHUYÊN SÂU"):

        with st.spinner("AI đang đối chiếu từng tiêu chí..."):

            hsmt_text = extract_text(hsmt_files)
            hsdt_text = extract_text(hsdt_files)

            full_prompt = AUDIT_PROMPT + f"""

=== HỒ SƠ MỜI THẦU ===
{hsmt_text}

=== HỒ SƠ DỰ THẦU ===
{hsdt_text}
"""

            try:
                response = model.generate_content(full_prompt)
                result = response.text

                st.success("Đối chiếu hoàn tất")

                st.markdown("## KẾT QUẢ ĐỐI CHIẾU CHI TIẾT")
                st.markdown(result)

            except Exception as e:
                st.error("Lỗi AI: " + str(e))

else:
    st.info("Vui lòng upload đầy đủ HSMT và HSDT để bắt đầu.")
