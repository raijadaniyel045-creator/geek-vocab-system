# backend/database.py
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/words.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True, nullable=False)
    meaning = Column(String, nullable=False)  # 英文释义
    chinese_meaning = Column(String, nullable=True)  # 中文释义 (新)
    phonetic = Column(String, nullable=True)  # 音标
    audio_url = Column(String, nullable=True)  # 发音音频链接 (新)
    examples = Column(String, nullable=True)  # 例句

    # SM-2 记忆算法相关字段
    interval = Column(Integer, default=0)
    repetition = Column(Integer, default=0)
    easiness_factor = Column(Float, default=2.5)
    next_review_date = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)