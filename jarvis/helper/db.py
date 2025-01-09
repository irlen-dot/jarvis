from pathlib import Path
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    desc,
)
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
engine = create_engine(os.getenv("DATABASE_URL"))


class Base(DeclarativeBase):
    pass


class ProjectCollection(Base):
    __tablename__ = "project_collections"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    path = Column(String, nullable=False)
    cache_cleaned = Column(Boolean)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    messages = relationship(
        "Message", back_populates="session", cascade="all, delete-orphan"
    )
    type = Column(String, nullable=True)
    collection = Column(String, nullable=False)
    # project_type = Column(String, nullable=True)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    content = Column(String, nullable=False)
    role = Column(
        SQLAlchemyEnum(Role, name="role_enum"), nullable=False
    )  # Using Enum type
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("Session", back_populates="messages")


# Create all tables
Base.metadata.create_all(engine)


class Database:
    def __init__(self):
        """Initialize database connection using environment variables"""
        DB_USER = os.getenv("DB_USER", "postgres")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "8556")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_NAME = os.getenv("DB_NAME", "jarvis")

        # Create connection URL
        DATABASE_URL = (
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

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

    def create_project_collection(self, name: str, path: str):
        db_session = self.SessionLocal()
        path = self._replace_path_slashes(path=path)
        try:
            collection = ProjectCollection(name=name, path=path)
            db_session.add(collection)
            db_session.commit()
            db_session.refresh(collection)
            return collection
        finally:
            db_session.close()

    def get_collection_by_path(self, path: str):
        """Get a collection by path"""
        db_session = self.SessionLocal()
        path = self._replace_path_slashes(path=path)
        try:
            return (
                db_session.query(ProjectCollection)
                .filter(ProjectCollection.path == path)
                .first()
            )
        finally:
            db_session.close()

    def get_project_collection(self, collection_id: int):
        db_session = self.SessionLocal()
        try:
            return (
                db_session.query(ProjectCollection)
                .filter(ProjectCollection.id == collection_id)
                .first()
            )
        finally:
            db_session.close()

    def create_session(self, path: str):
        """Create a new coding session"""
        print("Creating new session...")
        db_session = self.SessionLocal()
        parsed_path = self._replace_path_slashes(path)
        print(f"The path parsed is {parsed_path}")
        try:
            new_session = Session(path=parsed_path)
            db_session.add(new_session)
            db_session.commit()
            db_session.refresh(new_session)
            return new_session
        finally:
            db_session.close()

    def get_messages_by_sessions_path(self, path_to_find: str):
        path = self._replace_path_slashes(path_to_find)
        session = self.find_session_by_path(path)
        messages = self.get_messages(session.id)
        return messages

    def find_session_by_path(self, path_to_find: str) -> Session:
        path_obj = Path(path_to_find)
        while path_obj != path_obj.parent:
            parsed_path = self._replace_path_slashes(str(path_obj))
            db = self.session
            try:
                query = (
                    db.query(Session)
                    .filter(Session.path == parsed_path)
                    .order_by(Session.created_at.desc())
                )
                result = query.first()
                if result:
                    return result
                path_obj = path_obj.parent
            finally:
                db.close()
        return None

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
        print("Start Start")
        db_session = self.SessionLocal()
        print("End end")
        try:
            new_message = Message(session_id=session_id, content=content, role=role)
            print(f"The new message: {new_message}")
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
                .filter(Message.session_id == session_id)
                .order_by(Message.created_at)
                .all()
            )
        finally:
            db_session.close()

    def get_latest_session_by_path(self, path: str):
        """Get the latest session for a specific path"""
        print(f"The path {path}")
        parsed_path = self._replace_path_slashes(path)
        # print(f"Parsed path: {parsed_path}")
        db_session = self.SessionLocal()
        try:
            return (
                db_session.query(Session)
                .filter(Session.path == parsed_path)
                .order_by(Session.id.desc())
                .first()
            )
        finally:
            db_session.close()

    def update_collection(self, session_id: int, collection: str):
        """Update the collection field for a session"""
        db_session = self.SessionLocal()
        try:
            session = db_session.query(Session).filter(Session.id == session_id).first()
            if session:
                session.collection = collection
                db_session.commit()
                return session
        finally:
            db_session.close()

    def _replace_path_slashes(self, path: str):
        parsed_path = path.replace("\\", "/")
        print(f"the parsed Parsed path: {parsed_path}")
        return parsed_path

    def delete_collection_by_path(self, path: str) -> bool:
        """
        Delete a project collection and its associated data by path.

        Args:
            path (str): The path of the project collection to delete

        Returns:
            bool: True if deletion was successful, False if collection wasn't found
        """
        db_session = self.SessionLocal()
        path = self._replace_path_slashes(path)

        try:
            collection = (
                db_session.query(ProjectCollection)
                .filter(ProjectCollection.path == path)
                .first()
            )

            if collection:
                # Delete the collection
                db_session.delete(collection)
                db_session.commit()
                return True
            return False
        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            db_session.close()

    def delete_collection_by_name(self, name: str) -> bool:
        """
        Delete a project collection and its associated data by collection name.

        Args:
            name (str): The name of the project collection to delete

        Returns:
            bool: True if deletion was successful, False if collection wasn't found
        """
        db_session = self.SessionLocal()

        try:
            collection = (
                db_session.query(ProjectCollection)
                .filter(ProjectCollection.name == name)
                .first()
            )

            if collection:
                # Delete the collection
                db_session.delete(collection)
                db_session.commit()
                return True
            return False
        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            db_session.close()
