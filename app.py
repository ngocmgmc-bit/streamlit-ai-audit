import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from docx import Document

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Hệ thống chấm thầu – Tổ chuyên gia", layout="wide")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# FUNCTIONS
# =========================
def read_pdf(file):
    reader = PdfReader(file)
    return "\n".join([p.extract_text() or "" for p in reader.pages])

def read_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def read_file(file):
    if file.name.lower().endswith(".pdf"):
        return read_pdf(file)
    if file.name.lower().endswith(".docx"):
        return read_docx(file)
    return ""

def ai_extract_criteria(hsmt_text):
    prompt = f"""
    Bạn là TỔ CHUYÊN GIA ĐẤU THẦU.

    Từ nội dung HSMT sau, hãy:
    1. Trích xuất CÁC TIÊU CHÍ ĐÁNH GIÁ (đặc biệt Chương III)
    2. Mỗi tiêu chí gồm:
       - Tên tiêu chí
       - Yêu cầu cụ thể
       - Điều/mục/chương làm căn cứ

    Trả kết quả dạng DANH SÁCH GẠCH ĐẦU DÒNG.
    KHÔNG suy diễn ngoài HSMT.

    HSMT:
    ----------------
    {hsmt_text}
    """
    return model.generate_content(prompt).text

def ai_score_criterion(criterion, hsdt_text):
    prompt = f"""
    Bạn là TỔ CHUYÊN GIA CHẤM THẦU.

    TIÊU CHÍ:
    {criterion}

    HSDT:
    {hsdt_text}

    Hãy đánh giá:
    - Đạt / Không đạt
    - Trích dẫn nội dung HSDT làm căn cứ
    - Nhận xét ngắn gọn

    TUYỆT ĐỐI bám HSMT, không suy diễn.
    """
    return model.generate_content(prompt).text

# =========================
# SESSION STATE
# =========================
st.session_state.setdefault("hsmt_text", "")
st.session_state.setdefault("criteria", [])
st.session_state.setdefault("hsdt_text", "")

# =========================
# UI
# =========================
st.title("📑 HỆ THỐNG CHẤM THẦU – TỔ CHUYÊN GIA (AI HỖ TRỢ)")

tab1, tab2, tab3 = st.tabs(["1️⃣ Upload HSMT", "2️⃣ Gán tiêu chí (AI)", "3️⃣ Chấm thầu"])

# =========================
# TAB 1 – UPLOAD HSMT
# =========================
with tab1:
    st.header("Upload Hồ sơ mời thầu (HSMT)")
    hsmt_files = st.file_uploader(
        "Upload HSMT (PDF/DOCX – có thể nhiều file)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if hsmt_files:
        texts = []
        for f in hsmt_files:
            texts.append(f"\n===== FILE: {f.name} =====\n" + read_file(f))
        st.session_state.hsmt_text = "\n".join(texts)
        st.success("✅ Đã đọc HSMT")

# =========================
# TAB 2 – AI GỢI Ý TIÊU CHÍ
# =========================
with tab2:
    st.header("🔖 Gán tiêu chí đánh giá theo HSMT")

    if not st.session_state.hsmt_text:
        st.warning("⚠️ Cần upload HSMT trước")
    else:
        if st.button("🤖 AI gợi ý tiêu chí từ HSMT"):
            with st.spinner("AI đang rà soát HSMT..."):
                result = ai_extract_criteria(st.session_state.hsmt_text)
                st.session_state.criteria = result.split("\n")

        if st.session_state.criteria:
            st.markdown("### 📌 Danh sách tiêu chí (có thể chỉnh sửa)")
            for i, c in enumerate(st.session_state.criteria):
                st.session_state.criteria[i] = st.text_area(
                    f"Tiêu chí {i+1}", c, height=80
                )

# =========================
# TAB 3 – CHẤM THẦU
# =========================
with tab3:
    st.header("⚖️ Chấm thầu – Có căn cứ & AI hỗ trợ")

    hsdt_files = st.file_uploader(
        "Upload HSDT (PDF/DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True
    )

    if hsdt_files:
        texts = []
        for f in hsdt_files:
            texts.append(read_file(f))
        st.session_state.hsdt_text = "\n".join(texts)

    if not st.session_state.criteria:
        st.warning("⚠️ Chưa có tiêu chí")
    elif not st.session_state.hsdt_text:
        st.warning("⚠️ Chưa upload HSDT")
    else:
        if st.button("🧠 AI hỗ trợ chấm thầu"):
            for i, crit in enumerate(st.session_state.criteria):
                with st.expander(f"Tiêu chí {i+1}"):
                    with st.spinner("Đang đánh giá..."):
                        result = ai_score_criterion(crit, st.session_state.hsdt_text)
                        st.markdown(result)

st.caption("AI hỗ trợ phân tích – Quyết định cuối cùng thuộc Tổ chuyên gia")
