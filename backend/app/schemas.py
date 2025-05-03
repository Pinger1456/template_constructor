from typing import List, Optional, Dict
from pydantic import BaseModel

# --- Section ---

class SectionBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

class SectionCreate(SectionBase):
    pass

class SectionRead(SectionBase):
    id: int
    class Config:
        orm_mode = True

# --- Template ---

class TemplateBase(BaseModel):
    name: str
    section_id: int

class TemplateCreate(TemplateBase):
    pass  # файл загружается через UploadFile

class TemplateRead(TemplateBase):
    id: int
    file_path: str
    class Config:
        orm_mode = True

# --- Case & Parameter ---

class ParameterBase(BaseModel):
    key: str
    value: str

class ParameterCreate(ParameterBase):
    pass

class ParameterRead(ParameterBase):
    id: int
    class Config:
        orm_mode = True

class CaseBase(BaseModel):
    title: str

class CaseCreate(CaseBase):
    parameters: List[ParameterCreate] = []

class CaseRead(CaseBase):
    id: int
    parameters: List[ParameterRead] = []
    class Config:
        orm_mode = True

# --- Generation ---

class GenerateRequest(BaseModel):
    template_id: int
    case_id: int

class AdhocGenerateRequest(BaseModel):
    template_id: int
    context: Dict[str, str]
