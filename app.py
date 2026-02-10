import streamlit as st
import google.generativeai as genai
from typing import List
import traceback

# =========================
# 1. CẤU HÌNH CHUNG
# =========================
st.set_page_config(
    page_title="HỆ THỐNG CHẤM THẦU CHUYÊN GIA",
    layout="wide"
)

st.title("⚖️ HỆ THỐNG CHẤM THẦU CHUYÊN GIA")
st.caption("Chuẩn hóa theo Luật Đấu thầu & Thông tư 08/2022/TT-BKHĐT")

# =========================
# 2. KẾT NỐI GEMINI (AN TOÀN)
# =========================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

MODEL_NAME = "models/gemini-1.5-pro"

def ai_call(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        # ĐỌC OUTPUT AN TOÀN
        if hasattr(response, "text") and response.text:
            return response.text

        if hasattr(response, "parts"):
            return "\n".join([p.text for p in response.parts if hasattr(p, "text")])

        return "❌ AI không trả về nội dung."

    except Exception as e:
        return f"❌ Lỗi AI:\n{str(e)}\n\n{traceback.format_exc()}"

# =========================
# 3. UPLOAD FILE
# =========================
st.subheader("📂 1. Upload hồ sơ")

col1, col2 = st.columns(2)

with col1:
    hsmt_files = st.file_uploader(
        "📘 Upload HSMT (có thể nhiều file)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

with col2:
    hsdt_files = st.file_uploader(
        "📕 Upload HSDT (1 nhà thầu – nhiều file)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

# =========================
# 4. KIỂM TRA ĐẦU VÀO
# =========================
if hsmt_files and hsdt_files:
    st.success("✅ Đã upload đầy đủ HSMT và HSDT")
else:
    st.warning("⚠️ Cần upload đầy đủ HSMT và HSDT trước khi chấm thầu")

st.divider()

# =========================
# 5. TOOL CHẤM THẦU
# =========================
st.subheader("⚙️ 2. Công cụ chấm thầu")

def build_prompt(hsmt_files: List, hsdt_files: List) -> str:
    hsmt_names = ", ".join([f.name for f in hsmt_files])
    hsdt_names = ", ".join([f.name for f in hsdt_files])

    return f"""
Bạn là CHUYÊN GIA ĐẤU THẦU cấp Bộ.

NHIỆM VỤ:
- Rà soát 01 hồ sơ dự thầu (HSDT) gồm nhiều file
- Đối chiếu với HSMT
- Đánh giá theo:
  + Luật Đấu thầu Việt Nam hiện hành
  + Thông tư 08/2022/TT-BKHĐT
- Không suy diễn, không bịa thông tin

DỮ LIỆU:
- HSMT: {hsmt_names}
- HSDT: {hsdt_names}

YÊU CẦU KẾT QUẢ:
1. Bảng tổng hợp đánh giá tính hợp lệ
2. Bảng đáp ứng kỹ thuật (Đạt / Không đạt)
3. Các điểm không phù hợp (nếu có)
4. Kết luận sơ bộ

TRÌNH BÀY RÕ RÀNG – NGẮN GỌN – CHUẨN MẪU BỘ KHĐT
"""

# =========================
# 6. NÚT CHẤM THẦU
# =========================
if st.button("⚖️ CHẤM THẦU", use_container_width=True):
    if not hsmt_files or not hsdt_files:
        st.error("❌ Thiếu HSMT hoặc HSDT")
    else:
        with st.spinner("🔍 AI đang chấm thầu..."):
            prompt = build_prompt(hsmt_files, hsdt_files)
            result = ai_call(prompt)

        st.subheader("📑 KẾT QUẢ CHẤM THẦU")
        st.markdown(result)

# =========================
# 7. GHI CHÚ
# =========================
st.info("""
🔒 Lưu ý:
- Hệ thống hiện chấm 01 HSDT (nhiều file)
- Có thể mở rộng xuất Word/PDF theo mẫu Bộ KHĐT
- Logic chấm không tự ý sửa
""")
