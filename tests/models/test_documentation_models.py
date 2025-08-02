"""Tests for documentation models and utilities."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.ares.models.agent import Agent
from src.ares.models.base import Base
from src.ares.models.documentation import (
    DocumentationArtifact,
    DocumentationFormat,
    DocumentationTask,
    DocumentationTaskStatus,
    DocumentationTemplate,
    DocumentationType,
    QualityAssessment,
    QualityScore,
)
from src.ares.models.task import Task, TaskStatus


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()


@pytest.fixture
def sample_agent(db_session):
    """Create a sample agent for testing."""
    agent = Agent(
        name="test-documentation-agent",
        type="documentation",
        status="active",
        capabilities="documentation,quality_check",
    )
    db_session.add(agent)
    db_session.commit()
    return agent


@pytest.fixture
def sample_task(db_session, sample_agent):
    """Create a sample task for testing."""
    task = Task(
        agent_id=sample_agent.id,
        title="Test Documentation Task",
        description="Generate API documentation",
        status=TaskStatus.PENDING.value,
    )
    db_session.add(task)
    db_session.commit()
    return task


class TestDocumentationTask:
    """Test cases for DocumentationTask model."""

    def test_create_documentation_task(self, db_session, sample_agent, sample_task):
        """Test creating a documentation task."""
        doc_task = DocumentationTask(
            agent_id=sample_agent.id,
            task_id=sample_task.id,
            documentation_type=DocumentationType.API.value,
            title="API Documentation",
            description="Generate comprehensive API documentation",
            source_paths=["/src/api", "/docs/specs"],
            target_audience="developers",
            output_format=DocumentationFormat.MARKDOWN.value,
            priority=2,
        )

        db_session.add(doc_task)
        db_session.commit()

        assert doc_task.id is not None
        assert doc_task.agent_id == sample_agent.id
        assert doc_task.task_id == sample_task.id
        assert doc_task.status == DocumentationTaskStatus.PENDING.value
        assert doc_task.progress_percentage == 0.0


class TestDocumentationArtifact:
    """Test cases for DocumentationArtifact model."""

    def test_create_artifact(self, db_session, sample_agent):
        """Test creating a documentation artifact."""
        doc_task = DocumentationTask(
            agent_id=sample_agent.id,
            documentation_type=DocumentationType.API.value,
            title="Test Task",
            output_format=DocumentationFormat.MARKDOWN.value,
        )
        db_session.add(doc_task)
        db_session.commit()

        artifact = DocumentationArtifact(
            task_id=doc_task.id,
            name="api_documentation.md",
            file_path="/output/api_documentation.md",
            artifact_type="main",
            format=DocumentationFormat.MARKDOWN.value,
            size_bytes=2048,
            word_count=500,
            checksum="abc123def456",  # pragma: allowlist secret
        )

        db_session.add(artifact)
        db_session.commit()

        assert artifact.id is not None
        assert artifact.task_id == doc_task.id
        assert artifact.name == "api_documentation.md"
        assert artifact.version == "1.0"
        assert artifact.is_latest is True


class TestQualityAssessment:
    """Test cases for QualityAssessment model."""

    def test_create_quality_assessment(self, db_session, sample_agent):
        """Test creating a quality assessment."""
        doc_task = DocumentationTask(
            agent_id=sample_agent.id,
            documentation_type=DocumentationType.API.value,
            title="Quality Test Task",
            output_format=DocumentationFormat.MARKDOWN.value,
        )
        db_session.add(doc_task)
        db_session.commit()

        assessment = QualityAssessment(
            task_id=doc_task.id,
            overall_score=QualityScore.GOOD.value,
            assessment_type="automated",
            passed=True,
            completeness_score=85.0,
            accuracy_score=90.0,
            clarity_score=80.0,
            usefulness_score=88.0,
            issues_found=[{"type": "minor", "description": "Missing example"}],
            strengths=["Clear structure", "Comprehensive coverage"],
        )

        db_session.add(assessment)
        db_session.commit()

        assert assessment.id is not None
        assert assessment.task_id == doc_task.id
        assert assessment.overall_score == QualityScore.GOOD.value
        assert assessment.passed is True
        assert assessment.completeness_score == 85.0


class TestDocumentationTemplate:
    """Test cases for DocumentationTemplate model."""

    def test_create_template(self, db_session, sample_agent):
        """Test creating a documentation template."""
        template = DocumentationTemplate(
            name="Test Template",
            description="A test template",
            documentation_type=DocumentationType.USER_GUIDE.value,
            template_content="# User Guide\n\n{content}",
            default_config={"style": "modern"},
            required_inputs=["content", "version"],
            created_by=sample_agent.id,
        )

        db_session.add(template)
        db_session.commit()

        assert template.id is not None
        assert template.name == "Test Template"
        assert template.is_active is True
        assert template.usage_count == 0


if __name__ == "__main__":
    pytest.main([__file__])
