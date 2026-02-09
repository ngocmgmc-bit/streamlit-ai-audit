import os
import streamlit as st
import google.generativeai as genai
import pdfplumber

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Hệ thống chấm thầu – Tổ chuyên gia",
    layout="wide"
)

# =========================
# CHECK API KEY
# =========================
if "GOOGLE_API_KEY" not in os.environ:
    st.error("❌ Chưa cấu hình GOOGLE_API_KEY trong biến môi trường")
    st.stop()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-pro")

# =========================
# UTILS
# =========================
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def ai_extract_criteria(hsmt_text: str) -> list:
    prompt = f"""
Bạn là chuyên gia đấu thầu.
Từ nội dung HSMT sau, hãy trích xuất DANH SÁCH TIÊU CHÍ ĐÁNH GIÁ.

YÊU CẦU:
- Trả về danh sách
- Mỗi tiêu chí gồm:
  - ten_tieu_chi
  - loai (Kỹ thuật / Năng lực / Tài chính / Pháp lý)
  - mo_ta_ngan
  - bat_buoc (true/false)

TRẢ VỀ DẠNG JSON LIST, KHÔNG GIẢI THÍCH.

HSMT:
\"\"\"
{hsmt_text[:12000]}
\"\"\"
"""
    response = model.generate_content(prompt)
    return response.text


# =========================
# SESSION STATE
# =========================
if "hsmt_text" not in st.session_state:
    st.session_state.hsmt_text = ""

if "criteria" not in st.session_state:
    st.session_state.criteria = []

# =========================
# UI
# =========================
st.title("📊 HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA")

tabs = st.tabs([
    "📤 Upload HSMT & HSDT",
    "🎯 Gắn tiêu chí (AI)",
    "📑 Chấm thầu"
])

# =========================
# TAB 1: UPLOAD
# =========================
with tabs[0]:
    st.subheader("📤 Upload hồ sơ")

    hsmt_file = st.file_uploader("Upload HSMT (PDF)", type=["pdf"])
    if hsmt_file:
        st.session_state.hsmt_text = extract_text_from_pdf(hsmt_file)
        st.success("✅ Đã đọc nội dung HSMT")

    hsdt_file = st.file_uploader("Upload HSDT (PDF)", type=["pdf"])
    if hsdt_file:
        st.info("📌 HSDT sẽ dùng ở bước chấm thầu")

# =========================
# TAB 2: AI GỢI Ý TIÊU CHÍ
# =========================
with tabs[1]:
    st.subheader("🎯 Gắn tiêu chí đánh giá theo HSMT")

    if not st.session_state.hsmt_text:
        st.warning("⚠️ Chưa upload HSMT")
    else:
        if st.button("🤖 AI gợi ý tiêu chí từ HSMT"):
            with st.spinner("AI đang phân tích HSMT..."):
                raw = ai_extract_criteria(st.session_state.hsmt_text)

                try:
                    import json
                    st.session_state.criteria = json.loads(raw)
                    st.success("✅ AI đã trích xuất tiêu chí")
                except Exception:
                    st.error("❌ AI trả về sai định dạng JSON")
                    st.code(raw)

        if st.session_state.criteria:
            for i, c in enumerate(st.session_state.criteria, start=1):
                # FIX LỖI: đảm bảo c là dict
                if not isinstance(c, dict):
                    continue

                title = c.get("ten_tieu_chi", f"Tiêu chí {i}")
                with st.expander(f"{i}. {title}"):
                    st.markdown(f"**Loại:** {c.get('loai','')}")
                    st.markdown(f"**Mô tả:** {c.get('mo_ta_ngan','')}")
                    st.markdown(f"**Bắt buộc:** {c.get('bat_buoc', False)}")

# =========================
# TAB 3: CHẤM THẦU
# =========================
with tabs[2]:
    st.subheader("📑 Chấm thầu")

    if not st.session_state.criteria:
        st.warning("⚠️ Chưa có tiêu chí để chấm thầu")
    else:
        st.success(f"✅ Sẵn sàng chấm thầu với {len(st.session_state.criteria)} tiêu chí")
        st.info("👉 Bước tiếp theo: so khớp HSDT với từng tiêu chí (sẽ triển khai tiếp)")
