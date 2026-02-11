import streamlit as st
import os
from google import genai
import PyPDF2
import docx

# =============================
# CẤU HÌNH TRANG
# =============================
st.set_page_config(
    page_title="HỆ THỐNG CHẤM THẦU CHUYÊN GIA",
    layout="wide"
)

st.title("HỆ THỐNG CHẤM THẦU CHUYÊN GIA")
st.caption("Chuẩn hóa theo Luật Đấu thầu & Thông tư 08/2022/TT-BKHĐT")

# =============================
# KẾT NỐI GEMINI API v1
# =============================
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    AI_READY = True
except Exception as e:
    AI_READY = False
    st.error("Không kết nối được Gemini API.")

# =============================
# HÀM ĐỌC FILE
# =============================
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
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

# =============================
# GIAO DIỆN UPLOAD
# =============================
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

# =============================
# CHẤM THẦU CHUYÊN SÂU
# =============================
if st.button("CHẤM THẦU CHUYÊN SÂU"):

    if not AI_READY:
        st.stop()

    if not hsmt_files or not hsdt_files:
        st.warning("Vui lòng upload đầy đủ HSMT và HSDT.")
        st.stop()

    with st.spinner("AI đang phân tích đối chiếu chi tiết từng tiêu chí..."):

        hsmt_text = read_uploaded_files(hsmt_files)
        hsdt_text = read_uploaded_files(hsdt_files)

        prompt = f"""
Bạn là chuyên gia kiểm toán đấu thầu cấp cao.

NHIỆM VỤ BẮT BUỘC:

1. Trích xuất TOÀN BỘ tiêu chí, tiêu chuẩn, yêu cầu kỹ thuật từ HSMT.
2. Đối chiếu CHI TIẾT từng tiêu chí với nội dung tương ứng trong HSDT.
3. Không được bỏ sót bất kỳ tiêu chí nào.
4. Không tự suy đoán.
5. Nếu không tìm thấy → ghi rõ "KHÔNG TÌM THẤY TRONG HSDT".
6. Chỉ đánh giá:
   - ĐẠT
   - KHÔNG ĐẠT
   - THIẾU
   - CẦN LÀM RÕ

Trình bày dạng bảng gồm:

| STT | Tiêu chí HSMT | Trích dẫn HSDT đối chiếu | Đánh giá | Nhận định chuyên gia |

===== HSMT =====
{hsmt_text[:40000]}

===== HSDT =====
{hsdt_text[:40000]}
"""

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )

            st.success("Hoàn tất chấm thầu.")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"Lỗi khi gọi AI: {e}")
        except Exception as e:
            st.error(f"Lỗi khi gọi AI: {e}")
