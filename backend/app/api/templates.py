from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import os
from urllib.parse import quote

from .. import models, schemas, utils
from ..db import get_db
from ..schemas import AdhocGenerateRequest

router = APIRouter(prefix="/api")

# --- Sections ---

@router.post("/sections/", response_model=schemas.SectionRead)
def create_section(section: schemas.SectionCreate, db: Session = Depends(get_db)):
    db_section = models.Section(**section.dict())
    db.add(db_section)
    db.commit()
    db.refresh(db_section)
    return db_section

@router.get("/sections/", response_model=list[schemas.SectionRead])
def list_sections(db: Session = Depends(get_db)):
    return db.query(models.Section).all()

# --- Templates upload/list ---

@router.post("/templates/", response_model=schemas.TemplateRead)
def upload_template(
    name: str,
    section_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    section = db.get(models.Section, section_id)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    filename = f"{section_id}_{file.filename}"
    dest = os.path.join(utils.TEMPLATES_DIR, filename)
    utils.save_upload_file(file, dest)

    db_template = models.Template(name=name, section_id=section_id, file_path=dest)
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/sections/{section_id}/templates", response_model=list[schemas.TemplateRead])
def list_templates(section_id: int, db: Session = Depends(get_db)):
    return db.query(models.Template).filter_by(section_id=section_id).all()

# --- Flat list of templates & variables introspection ---

@router.get("/templates/", response_model=list[schemas.TemplateRead])
def list_all_templates(db: Session = Depends(get_db)):
    return db.query(models.Template).all()

@router.get("/templates/{template_id}/variables")
def get_template_variables(template_id: int, db: Session = Depends(get_db)):
    template = db.get(models.Template, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    vars = utils.get_template_variables(template.file_path)
    return {"variables": list(vars)}

# --- Generation endpoints ---

@router.post("/generate")
def generate(req: schemas.GenerateRequest, db: Session = Depends(get_db)):
    template = db.get(models.Template, req.template_id)
    case = db.get(models.Case, req.case_id)
    if not template or not case:
        raise HTTPException(status_code=404, detail="Template or Case not found")
    context = {p.key: p.value for p in case.parameters}
    doc_bytes = utils.render_docx(template.file_path, context)
    return StreamingResponse(
        iter([doc_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={template.name}.docx"},
    )


@router.post("/generate-adhoc")
def generate_adhoc(req: AdhocGenerateRequest, db: Session = Depends(get_db)):
    template = db.get(models.Template, req.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Генерим документ
    doc_bytes = utils.render_docx(template.file_path, req.context)

    # Кодируем имя файла в ASCII-процентном виде
    filename = f"{template.name}.docx"
    filename_quoted = quote(filename)  # кодирует UTF-8 → %XX

    headers = {
        # RFC5987: filename* указывает кодировку и url-encoded имя
        "Content-Disposition": f"attachment; filename*=UTF-8''{filename_quoted}"
    }

    return StreamingResponse(
        iter([doc_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )

# --- Cases CRUD (осталось без изменений) ---

@router.post("/cases/", response_model=schemas.CaseRead)
def create_case(case_in: schemas.CaseCreate, db: Session = Depends(get_db)):
    case = models.Case(title=case_in.title)
    db.add(case)
    db.commit()
    for param in case_in.parameters:
        db_param = models.Parameter(case_id=case.id, **param.dict())
        db.add(db_param)
    db.commit()
    db.refresh(case)
    return case

@router.get("/cases/", response_model=list[schemas.CaseRead])
def list_cases(db: Session = Depends(get_db)):
    return db.query(models.Case).all()

@router.get("/cases/{case_id}", response_model=schemas.CaseRead)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.get(models.Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.put("/cases/{case_id}", response_model=schemas.CaseRead)
def update_case(case_id: int, case_in: schemas.CaseCreate, db: Session = Depends(get_db)):
    case = db.get(models.Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.title = case_in.title
    db.query(models.Parameter).filter_by(case_id=case_id).delete()
    for p in case_in.parameters:
        db.add(models.Parameter(case_id=case_id, **p.dict()))
    db.commit()
    db.refresh(case)
    return case

@router.delete("/cases/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db)):
    case = db.get(models.Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    db.delete(case)
    db.commit()
    return {"detail": "Deleted"}
