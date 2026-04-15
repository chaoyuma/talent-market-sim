from app.core.database import SessionLocal
from app.models.system_metadata import SystemMetadata


def main():
    db = SessionLocal()

    try:
        rows = [
            SystemMetadata(
                table_name="students",
                field_name=None,
                field_meaning="学生主体基础数据表，用于初始化仿真中的学生Agent。",
                data_source="公开数据+规则生成",
                notes="用于学生能力、偏好和预期薪资初始化",
                sort_order=0,
            ),
            SystemMetadata(
                table_name="students",
                field_name="student_code",
                field_type="VARCHAR(64)",
                is_nullable=0,
                default_value=None,
                field_meaning="学生唯一编码。",
                example_value="STU00001",
                data_source="规则生成",
                notes="主业务唯一标识",
                sort_order=1,
            ),
            SystemMetadata(
                table_name="students",
                field_name="ability",
                field_type="FLOAT",
                is_nullable=0,
                default_value="0.5",
                field_meaning="学生能力水平，通常取值0到1之间。",
                example_value="0.73",
                data_source="规则生成",
                notes="影响学习效果与岗位匹配",
                sort_order=2,
            ),
        ]

        db.add_all(rows)
        db.commit()
        print("system_metadata initialized successfully.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()