import pytest
from jarvis.project_template.controller import ProjectTempController
from jarvis.helper.db import Database, Session

@pytest.fixture
def db():
   return Database()

@pytest.fixture
def project_temp():
   return ProjectTempController()

def test_create_python_project_creates_session(db: Database, project_temp: ProjectTempController):
   """Test that creating a Python project creates a session with correct ID"""
   # Get latest session before action
   session: Session = db.get_latest_session()
   
   # Create project
   result = project_temp.manage_input("python Jaja_Binks")
   
   # Verify session ID matches
   assert session.id == result["session_id"]