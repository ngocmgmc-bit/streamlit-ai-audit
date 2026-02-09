import streamlit as st
import os
import json
import google.generativeai as genai
from PyPDF2 import PdfReader

# ======================
# CẤU HÌNH CHUNG
# ======================
st.set_page_config(page_title="Hệ thống chấm thầu – Tổ chuyên gia", layout="wide")

if "GOOGLE_API_KEY" not in os.environ:
    st.error("❌ Chưa cấu hình GOOGLE_API_KEY trong biến môi trường")
    st.stop()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# ======================
# HÀM DÙNG CHUNG
# ======================
def read_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for p in reader.pages:
        text += p.extract_text() or ""
    return text


def call_gemini_json(prompt):
    response = model.generate_content(prompt)
    raw = response.text.strip()

    # loại bỏ ```json nếu có
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except Exception as e:
        st.error("❌ AI không trả về JSON hợp lệ")
        st.code(raw)
        raise e


# ======================
# AI TRÍCH TIÊU CHÍ TỪ HSMT
# ======================
def ai_extract_criteria(hsmt_text):
    prompt = f"""
Bạn là TỔ CHUYÊN GIA ĐẤU THẦU theo Luật Đấu thầu Việt Nam.

Nhiệm vụ:
- Đọc HSMT bên dưới
- Trích xuất TOÀN BỘ tiêu chí đánh giá HSDT
- Mỗi tiêu chí phải có:
  + ten_tieu_chi
  + loai (đạt/không đạt | chấm điểm)
  + can_cu (mục/chương trong HSMT)
  + mo_ta

YÊU CẦU BẮT BUỘC:
- Chỉ trả về JSON
- Dạng danh sách (list)
- Không thêm lời giải thích

HSMT:
\"\"\"{hsmt_text[:12000]}\"\"\"
"""
    return call_gemini_json(prompt)


# ======================
# AI CHẤM THẦU
# ======================
def ai_score_bid(criteria, hsdt_text):
    prompt = f"""
Bạn là TỔ CHUYÊN GIA CHẤM THẦU.

Tiêu chí đánh giá (JSON):
{json.dumps(criteria, ensure_ascii=False)}

Hồ sơ dự thầu:
\"\"\"{hsdt_text[:12000]}\"\"\"

Nhiệm vụ:
- Đánh giá từng tiêu chí
- Trả kết quả JSON với:
  + ten_tieu_chi
  + ket_qua (Đạt / Không đạt / Điểm số)
  + nhan_xet
  + trich_dan_tu_HSDT

Chỉ trả JSON, không giải thích.
"""
    return call_gemini_json(prompt)


# ======================
# GIAO DIỆN
# ======================
st.title("📊 HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA")

tab1, tab2, tab3 = st.tabs(["1️⃣ Upload HSMT & HSDT", "2️⃣ Gán tiêu chí (AI)", "3️⃣ Chấm thầu"])


# ======================
# TAB 1: UPLOAD
# ======================
with tab1:
    st.subheader("📤 Upload hồ sơ")

    hsmt_file = st.file_uploader("Upload HSMT (PDF)", type=["pdf"])
    hsdt_file = st.file_uploader("Upload HSDT (PDF)", type=["pdf"])

    if hsmt_file:
        st.session_state.hsmt_text = read_pdf(hsmt_file)
        st.success("✅ Đã đọc HSMT")

    if hsdt_file:
        st.session_state.hsdt_text = read_pdf(hsdt_file)
        st.success("✅ Đã đọc HSDT")


# ======================
# TAB 2: GÁN TIÊU CHÍ
# ======================
with tab2:
    st.subheader("🎯 Gán tiêu chí đánh giá theo HSMT")

    if "hsmt_text" not in st.session_state:
        st.warning("⚠️ Cần upload HSMT trước")
    else:
        if st.button("🤖 AI gợi ý tiêu chí từ HSMT"):
            with st.spinner("AI đang phân tích HSMT..."):
                st.session_state.criteria = ai_extract_criteria(st.session_state.hsmt_text)
                st.success("✅ Đã trích xuất tiêu chí")

        if "criteria" in st.session_state:
            for i, c in enumerate(st.session_state.criteria, 1):
                with st.expander(f"Tiêu chí {i}: {c.get('ten_tieu_chi','')}"):
                    st.write("**Loại:**", c.get("loai"))
                    st.write("**Căn cứ:**", c.get("can_cu"))
                    st.write("**Mô tả:**", c.get("mo_ta"))


# ======================
# TAB 3: CHẤM THẦU
# ======================
with tab3:
    st.subheader("🧮 Chấm thầu theo tiêu chí")

    if "criteria" not in st.session_state or "hsdt_text" not in st.session_state:
        st.warning("⚠️ Cần có tiêu chí và HSDT")
    else:
        if st.button("⚖️ Chấm thầu"):
            with st.spinner("AI đang chấm thầu..."):
                result = ai_score_bid(
                    st.session_state.criteria,
                    st.session_state.hsdt_text
                )
                st.session_state.result = result
                st.success("✅ Hoàn thành chấm thầu")

        if "result" in st.session_state:
            for r in st.session_state.result:
                with st.expander(f"{r.get('ten_tieu_chi','')} – {r.get('ket_qua','')}"):
                    st.write("**Nhận xét:**", r.get("nhan_xet"))
                    st.write("**Trích dẫn HSDT:**", r.get("trich_dan_tu_HSDT"))
