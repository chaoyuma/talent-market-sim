from app.core.database import Base, engine

# 关键：导入所有模型，让 Base 知道它们
from app.models import *  # noqa


def main():
    Base.metadata.create_all(bind=engine)
    print("Tables created/checked successfully.")


if __name__ == "__main__":
    main()