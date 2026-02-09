import streamlit as st
import os
import json

# ================== AI SETUP (SAFE) ==================
USE_AI = True
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    MODEL = genai.GenerativeModel("models/gemini-1.5-flash")
except Exception:
    USE_AI = False
    MODEL = None


def call_ai(prompt: str) -> str:
    if not USE_AI:
        return ""
    try:
        return MODEL.generate_content(prompt).text
    except Exception:
        return ""


# ================== AI LOGIC ==================
def ai_extract_criteria(hsmt_text: str):
    prompt = f"""
Bạn là TỔ CHUYÊN GIA ĐẤU THẦU.

Nhiệm vụ:
- Đọc HSMT
- Trích xuất TOÀN BỘ tiêu chí đánh giá
- Mỗi tiêu chí gồm:
  + ten_tieu_chi
  + mo_ta
  + can_cu (điều/chương/mục trong HSMT)

Xuất JSON thuần, KHÔNG giải thích.

HSMT:
{hsmt_text}
"""
    text = call_ai(prompt)

    if not text:
        return []

    try:
        json_text = text[text.find("["): text.rfind("]")+1]
        return json.loads(json_text)
    except Exception:
        return []


def ai_score_bid(criteria, hsdt_text):
    prompt = f"""
Bạn là TỔ CHUYÊN GIA CHẤM THẦU.

Nguyên tắc:
- TUÂN THỦ TUYỆT ĐỐI HSMT
- KHÔNG suy diễn
- Nếu không đáp ứng → Không đạt

Tiêu chí:
{json.dumps(criteria, ensure_ascii=False)}

HSDT:
{hsdt_text}

Xuất bảng JSON:
[
  {{
    "ten_tieu_chi": "",
    "ket_qua": "Đạt/Không đạt",
    "nhan_xet": "",
    "can_cu": ""
  }}
]
"""
    text = call_ai(prompt)
    if not text:
        return []

    try:
        json_text = text[text.find("["): text.rfind("]")+1]
        return json.loads(json_text)
    except Exception:
        return []


# ================== UI ==================
st.set_page_config(page_title="AI Chấm thầu HSMT", layout="wide")

st.title("📊 HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA")

tab1, tab2, tab3 = st.tabs([
    "1️⃣ Upload HSMT & HSDT",
    "2️⃣ Gán tiêu chí (AI)",
    "3️⃣ Chấm thầu"
])

# ---------- TAB 1 ----------
with tab1:
    st.subheader("Upload hồ sơ")

    hsmt = st.text_area("📘 Nội dung HSMT", height=250)
    hsdt = st.text_area("📕 Nội dung HSDT", height=250)

    if hsmt:
        st.session_state.hsmt_text = hsmt
    if hsdt:
        st.session_state.hsdt_text = hsdt

# ---------- TAB 2 ----------
with tab2:
    st.subheader("🎯 Gán tiêu chí đánh giá theo HSMT")

    if "hsmt_text" not in st.session_state:
        st.warning("⚠️ Chưa có HSMT")
    else:
        if st.button("🤖 AI gợi ý tiêu chí từ HSMT"):
            with st.spinner("AI đang rà soát HSMT..."):
                criteria = ai_extract_criteria(st.session_state.hsmt_text)

            if not criteria:
                st.error("❌ AI không trích xuất được – kiểm tra API Key hoặc HSMT")
            else:
                st.session_state.criteria = criteria
                st.success(f"✅ Đã trích xuất {len(criteria)} tiêu chí")

        if "criteria" in st.session_state:
            for i, c in enumerate(st.session_state.criteria, 1):
                with st.expander(f"Tiêu chí {i}: {c.get('ten_tieu_chi','')}"):
                    st.text_area("Mô tả", c.get("mo_ta",""), height=80)
                    st.text_area("Căn cứ HSMT", c.get("can_cu",""), height=60)

# ---------- TAB 3 ----------
with tab3:
    st.subheader("⚖️ Chấm thầu – Tổ chuyên gia")

    if "criteria" not in st.session_state or "hsdt_text" not in st.session_state:
        st.warning("⚠️ Thiếu tiêu chí hoặc HSDT")
    else:
        if st.button("🧠 AI hỗ trợ chấm thầu"):
            with st.spinner("AI đang chấm thầu theo HSMT..."):
                result = ai_score_bid(
                    st.session_state.criteria,
                    st.session_state.hsdt_text
                )

            if not result:
                st.error("❌ AI không trả kết quả")
            else:
                st.success("✅ Chấm thầu hoàn tất")
                for r in result:
                    with st.expander(r["ten_tieu_chi"]):
                        st.write(f"**Kết quả:** {r['ket_qua']}")
                        st.write(f"**Nhận xét:** {r['nhan_xet']}")
                        st.write(f"**Căn cứ:** {r['can_cu']}")

st.caption("⚠️ AI chỉ hỗ trợ – Quyết định cuối cùng thuộc Tổ chuyên gia")
