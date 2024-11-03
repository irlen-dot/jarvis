from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, MetaData, desc
from sqlalchemy.orm import relationship, declarative_base, Session as SQLAlchemySession
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List
import os
from dotenv import load_dotenv
from sqlalchemy.orm import relationship, sessionmaker, scoped_session, DeclarativeBase
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum


load_dotenv()

# Define the Role enum
class Role(str, Enum):
    AI = "AI"
    HUMAN = "Human"

# Create SQLAlchemy engine and base
engine = create_engine(os.getenv('DATABASE_URL'))
class Base(DeclarativeBase):
    pass

# Base = declarative_base()

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    type=Column(String, nullable=True)

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    content = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(Role, name='role_enum'), nullable=False)  # Using Enum type
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    session = relationship("Session", back_populates="messages")

# Create all tables
Base.metadata.create_all(engine)

class Database:
    def __init__(self):
        """Initialize database connection using environment variables"""
        DB_USER = os.getenv('DB_USER', 'postgres')
        DB_PASSWORD = os.getenv('DB_PASSWORD', '8556')
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '5432')
        DB_NAME = os.getenv('DB_NAME', 'jarvis')

        # Create connection URL
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        
        # Create engine
        self.engine = create_engine(DATABASE_URL)
        
        # Create all tables
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine)
        scoped_session(self.SessionLocal)
        self.Session = Session()

    @property
    def session(self):
        session_local = self.SessionLocal()
        return session_local

    def create_session(self, path: str):
        """Create a new coding session"""
        db_session = self.SessionLocal()
    
        try:
            new_session = Session(path=path)
            db_session.add(new_session)
            db_session.commit()
            db_session.refresh(new_session)
            return new_session
        finally:
            db_session.close()

    def find_session_by_path(self, path_to_find: str) -> Session:
        # Convert backslashes to forward slashes
        path_str = str(path_to_find)
        path_parsed = path_str.replace('\\', '/')  # Use single backslash
        like_pattern = f"%{path_parsed}%"
        
        print("Original path:", path_str)
        print("Parsed path:", path_parsed)
        print("Like pattern:", like_pattern)
        
        # It is just a connection to the Session table
        db = self.session

        try:
            query = db.query(Session)\
                .filter(Session.path.like(like_pattern))\
                .order_by(Session.created_at.desc())
            
            result = query.first()
            return result
        finally:
            db.close()

    def get_latest_session(self) -> Session:
        session = self.session.query(Session).first()
        return session

    def get_session(self, session_id: int) -> Session:
        """Get a session by ID"""
        db_session = self.SessionLocal()
        try:
            return db_session.query(Session).filter(Session.id == session_id).first()
        finally:
            db_session.close()

    def add_message(self, session_id: int, content: str, role: Role):
        """Add a message to a session"""
        db_session = self.SessionLocal()
        try:
            new_message = Message(
                session_id=session_id,
                content=content,
                role=role
            )
            db_session.add(new_message)
            db_session.commit()
            db_session.refresh(new_message)
            return new_message
        finally:
            db_session.close()

    def get_messages(self, session_id: int):
        """Get all messages for a session"""
        db_session = self.SessionLocal()
        try:
            return (
                db_session.query(Message)
                .filter(Message.sessionId == session_id)
                .order_by(Message.timestamp)
                .all()
            )
        finally:
            db_session.close()

    def get_latest_session_by_path(self, path: str):
        """Get the latest session for a specific path"""
        db_session = self.SessionLocal()
        try:
            return (
                db_session.query(Session)
                .filter(Session.path == path)
                .order_by(Session.id.desc())
                .first()
            )
        finally:
            db_session.close()