import streamlit as st
import pdfplumber
from docx import Document
import io
import os

# =========================
# AI (OPTIONAL – KHÔNG BẮT BUỘC)
# =========================
USE_AI = False
try:
    import google.generativeai as genai
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel("gemini-pro")
        USE_AI = True
except:
    USE_AI = False

# =========================
# HÀM ĐỌC FILE
# =========================
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

def read_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

def read_file(file):
    name = file.name.lower()
    if name.endswith(".pdf"):
        return read_pdf(file)
    if name.endswith(".docx"):
        return read_docx(file)
    return ""

# =========================
# GIAO DIỆN
# =========================
st.set_page_config(page_title="AI Audit – Chấm thầu", layout="wide")

st.title("📑 HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA (AI HỖ TRỢ)")

tab1, tab2, tab3 = st.tabs([
    "1️⃣ Upload HSMT",
    "2️⃣ Gán tiêu chí (Chương III)",
    "3️⃣ CHẤM THẦU – CÓ CĂN CỨ"
])

# =========================
# TAB 1 – UPLOAD HSMT
# =========================
with tab1:
    st.header("📂 Upload Hồ sơ mời thầu (HSMT)")
    hsmt_files = st.file_uploader(
        "Chọn file HSMT (PDF / DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    hsmt_texts = {}
    if hsmt_files:
        for f in hsmt_files:
            text = read_file(f)
            hsmt_texts[f.name] = text

        st.success(f"Đã upload {len(hsmt_files)} file HSMT")

        st.subheader("📄 Nội dung HSMT (tách theo từng file)")
        selected = st.radio(
            "Chọn file HSMT",
            list(hsmt_texts.keys()),
            horizontal=True
        )
        st.text_area(
            f"Nội dung: {selected}",
            hsmt_texts[selected],
            height=400
        )

    st.session_state["hsmt_texts"] = hsmt_texts

# =========================
# TAB 2 – GÁN TIÊU CHÍ
# =========================
with tab2:
    st.header("🏷️ Gán tiêu chí đánh giá theo HSMT (Chương III)")

    if "hsmt_texts" not in st.session_state or not st.session_state["hsmt_texts"]:
        st.warning("⚠️ Cần upload HSMT trước")
    else:
        st.info("👉 Dán / chỉnh sửa tiêu chí đánh giá trích từ **Chương III – Tiêu chuẩn đánh giá**")

        criteria_text = st.text_area(
            "📌 Tiêu chí đánh giá (mỗi tiêu chí 1 dòng)",
            height=300,
            placeholder="""
Ví dụ:
- Có / Không đạt về năng lực
- Kinh nghiệm thực hiện hợp đồng tương tự
- Giải pháp kỹ thuật đáp ứng yêu cầu
- Nhân sự chủ chốt
- Thiết bị thi công
"""
        )

        criteria = [c.strip() for c in criteria_text.split("\n") if c.strip()]
        st.session_state["criteria"] = criteria

        if criteria:
            st.success(f"Đã ghi nhận {len(criteria)} tiêu chí")

# =========================
# TAB 3 – CHẤM THẦU
# =========================
with tab3:
    st.header("⚖️ CHẤM THẦU – CÓ CĂN CỨ & AI HỖ TRỢ")

    hsdt_files = st.file_uploader(
        "📂 Upload Hồ sơ dự thầu (HSDT)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if not hsdt_files:
        st.warning("⚠️ Cần upload HSDT")
        st.stop()

    if "criteria" not in st.session_state or not st.session_state["criteria"]:
        st.warning("⚠️ Chưa có tiêu chí đánh giá")
        st.stop()

    # Đọc HSDT
    hsdt_texts = {}
    for f in hsdt_files:
        hsdt_texts[f.name] = read_file(f)

    st.success(f"Đã upload {len(hsdt_files)} HSDT")

    st.subheader("📊 BẢNG CHẤM THẦU (MÔ PHỎNG TỔ CHUYÊN GIA)")

    for hsdt_name, hsdt_text in hsdt_texts.items():
        st.markdown(f"## 📁 HSDT: {hsdt_name}")

        for idx, criterion in enumerate(st.session_state["criteria"], start=1):
            with st.expander(f"Tiêu chí {idx}: {criterion}", expanded=True):
                col1, col2 = st.columns([1, 2])

                with col1:
                    result = st.radio(
                        "Kết quả",
                        ["Đạt", "Không đạt"],
                        key=f"{hsdt_name}_{idx}"
                    )

                with col2:
                    evidence = st.text_area(
                        "📌 Căn cứ (trích dẫn HSDT)",
                        height=120,
                        key=f"ev_{hsdt_name}_{idx}"
                    )

                if USE_AI and hsdt_text:
                    if st.button("🤖 AI gợi ý căn cứ", key=f"ai_{hsdt_name}_{idx}"):
                        prompt = f"""
Bạn là tổ chuyên gia chấm thầu.
Tiêu chí: {criterion}

HSDT:
{hsdt_text[:4000]}

Hãy gợi ý đoạn căn cứ phù hợp (KHÔNG kết luận đạt hay không đạt).
"""
                        try:
                            resp = model.generate_content(prompt)
                            st.info(resp.text)
                        except:
                            st.warning("AI không phản hồi")

    st.success("✅ Hoàn tất bước chấm thầu (theo đúng quy trình tổ chuyên gia)")

# =========================
# GHI CHÚ
# =========================
st.caption(
    "⚠️ AI chỉ hỗ trợ đọc hiểu – gợi ý ngữ nghĩa. "
    "Quyết định chấm thầu do TỔ CHUYÊN GIA chịu trách nhiệm."
)
                    st.markdown("**🧠 Kết quả AI:**")
                    st.markdown(textwrap.indent(ai_result, "> "))
