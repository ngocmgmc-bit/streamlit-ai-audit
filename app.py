import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# ======================
# 1. CẤU HÌNH CHUNG
# ======================
st.set_page_config(page_title="AI Chấm thầu HSMT/HSDT", layout="wide")

genai.configure(api_key=st.secrets.get("GEMINI_API_KEY", ""))

MODEL_NAME = "models/gemini-1.5-flash"

# ======================
# 2. HÀM DÙNG CHUNG
# ======================
def read_pdf_text(uploaded_files):
    full_text = ""
    for f in uploaded_files:
        reader = PdfReader(f)
        for page in reader.pages:
            if page.extract_text():
                full_text += page.extract_text() + "\n"
    return full_text.strip()


def call_gemini(prompt):
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text


# ======================
# 3. AI GỢI Ý TIÊU CHÍ
# ======================
def ai_extract_criteria(hsmt_text):
    prompt = f"""
Bạn là chuyên gia đấu thầu.

Từ nội dung HSMT dưới đây, hãy TRÍCH XUẤT các TIÊU CHÍ ĐÁNH GIÁ
theo đúng tinh thần tổ chuyên gia.

YÊU CẦU:
- Chỉ trích tiêu chí CÓ TRONG HSMT
- Mỗi tiêu chí gồm:
  1. Tên tiêu chí
  2. Mô tả/yêu cầu
  3. Căn cứ HSMT (chương/mục/điều)

Trình bày dạng danh sách đánh số rõ ràng.

HSMT:
\"\"\"{hsmt_text}\"\"\"
"""
    return call_gemini(prompt)


# ======================
# 4. AI CHẤM THẦU
# ======================
def ai_evaluate_bid(criteria, hsdt_text):
    prompt = f"""
Bạn là tổ chuyên gia đấu thầu.

Dựa trên:
- TIÊU CHÍ ĐÁNH GIÁ đã được phê duyệt
- HỒ SƠ DỰ THẦU của nhà thầu

Hãy đánh giá TỪNG TIÊU CHÍ theo mẫu:
- Đạt / Không đạt
- Nhận xét ngắn gọn
- Trích dẫn căn cứ từ HSDT

TIÊU CHÍ:
{criteria}

HỒ SƠ DỰ THẦU:
\"\"\"{hsdt_text}\"\"\"
"""
    return call_gemini(prompt)


# ======================
# 5. GIAO DIỆN APP
# ======================
st.title("📑 Hệ thống AI hỗ trợ chấm thầu")

tabs = st.tabs(["1️⃣ Upload HSMT", "2️⃣ Gán tiêu chí (AI)", "3️⃣ Chấm thầu"])

# ----------------------
# TAB 1: UPLOAD HSMT
# ----------------------
with tabs[0]:
    st.header("📤 Upload Hồ sơ mời thầu (HSMT)")
    hsmt_files = st.file_uploader(
        "Chọn file PDF HSMT (có thể nhiều file)",
        type=["pdf"],
        accept_multiple_files=True
    )

    if hsmt_files:
        st.session_state.hsmt_text = read_pdf_text(hsmt_files)
        st.success("✅ Đã đọc HSMT thành công")
        with st.expander("Xem trước nội dung HSMT"):
            st.text(st.session_state.hsmt_text[:5000])


# ----------------------
# TAB 2: GÁN TIÊU CHÍ
# ----------------------
with tabs[1]:
    st.header("🏷️ Gán tiêu chí đánh giá theo HSMT")

    if "hsmt_text" not in st.session_state:
        st.warning("⚠️ Vui lòng upload HSMT trước")
    else:
        if st.button("🤖 AI gợi ý tiêu chí từ HSMT"):
            with st.spinner("AI đang phân tích HSMT..."):
                criteria_text = ai_extract_criteria(st.session_state.hsmt_text)
                st.session_state.criteria = criteria_text

        if "criteria" in st.session_state:
            st.subheader("📌 Danh sách tiêu chí (có thể chỉnh sửa)")
            criteria_edit = st.text_area(
                "Tiêu chí đánh giá",
                st.session_state.criteria,
                height=400
            )
            st.session_state.criteria = criteria_edit
            st.success("✅ Tiêu chí đã sẵn sàng cho chấm thầu")


# ----------------------
# TAB 3: CHẤM THẦU
# ----------------------
with tabs[2]:
    st.header("⚖️ Chấm thầu theo tiêu chí")

    if "criteria" not in st.session_state:
        st.warning("⚠️ Chưa có tiêu chí đánh giá")
    else:
        hsdt_files = st.file_uploader(
            "Upload HỒ SƠ DỰ THẦU (HSDT)",
            type=["pdf"],
            accept_multiple_files=True,
            key="hsdt"
        )

        if hsdt_files:
            hsdt_text = read_pdf_text(hsdt_files)

            if st.button("🧠 AI chấm thầu"):
                with st.spinner("AI đang chấm thầu theo từng tiêu chí..."):
                    result = ai_evaluate_bid(
                        st.session_state.criteria,
                        hsdt_text
                    )
                    st.subheader("📊 KẾT QUẢ CHẤM THẦU")
                    st.text_area("Báo cáo chấm thầu", result, height=500)

                    st.info(
                        "📌 Lưu ý: Kết quả là trợ lý phân tích. "
                        "Tổ chuyên gia chịu trách nhiệm phê duyệt cuối cùng."
                    )
