from pathlib import Path
from typing import Dict, List, Type

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.models.major import Major
from app.models.school import School
from app.models.employer import Employer
from app.models.student import Student
from app.models.job import Job
from app.models.system_metadata import SystemMetadata

# 如果你已经建了这个 ORM，就取消注释
from app.models.major_industry_mapping import MajorIndustryMapping


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "generated_data"


def normalize_value(value):
    """
    将 pandas 中的 NaN 转为 None，避免写库时报错。
    """
    if pd.isna(value):
        return None
    return value


def dataframe_to_records(df: pd.DataFrame) -> List[Dict]:
    """
    将 DataFrame 转成适合 SQLAlchemy bulk_insert_mappings 的 records。
    """
    records = []
    for _, row in df.iterrows():
        item = {col: normalize_value(row[col]) for col in df.columns}
        records.append(item)
    return records


def load_csv(file_name: str) -> pd.DataFrame:
    """
    读取 CSV 文件。
    """
    file_path = DATA_DIR / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    return pd.read_csv(file_path)


def clear_table(db, model):
    """
    清空目标表数据。
    """
    db.query(model).delete()
    db.commit()


def import_table(db, model: Type, file_name: str, clear_before_insert: bool = True):
    """
    导入单张表。
    """
    print(f"Importing {file_name} -> {model.__tablename__}")

    df = load_csv(file_name)
    records = dataframe_to_records(df)

    if clear_before_insert:
        db.query(model).delete()
        db.commit()

    if records:
        db.bulk_insert_mappings(model, records)
        db.commit()

    print(f"Imported {len(records)} rows into {model.__tablename__}")


def main():
    db = SessionLocal()

    try:
        # 1. 先导入基础维表
        import_table(db, Major, "majors.csv", clear_before_insert=True)
        import_table(db, School, "schools.csv", clear_before_insert=True)
        import_table(db, Employer, "employers.csv", clear_before_insert=True)
        import_table(db, Student, "students.csv", clear_before_insert=True)
        import_table(db, Job, "jobs.csv", clear_before_insert=True)

        # 2. 导入专业-行业映射表
        import_table(
            db,
            MajorIndustryMapping,
            "major_industry_mapping.csv",
            clear_before_insert=True,
        )

        print("All seed data imported successfully.")

    except FileNotFoundError as e:
        db.rollback()
        print(f"[File Error] {e}")
        raise
    except SQLAlchemyError as e:
        db.rollback()
        print(f"[Database Error] {e}")
        raise
    except Exception as e:
        db.rollback()
        print(f"[Unexpected Error] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()