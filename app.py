import streamlit as st
import os
import pdfplumber
from google.generativeai import GenerativeModel, configure

# ==================================================
# CẤU HÌNH CHUNG
# ==================================================
st.set_page_config(
    page_title="Hệ thống chấm thầu – Tổ chuyên gia",
    layout="wide"
)

# ==================================================
# KIỂM TRA API KEY
# ==================================================
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    st.error("❌ Chưa cấu hình biến môi trường GEMINI_API_KEY")
    st.stop()

configure(api_key=GOOGLE_API_KEY)

# ==================================================
# MODEL GEMINI (ĐÃ FIX)
# ==================================================
model = GenerativeModel("models/gemini-1.5-pro")

# ==================================================
# HÀM TIỆN ÍCH
# ==================================================
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Trang {i+1} ---\n{page_text}"
    return text


def call_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"[LỖI AI] {str(e)}"


def ai_extract_criteria(hsmt_text):
    prompt = f"""
Bạn là chuyên gia đấu thầu.

Từ nội dung HSMT sau, hãy TRÍCH XUẤT ĐẦY ĐỦ các tiêu chí đánh giá HSDT.

Yêu cầu:
- Bám sát HSMT
- Chia nhóm: Kỹ thuật / Năng lực / Tài chính / Khác
- Mỗi tiêu chí gồm:
  • Tên tiêu chí
  • Mô tả
  • Căn cứ HSMT

Trình bày rõ ràng, dạng gạch đầu dòng.

HSMT:
{hsmt_text}
"""
    return call_gemini(prompt)


def ai_evaluate(criteria_text, hsdt_text):
    prompt = f"""
Bạn là tổ chuyên gia chấm thầu.

Căn cứ các tiêu chí sau:
{criteria_text}

Đánh giá hồ sơ dự thầu (HSDT):
{hsdt_text}

Yêu cầu:
- Đánh giá từng tiêu chí
- Kết luận: ĐẠT / KHÔNG ĐẠT
- Trích dẫn căn cứ từ HSDT
- Văn phong báo cáo tổ chuyên gia
"""
    return call_gemini(prompt)

# ==================================================
# KHỞI TẠO SESSION STATE (CỰC QUAN TRỌNG)
# ==================================================
if "hsmt_text" not in st.session_state:
    st.session_state.hsmt_text = None

if "hsdt_text" not in st.session_state:
    st.session_state.hsdt_text = None

if "criteria_text" not in st.session_state:
    st.session_state.criteria_text = None

# ==================================================
# GIAO DIỆN
# ==================================================
st.title("📊 HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA")

tabs = st.tabs([
    "📁 Upload HSMT & HSDT",
    "🎯 Gán tiêu chí (AI)",
    "📑 Chấm thầu"
])

# ==================================================
# TAB 1: UPLOAD HSMT & HSDT
# ==================================================
with tabs[0]:
    st.subheader("📁 Upload hồ sơ")

    hsmt_files = st.file_uploader(
        "Upload HSMT (PDF – có thể nhiều file)",
        type=["pdf"],
        accept_multiple_files=True,
        key="hsmt_uploader"
    )

    if hsmt_files:
        text = ""
        for f in hsmt_files:
            text += extract_text_from_pdf(f) + "\n\n"
        st.session_state.hsmt_text = text
        st.success(f"✅ Đã đọc {len(hsmt_files)} file HSMT")

    if st.session_state.hsmt_text:
        st.info("📌 HSMT đã được lưu trong phiên làm việc")

    st.divider()

    hsdt_files = st.file_uploader(
        "Upload HSDT (PDF – có thể nhiều file)",
        type=["pdf"],
        accept_multiple_files=True,
        key="hsdt_uploader"
    )

    if hsdt_files:
        text = ""
        for f in hsdt_files:
            text += extract_text_from_pdf(f) + "\n\n"
        st.session_state.hsdt_text = text
        st.success(f"✅ Đã đọc {len(hsdt_files)} file HSDT")

    if st.session_state.hsdt_text:
        st.info("📌 HSDT đã được lưu trong phiên làm việc")

# ==================================================
# TAB 2: GÁN TIÊU CHÍ
# ==================================================
with tabs[1]:
    st.subheader("🎯 Gán tiêu chí đánh giá theo HSMT")

    if not st.session_state.hsmt_text:
        st.warning("⚠️ Chưa có HSMT. Vui lòng upload ở tab 1.")
        st.stop()

    if st.button("🤖 AI gợi ý tiêu chí từ HSMT"):
        with st.spinner("AI đang phân tích HSMT..."):
            criteria = ai_extract_criteria(st.session_state.hsmt_text)
            st.session_state.criteria_text = criteria
        st.success("✅ Đã trích xuất tiêu chí từ HSMT")

    if st.session_state.criteria_text:
        st.text_area(
            "Danh sách tiêu chí (có thể chỉnh sửa)",
            value=st.session_state.criteria_text,
            height=450
        )

# ==================================================
# TAB 3: CHẤM THẦU
# ==================================================
with tabs[2]:
    st.subheader("📑 Chấm thầu – Báo cáo tổ chuyên gia")

    if not st.session_state.criteria_text:
        st.warning("⚠️ Chưa có tiêu chí đánh giá")
        st.stop()

    if not st.session_state.hsdt_text:
        st.warning("⚠️ Chưa có HSDT")
        st.stop()

    if st.button("⚖️ Thực hiện chấm thầu"):
        with st.spinner("AI đang chấm thầu..."):
            result = ai_evaluate(
                st.session_state.criteria_text,
                st.session_state.hsdt_text
            )
        st.success("✅ Chấm thầu hoàn tất")

        st.text_area(
            "📄 KẾT QUẢ CHẤM THẦU (chuẩn báo cáo tổ chuyên gia)",
            value=result,
            height=550
        )
