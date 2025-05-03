import os
import sys
from app.db import SessionLocal, Base, engine
from app.models import Section, Template
# добавляем в sys.path саму папку backend, чтобы Python увидел пакет app
sys.path.append(os.path.dirname(__file__))


# создаём все таблицы (если их ещё нет)
Base.metadata.create_all(bind=engine)

# папка с вашими .doc/.docx
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates_files")


def main():
    db = SessionLocal()

    # 1) убедимся, что раздел "Основные" существует
    sec = db.query(Section).filter_by(name="Основные").first()
    if not sec:
        sec = Section(name="Основные", parent_id=None)
        db.add(sec)
        db.commit()
        db.refresh(sec)
    print(f"Используем раздел: {sec.id} — {sec.name}")

    # 2) пробежимся по файлам и зарегистрируем те, которых нет
    for fname in os.listdir(TEMPLATES_DIR):
        if not fname.lower().endswith((".doc", ".docx")):
            continue
        full_path = os.path.join(TEMPLATES_DIR, fname)
        exists = db.query(Template).filter_by(file_path=full_path).first()
        if exists:
            continue
        tmpl = Template(
            name=os.path.splitext(fname)[0],
            file_path=full_path,
            section_id=sec.id
        )
        db.add(tmpl)
        print(f"Добавляем шаблон: {fname}")

    db.commit()
    db.close()
    print("✅ Все шаблоны зарегистрированы.")


if __name__ == "__main__":
    main()
