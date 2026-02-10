import streamlit as st
import pdfplumber
import docx
import io
import os
from datetime import datetime
import google.generativeai as genai

# ================= CẤU HÌNH =================
st.set_page_config(
    page_title="HỆ THỐNG CHẤM THẦU CHUYÊN GIA",
    layout="wide"
)

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-pro")

# ================= HÀM TIỆN ÍCH =================
def read_files(files):
    text = ""
    for f in files:
        if f.name.lower().endswith(".pdf"):
            with pdfplumber.open(f) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        elif f.name.lower().endswith(".docx"):
            doc = docx.Document(f)
            for p in doc.paragraphs:
                text += p.text + "\n"
    return text.strip()

def ai_call(prompt):
    return model.generate_content(prompt).text

def export_word(content):
    doc = docx.Document()
    doc.add_heading("BÁO CÁO ĐÁNH GIÁ HỒ SƠ DỰ THẦU", level=1)

    doc.add_paragraph(
        "Căn cứ Luật Đấu thầu số 22/2023/QH15 và Thông tư 08/2022/TT-BKHĐT.\n"
    )

    table = doc.add_table(rows=2, cols=2)
    table.style = "Table Grid"
    table.cell(0, 0).text = "Nội dung"
    table.cell(0, 1).text = "Đánh giá"

    table.cell(1, 0).text = "Kết quả chấm thầu"
    table.cell(1, 1).text = content

    doc.add_paragraph(
        f"\nNgày lập báo cáo: {datetime.now().strftime('%d/%m/%Y')}\n"
        "TỔ CHUYÊN GIA ĐẤU THẦU"
    )

    path = "/tmp/bao_cao_cham_thau.docx"
    doc.save(path)
    return path

# ================= GIAO DIỆN =================
st.title("⚖️ HỆ THỐNG CHẤM THẦU CHUYÊN GIA")

st.markdown("### 📂 Upload HSMT (nhiều file)")
hsmt_files = st.file_uploader(
    "",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    key="hsmt"
)

st.markdown("### 📂 Upload HSDT (1 nhà thầu – nhiều file)")
hsdt_files = st.file_uploader(
    "",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    key="hsdt"
)

st.markdown("---")

# ================= CHẤM THẦU =================
if hsmt_files and hsdt_files:
    st.success("✅ Đã upload đầy đủ HSMT và HSDT")

    if st.button("⚖️ CHẤM THẦU", use_container_width=True):
        with st.spinner("AI đang chấm thầu theo Luật Đấu thầu & Thông tư 08..."):
            hsmt_text = read_files(hsmt_files)
            hsdt_text = read_files(hsdt_files)

            prompt = f"""
Bạn là TỔ CHUYÊN GIA ĐẤU THẦU.

Hãy đánh giá HỒ SƠ DỰ THẦU theo đúng quy định:
- Luật Đấu thầu Việt Nam
- Thông tư 08/2022/TT-BKHĐT
- Văn phong báo cáo thẩm định

YÊU CẦU:
1. Đánh giá sự đáp ứng HSDT so với HSMT
2. Nêu rõ các nội dung đạt / không đạt
3. Kết luận cuối cùng: ĐẠT hoặc KHÔNG ĐẠT
4. Trình bày mạch lạc, có thể dùng trực tiếp trong báo cáo

=== HSMT ===
{hsmt_text}

=== HSDT ===
{hsdt_text}
"""

            result = ai_call(prompt)

            st.markdown("## 📄 KẾT QUẢ CHẤM THẦU")
            st.text_area("", result, height=450)

            word_path = export_word(result)
            with open(word_path, "rb") as f:
                st.download_button(
                    "⬇️ TẢI BÁO CÁO WORD",
                    f,
                    file_name="Bao_cao_cham_thau.docx",
                    use_container_width=True
                )
else:
    st.info("⬆️ Vui lòng upload đầy đủ HSMT và HSDT để thực hiện chấm thầu")
