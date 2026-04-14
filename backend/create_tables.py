from app.core.database import Base, engine
import app.models  # noqa: F401


def create_all_tables():
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully.")


if __name__ == "__main__":
    create_all_tables()