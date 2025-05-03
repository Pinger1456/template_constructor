import os
from fastapi import HTTPException
from docxtpl import DocxTemplate
from io import BytesIO

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates_files")
os.makedirs(TEMPLATES_DIR, exist_ok=True)


def save_upload_file(upload_file, destination: str) -> None:
    """
    Сохраняет загруженный файл в указанное место.
    """
    try:
        with open(destination, "wb") as buffer:
            buffer.write(upload_file.file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")


def render_docx(template_path: str, context: dict) -> bytes:
    """
    Отрисовывает .docx-шаблон с помощью docxtpl.
    Возвращает байты готового документа.
    """
    doc = DocxTemplate(template_path)
    try:
        doc.render(context)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Template rendering error: {e}")
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()


def get_template_variables(template_path: str) -> set:
    """
    Возвращает набор имён всех {{variables}} в данном .docx-шаблоне.
    """
    doc = DocxTemplate(template_path)
    return doc.get_undeclared_template_variables()
