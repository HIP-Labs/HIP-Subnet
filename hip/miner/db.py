from sqlalchemy import ForeignKey, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    label = Column(String, nullable=False)
    type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    image = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    expiry = Column(Integer, nullable=False)
    answer = Column(String, nullable=False)

    options = relationship(
        "Option", back_populates="task", cascade="all, delete-orphan"
    )


class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    option = Column(String, nullable=False)

    task = relationship("Task", back_populates="options")


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
