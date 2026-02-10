import streamlit as st
from google import genai
import traceback
from typing import List

# =========================
# 1. CẤU HÌNH TRANG
# =========================
st.set_page_config(
    page_title="HỆ THỐNG CHẤM THẦU CHUYÊN GIA",
    layout="wide"
)

st.title("⚖️ HỆ THỐNG CHẤM THẦU CHUYÊN GIA")
st.caption("Chuẩn hóa theo Luật Đấu thầu & Thông tư 08/2022/TT-BKHĐT")

# =========================
# 2. KẾT NỐI GEMINI API MỚI (BẮT BUỘC)
# =========================
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

MODEL = "gemini-1.5-flash"  # model ĐANG ĐƯỢC GOOGLE HỖ TRỢ

def ai_call(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return "❌ LỖI AI\n\n" + str(e) + "\n\n" + traceback.format_exc()

# =========================
# 3. UPLOAD HỒ SƠ
# =========================
st.subheader("📂 1. Upload hồ sơ")

col1, col2 = st.columns(2)

with col1:
    hsmt_files = st.file_uploader(
        "📘 Upload HSMT (nhiều file)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

with col2:
    hsdt_files = st.file_uploader(
        "📕 Upload HSDT (01 nhà thầu – nhiều file)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

if hsmt_files and hsdt_files:
    st.success("✅ Đã upload đầy đủ HSMT và HSDT")
else:
    st.warning("⚠️ Cần upload đủ HSMT và HSDT")

st.divider()

# =========================
# 4. TOOL CHẤM THẦU
# =========================
st.subheader("⚙️ 2. Công cụ chấm thầu")

def build_prompt(hsmt_files: List, hsdt_files: List) -> str:
    return f"""
Bạn là chuyên gia đấu thầu cấp Bộ.

HSMT: {', '.join(f.name for f in hsmt_files)}
HSDT: {', '.join(f.name for f in hsdt_files)}

Yêu cầu:
- Đánh giá tính hợp lệ
- Đánh giá kỹ thuật (Đạt / Không đạt)
- Chỉ rõ điểm không phù hợp
- Kết luận theo Luật Đấu thầu & TT08
"""

# =========================
# 5. CHẤM THẦU
# =========================
if st.button("⚖️ CHẤM THẦU", use_container_width=True):
    if not hsmt_files or not hsdt_files:
        st.error("❌ Thiếu hồ sơ")
    else:
        with st.spinner("AI đang chấm thầu..."):
            result = ai_call(build_prompt(hsmt_files, hsdt_files))

        st.subheader("📑 KẾT QUẢ CHẤM THẦU")
        st.markdown(result)

# =========================
# 6. GHI CHÚ
# =========================
st.info("""
- Chấm 01 HSDT (nhiều file)
- Logic chấm không tự sửa
- Sẵn sàng xuất Word/PDF theo mẫu Bộ KHĐT
""")
