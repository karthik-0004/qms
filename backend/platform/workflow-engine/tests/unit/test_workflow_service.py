"""Unit tests — WorkflowDomainService state machine logic."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from rainer_common.exceptions import ConflictError, NotFoundError, ValidationError

from app.domain.services import WorkflowDomainService
from app.infra.db.models import WorkflowDefinition, WorkflowInstance

DOCUMENT_STATES = {
    "draft": {"label": "Draft", "is_initial": True, "is_terminal": False},
    "under_review": {"label": "Under Review", "is_terminal": False},
    "approved": {"label": "Approved", "is_terminal": True},
    "rejected": {"label": "Rejected", "is_terminal": True},
}

DOCUMENT_TRANSITIONS = {
    "submit_for_review": {
        "from": ["draft"],
        "to": "under_review",
        "label": "Submit for Review",
    },
    "approve": {
        "from": ["under_review"],
        "to": "approved",
        "requires_signature": True,
    },
    "reject": {
        "from": ["under_review"],
        "to": "rejected",
        "requires_comment": True,
    },
    "rework": {
        "from": ["rejected"],
        "to": "draft",
    },
}


def make_definition(**kwargs) -> WorkflowDefinition:
    defaults = dict(
        id=str(uuid4()), name="Document Approval", version=1,
        entity_type="document", states=DOCUMENT_STATES, transitions=DOCUMENT_TRANSITIONS,
        is_active=True, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    d = MagicMock(spec=WorkflowDefinition)
    for k, v in defaults.items():
        setattr(d, k, v)
    return d


def make_instance(**kwargs) -> WorkflowInstance:
    defaults = dict(
        id=str(uuid4()), definition_id=str(uuid4()), entity_type="document",
        entity_id=str(uuid4()), current_state="draft", context={},
        assignee_id=None, due_at=None, completed_at=None,
        created_by=str(uuid4()), created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    i = MagicMock(spec=WorkflowInstance)
    for k, v in defaults.items():
        setattr(i, k, v)
    return i


@pytest.fixture
def definition_repo():
    return AsyncMock()


@pytest.fixture
def instance_repo():
    return AsyncMock()


@pytest.fixture
def history_repo():
    return AsyncMock()


@pytest.fixture
def svc(definition_repo, instance_repo, history_repo):
    return WorkflowDomainService(
        definition_repo=definition_repo,
        instance_repo=instance_repo,
        history_repo=history_repo,
    )


class TestCreateDefinition:
    @pytest.mark.asyncio
    async def test_creates_valid_definition(self, svc, definition_repo):
        definition_repo.get_active_by_entity_type.return_value = None
        mock_defn = make_definition()
        definition_repo.create.return_value = mock_defn

        result = await svc.create_definition(
            name="Document Approval",
            entity_type="document",
            states=DOCUMENT_STATES,
            transitions=DOCUMENT_TRANSITIONS,
        )
        assert result is mock_defn

    @pytest.mark.asyncio
    async def test_raises_on_no_initial_state(self, svc):
        bad_states = {
            "state_a": {"label": "A"},
            "state_b": {"label": "B"},
        }
        with pytest.raises(ValidationError, match="initial state"):
            await svc.create_definition("bad", "entity", bad_states, {})

    @pytest.mark.asyncio
    async def test_raises_on_multiple_initial_states(self, svc):
        bad_states = {
            "state_a": {"label": "A", "is_initial": True},
            "state_b": {"label": "B", "is_initial": True},
        }
        with pytest.raises(ValidationError, match="initial state"):
            await svc.create_definition("bad", "entity", bad_states, {})

    @pytest.mark.asyncio
    async def test_raises_on_unknown_state_in_transition(self, svc):
        states = {"draft": {"is_initial": True}}
        transitions = {"bad_action": {"from": ["nonexistent"], "to": "draft"}}
        with pytest.raises(ValidationError, match="Unknown state"):
            await svc.create_definition("bad", "entity", states, transitions)


class TestStartWorkflow:
    @pytest.mark.asyncio
    async def test_starts_workflow_with_initial_state(self, svc, definition_repo, instance_repo, history_repo):
        defn = make_definition()
        definition_repo.get_active_by_entity_type.return_value = defn
        instance_repo.get_by_entity.return_value = None
        mock_instance = make_instance(current_state="draft")
        instance_repo.create.return_value = mock_instance
        history_repo.create.return_value = MagicMock()

        result = await svc.start_workflow("document", str(uuid4()), str(uuid4()))
        assert result.current_state == "draft"

    @pytest.mark.asyncio
    async def test_raises_if_no_definition(self, svc, definition_repo):
        definition_repo.get_active_by_entity_type.return_value = None
        with pytest.raises(NotFoundError):
            await svc.start_workflow("document", str(uuid4()), str(uuid4()))

    @pytest.mark.asyncio
    async def test_raises_if_instance_already_active(self, svc, definition_repo, instance_repo):
        definition_repo.get_active_by_entity_type.return_value = make_definition()
        instance_repo.get_by_entity.return_value = make_instance()
        with pytest.raises(ConflictError):
            await svc.start_workflow("document", str(uuid4()), str(uuid4()))


class TestTransition:
    @pytest.mark.asyncio
    async def test_successful_transition(self, svc, definition_repo, instance_repo, history_repo):
        instance = make_instance(current_state="draft")
        defn = make_definition()
        instance_repo.get_by_id.side_effect = [instance, make_instance(current_state="under_review")]
        definition_repo.get_by_id.return_value = defn
        instance_repo.transition.return_value = None
        history_repo.create.return_value = MagicMock()

        result = await svc.transition(instance.id, "submit_for_review", str(uuid4()))
        instance_repo.transition.assert_called_once_with(instance.id, "under_review", None)

    @pytest.mark.asyncio
    async def test_raises_on_invalid_action(self, svc, definition_repo, instance_repo):
        instance = make_instance(current_state="draft")
        instance_repo.get_by_id.return_value = instance
        definition_repo.get_by_id.return_value = make_definition()

        with pytest.raises(ValidationError, match="not defined"):
            await svc.transition(instance.id, "nonexistent_action", str(uuid4()))

    @pytest.mark.asyncio
    async def test_raises_on_wrong_from_state(self, svc, definition_repo, instance_repo):
        instance = make_instance(current_state="approved")
        instance_repo.get_by_id.return_value = instance
        definition_repo.get_by_id.return_value = make_definition()

        with pytest.raises(ValidationError, match="not allowed from state"):
            await svc.transition(instance.id, "submit_for_review", str(uuid4()))

    @pytest.mark.asyncio
    async def test_raises_missing_signature(self, svc, definition_repo, instance_repo):
        instance = make_instance(current_state="under_review")
        instance_repo.get_by_id.return_value = instance
        definition_repo.get_by_id.return_value = make_definition()

        with pytest.raises(ValidationError, match="signature"):
            await svc.transition(instance.id, "approve", str(uuid4()))

    @pytest.mark.asyncio
    async def test_raises_missing_comment(self, svc, definition_repo, instance_repo):
        instance = make_instance(current_state="under_review")
        instance_repo.get_by_id.return_value = instance
        definition_repo.get_by_id.return_value = make_definition()

        with pytest.raises(ValidationError, match="comment"):
            await svc.transition(instance.id, "reject", str(uuid4()))
