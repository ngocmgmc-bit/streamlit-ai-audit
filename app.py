import streamlit as st
import os
import pdfplumber
from google.generativeai import GenerativeModel, configure

# =========================
# CẤU HÌNH CHUNG
# =========================
st.set_page_config(page_title="Hệ thống chấm thầu – Tổ chuyên gia", layout="wide")

# =========================
# KIỂM TRA API KEY
# =========================
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    st.error("❌ Chưa cấu hình GEMINI_API_KEY trong biến môi trường")
    st.stop()

configure(api_key=GOOGLE_API_KEY)
model = GenerativeModel("models/gemini-1.5-flash")

# =========================
# HÀM TIỆN ÍCH
# =========================
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Trang {i+1} ---\n{page_text}"
    return text


def call_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text


def ai_extract_criteria(hsmt_text):
    prompt = f"""
Bạn là chuyên gia đấu thầu.

Từ nội dung HSMT sau, hãy TRÍCH XUẤT ĐẦY ĐỦ các tiêu chí đánh giá HSDT.
Yêu cầu:
- Bám sát tuyệt đối HSMT
- Chia rõ: Kỹ thuật / Năng lực / Tài chính / Khác
- Mỗi tiêu chí gồm:
  - ten_tieu_chi
  - mo_ta
  - can_cu_hsmt

Trả về DẠNG GẠCH ĐẦU DÒNG, DỄ ĐỌC.
HSMT:
{hsmt_text}
"""
    return call_gemini(prompt)


def ai_evaluate(hsmt_criteria, hsdt_text):
    prompt = f"""
Bạn là tổ chuyên gia chấm thầu.

Căn cứ tiêu chí:
{hsmt_criteria}

Đánh giá HSDT sau:
{hsdt_text}

Yêu cầu:
- Đánh giá TỪNG tiêu chí
- Kết luận: ĐẠT / KHÔNG ĐẠT
- Nêu rõ căn cứ trích từ HSDT
- Viết đúng văn phong báo cáo tổ chuyên gia
"""
    return call_gemini(prompt)

# =========================
# GIAO DIỆN
# =========================
st.title("📊 HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA")

tabs = st.tabs([
    "1️⃣ Upload HSMT & HSDT",
    "2️⃣ Gán tiêu chí (AI)",
    "3️⃣ Chấm thầu"
])

# =========================
# TAB 1: UPLOAD
# =========================
with tabs[0]:
    st.subheader("📂 Upload hồ sơ")

    hsmt_files = st.file_uploader(
        "Upload HSMT (nhiều file PDF – cùng 1 bộ HSMT)",
        type=["pdf"],
        accept_multiple_files=True
    )

    hsdt_files = st.file_uploader(
        "Upload HSDT (nhiều file PDF – cùng 1 bộ HSDT)",
        type=["pdf"],
        accept_multiple_files=True
    )

    if hsmt_files:
        hsmt_text = ""
        for f in hsmt_files:
            hsmt_text += extract_text_from_pdf(f) + "\n\n"
        st.session_state.hsmt_text = hsmt_text
        st.success(f"✅ Đã đọc {len(hsmt_files)} file HSMT")

    if hsdt_files:
        hsdt_text = ""
        for f in hsdt_files:
            hsdt_text += extract_text_from_pdf(f) + "\n\n"
        st.session_state.hsdt_text = hsdt_text
        st.success(f"✅ Đã đọc {len(hsdt_files)} file HSDT")

# =========================
# TAB 2: GÁN TIÊU CHÍ
# =========================
with tabs[1]:
    st.subheader("🎯 Gán tiêu chí đánh giá theo HSMT")

    if "hsmt_text" not in st.session_state:
        st.warning("⚠️ Chưa có HSMT")
    else:
        if st.button("🤖 AI gợi ý tiêu chí từ HSMT"):
            criteria_text = ai_extract_criteria(st.session_state.hsmt_text)
            st.session_state.criteria_text = criteria_text
            st.success("✅ AI đã trích xuất tiêu chí")

        if "criteria_text" in st.session_state:
            st.text_area(
                "Danh sách tiêu chí (có thể chỉnh sửa)",
                st.session_state.criteria_text,
                height=400
            )

# =========================
# TAB 3: CHẤM THẦU
# =========================
with tabs[2]:
    st.subheader("🧠 Chấm thầu – Báo cáo tổ chuyên gia")

    if "criteria_text" not in st.session_state:
        st.warning("⚠️ Chưa có tiêu chí đánh giá")
    elif "hsdt_text" not in st.session_state:
        st.warning("⚠️ Chưa có HSDT")
    else:
        if st.button("⚖️ Thực hiện chấm thầu"):
            result = ai_evaluate(
                st.session_state.criteria_text,
                st.session_state.hsdt_text
            )
            st.success("✅ Chấm thầu hoàn tất")

            st.text_area(
                "📄 KẾT QUẢ CHẤM THẦU (chuẩn báo cáo tổ chuyên gia)",
                result,
                height=500
            )
