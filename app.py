import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
import google.generativeai as genai
import textwrap

# =========================
# CONFIG AI
# =========================
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# PAGE
# =========================
st.set_page_config(page_title="AI Audit – Chấm thầu", layout="wide")
st.title("📑 HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA (AI HỖ TRỢ)")

# =========================
# HÀM ĐỌC FILE
# =========================
def extract_text(file):
    if file.name.lower().endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    elif file.name.lower().endswith(".docx"):
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs)
    return ""

# =========================
# SESSION STATE
# =========================
for key in ["hsmt_files", "criteria", "hsdt_files"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key != "criteria" else []

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs([
    "1️⃣ Upload HSMT",
    "2️⃣ Gán tiêu chí (Chương III)",
    "3️⃣ CHẤM THẦU + CĂN CỨ + AI"
])

# =========================
# TAB 1 – HSMT
# =========================
with tab1:
    st.header("📘 Upload Hồ sơ mời thầu (HSMT)")

    files = st.file_uploader(
        "Upload HSMT (PDF/DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if files:
        for f in files:
            if f.name not in st.session_state.hsmt_files:
                st.session_state.hsmt_files[f.name] = extract_text(f)

    if st.session_state.hsmt_files:
        f = st.selectbox("Xem file HSMT", st.session_state.hsmt_files.keys())
        st.text_area("Nội dung HSMT", st.session_state.hsmt_files[f], height=350)

# =========================
# TAB 2 – TIÊU CHÍ
# =========================
with tab2:
    st.header("📌 Gán tiêu chí đánh giá theo Chương III")

    with st.form("criteria_form"):
        col1, col2 = st.columns(2)
        with col1:
            group = st.selectbox(
                "Nhóm tiêu chí",
                [
                    "I. Điều kiện hợp lệ",
                    "II. Năng lực & kinh nghiệm",
                    "III. Yêu cầu kỹ thuật",
                    "IV. Nhân sự",
                    "V. Thiết bị",
                    "VI. Điều kiện hợp đồng"
                ]
            )
            name = st.text_input("Tên tiêu chí")

        with col2:
            required = st.selectbox(
                "Loại tiêu chí",
                ["BẮT BUỘC (Đạt/Không đạt)", "KHÔNG BẮT BUỘC"]
            )

        description = st.text_area("Mô tả yêu cầu (trích đúng HSMT)")

        add = st.form_submit_button("➕ Thêm tiêu chí")

        if add and name.strip():
            st.session_state.criteria.append({
                "group": group,
                "name": name,
                "description": description,
                "required": required
            })

    if st.session_state.criteria:
        st.dataframe(pd.DataFrame(st.session_state.criteria), use_container_width=True)

# =========================
# AI HÀM CHẤM
# =========================
def ai_evaluate(criterion, description, hsdt_text):
    prompt = f"""
Bạn là tổ chuyên gia đấu thầu.

TIÊU CHÍ (trích từ HSMT):
{criterion}

MÔ TẢ YÊU CẦU:
{description}

NỘI DUNG HSDT:
{hsdt_text[:12000]}

YÊU CẦU:
1. Kết luận: ĐẠT hoặc KHÔNG ĐẠT
2. Trích đúng đoạn HSDT làm căn cứ
3. Giải thích ngắn gọn, tuyệt đối bám HSMT
"""

    response = model.generate_content(prompt)
    return response.text

# =========================
# TAB 3 – CHẤM THẦU
# =========================
with tab3:
    st.header("🧾 CHẤM THẦU – CÓ CĂN CỨ & AI")

    hsdt_uploads = st.file_uploader(
        "Upload HSDT (PDF/DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if hsdt_uploads:
        for f in hsdt_uploads:
            st.session_state.hsdt_files[f.name] = extract_text(f)

    if not st.session_state.criteria or not st.session_state.hsdt_files:
        st.warning("⚠️ Cần tiêu chí và HSDT để chấm thầu")
    else:
        for bidder, hsdt_text in st.session_state.hsdt_files.items():
            st.subheader(f"🏢 Nhà thầu: {bidder}")

            for c in st.session_state.criteria:
                with st.expander(f"{c['group']} – {c['name']}"):
                    with st.spinner("AI đang phân tích…"):
                        ai_result = ai_evaluate(
                            c["name"],
                            c["description"],
                            hsdt_text
                        )

                    st.markdown("**🧠 Kết quả AI:**")
                    st.markdown(textwrap.indent(ai_result, "> "))
