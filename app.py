import pdfplumber
from docx import Document
import io

def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def read_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs)

st.divider()
st.subheader("3️⃣ Nội dung trích xuất từ HSMT")

if hsmt_file:
    if hsmt_file.name.endswith(".pdf"):
        hsmt_text = read_pdf(hsmt_file)
    else:
        hsmt_text = read_docx(hsmt_file)

    st.text_area(
        "📄 Nội dung HSMT (đã trích xuất)",
        hsmt_text,
        height=400
    )
