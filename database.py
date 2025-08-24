from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

Base = declarative_base()

class VideoRecord(Base):
    __tablename__ = 'videos'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String, unique=True, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer)
    duration = Column(Float)  # em segundos
    
    # Transcrição
    transcript_pt = Column(Text)
    transcript_en = Column(Text)
    
    # Contexto e categorização
    video_context = Column(Text)
    category = Column(String)
    confidence_score = Column(Float)
    keywords = Column(Text)  # JSON string com keywords
    
    # Metadados
    processed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<VideoRecord(file_name='{self.file_name}', category='{self.category}')>"

class DatabaseManager:
    def __init__(self, db_path=config.DB_PATH):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_video(self, video_record):
        self.session.add(video_record)
        self.session.commit()
        return video_record.id
    
    def get_video_by_path(self, file_path):
        return self.session.query(VideoRecord).filter_by(file_path=file_path).first()
    
    def search_videos_by_keywords(self, keywords):
        results = []
        for keyword in keywords:
            videos = self.session.query(VideoRecord).filter(
                VideoRecord.transcript_pt.contains(keyword) |
                VideoRecord.video_context.contains(keyword) |
                VideoRecord.keywords.contains(keyword)
            ).all()
            results.extend(videos)
        return list(set(results))  # Remove duplicatas
    
    def get_videos_by_category(self, category):
        return self.session.query(VideoRecord).filter_by(category=category).all()
    
    def get_all_videos(self):
        return self.session.query(VideoRecord).all()
    
    def close(self):
        self.session.close()
