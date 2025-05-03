from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .db import Base


# Модели для SQLAlchemy, которые будут использоваться в Alembic
class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("sections.id"), nullable=True)

    children = relationship("Section", backref="parent", remote_side=[id])
    templates = relationship("Template", back_populates="section")


class Template(Base):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    file_path = Column(String, nullable=False)

    section_id = Column(Integer, ForeignKey("sections.id"))
    section = relationship("Section", back_populates="templates")


class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)

    parameters = relationship(
        "Parameter", back_populates="case", cascade="all, delete"
    )


class Parameter(Base):
    __tablename__ = "parameters"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, index=True)
    value = Column(Text)

    case_id = Column(Integer, ForeignKey("cases.id"))
    case = relationship("Case", back_populates="parameters")
