"""Workflow Engine — Core workflow domain service (state machine orchestration)."""

from datetime import datetime, timezone

import structlog

from rainer_common.exceptions import ConflictError, NotFoundError, ValidationError

from ..infra.db.models import WorkflowDefinition, WorkflowHistory, WorkflowInstance
from ..infra.db.repositories import (
    WorkflowDefinitionRepository,
    WorkflowHistoryRepository,
    WorkflowInstanceRepository,
)

logger = structlog.get_logger(__name__)


class WorkflowDomainService:
    """
    Generic state machine for workflow orchestration.
    Defines + executes state transitions for any entity type.
    """

    def __init__(
        self,
        definition_repo: WorkflowDefinitionRepository,
        instance_repo: WorkflowInstanceRepository,
        history_repo: WorkflowHistoryRepository,
    ) -> None:
        self._definitions = definition_repo
        self._instances = instance_repo
        self._history = history_repo

    async def create_definition(
        self,
        name: str,
        entity_type: str,
        states: dict,
        transitions: dict,
    ) -> WorkflowDefinition:
        """
        Define a new workflow state machine.
        
        states format:
        {
          "draft": {"label": "Draft", "is_initial": true, "is_terminal": false},
          "under_review": {"label": "Under Review"},
          "approved": {"label": "Approved", "is_terminal": true}
        }
        
        transitions format:
        {
          "submit_for_review": {
            "from": ["draft"],
            "to": "under_review",
            "label": "Submit for Review",
            "requires_comment": false,
            "requires_signature": false
          },
          "approve": {
            "from": ["under_review"],
            "to": "approved",
            "requires_signature": true
          }
        }
        """
        self._validate_definition(states, transitions)

        # Deactivate existing active definitions for same entity_type
        existing = await self._definitions.get_active_by_entity_type(entity_type)
        if existing:
            from sqlalchemy import update as sqla_update
            # We'll just create a new version alongside

        version = (existing.version + 1) if existing else 1
        defn = await self._definitions.create(
            name=name,
            entity_type=entity_type,
            states=states,
            transitions=transitions,
            version=version,
        )
        logger.info("workflow_definition_created", definition_id=defn.id, entity_type=entity_type)
        return defn

    async def start_workflow(
        self,
        entity_type: str,
        entity_id: str,
        created_by: str,
        assignee_id: str | None = None,
        due_at: datetime | None = None,
        context: dict | None = None,
    ) -> WorkflowInstance:
        """Start a workflow instance for an entity."""
        defn = await self._definitions.get_active_by_entity_type(entity_type)
        if not defn:
            raise NotFoundError("WorkflowDefinition", entity_type)

        # Check no active instance exists
        existing = await self._instances.get_by_entity(entity_type, entity_id)
        if existing:
            raise ConflictError(f"Workflow already active for {entity_type}/{entity_id}")

        # Find initial state
        initial_state = self._get_initial_state(defn.states)

        instance = await self._instances.create(
            definition_id=defn.id,
            entity_type=entity_type,
            entity_id=entity_id,
            initial_state=initial_state,
            created_by=created_by,
            assignee_id=assignee_id,
            due_at=due_at,
            context=context,
        )

        await self._history.create(
            instance_id=instance.id,
            from_state=None,
            to_state=initial_state,
            action="start",
            actor_id=created_by,
        )

        logger.info(
            "workflow_started",
            instance_id=instance.id,
            entity_type=entity_type,
            entity_id=entity_id,
            initial_state=initial_state,
        )
        return instance

    async def transition(
        self,
        instance_id: str,
        action: str,
        actor_id: str,
        comment: str | None = None,
        signature: str | None = None,
        new_assignee_id: str | None = None,
        metadata: dict | None = None,
    ) -> WorkflowInstance:
        """Execute a state transition on a workflow instance."""
        instance = await self._instances.get_by_id(instance_id)
        if not instance:
            raise NotFoundError("WorkflowInstance", instance_id)

        if instance.completed_at:
            raise ConflictError("Workflow instance is already completed")

        defn = await self._definitions.get_by_id(instance.definition_id)
        if not defn:
            raise NotFoundError("WorkflowDefinition", instance.definition_id)

        # Validate transition
        transition_def = defn.transitions.get(action)
        if not transition_def:
            raise ValidationError(f"Action '{action}' is not defined in this workflow")

        allowed_from = transition_def.get("from", [])
        if instance.current_state not in allowed_from:
            raise ValidationError(
                f"Action '{action}' is not allowed from state '{instance.current_state}'. "
                f"Allowed from: {allowed_from}"
            )

        # Check signature requirement
        if transition_def.get("requires_signature") and not signature:
            raise ValidationError(f"Action '{action}' requires an e-signature")

        # Check comment requirement
        if transition_def.get("requires_comment") and not comment:
            raise ValidationError(f"Action '{action}' requires a comment")

        new_state = transition_def["to"]

        await self._instances.transition(instance_id, new_state, new_assignee_id)

        # Record history
        await self._history.create(
            instance_id=instance_id,
            from_state=instance.current_state,
            to_state=new_state,
            action=action,
            actor_id=actor_id,
            comment=comment,
            signature=signature,
            metadata=metadata,
        )

        # Check if terminal state
        state_config = defn.states.get(new_state, {})
        if state_config.get("is_terminal"):
            await self._instances.complete(instance_id)
            logger.info("workflow_completed", instance_id=instance_id, final_state=new_state)

        # Reload instance
        updated = await self._instances.get_by_id(instance_id)
        logger.info(
            "workflow_transitioned",
            instance_id=instance_id,
            from_state=instance.current_state,
            to_state=new_state,
            action=action,
        )
        return updated

    async def get_instance(self, instance_id: str) -> WorkflowInstance:
        instance = await self._instances.get_by_id(instance_id)
        if not instance:
            raise NotFoundError("WorkflowInstance", instance_id)
        return instance

    async def get_instance_history(self, instance_id: str) -> list[WorkflowHistory]:
        await self.get_instance(instance_id)
        return await self._history.get_by_instance(instance_id)

    async def get_instance_for_entity(self, entity_type: str, entity_id: str) -> WorkflowInstance | None:
        return await self._instances.get_by_entity(entity_type, entity_id)

    async def list_my_tasks(
        self, assignee_id: str, state: str | None = None
    ) -> list[WorkflowInstance]:
        return await self._instances.list_by_assignee(assignee_id, state)

    async def list_instances(
        self,
        entity_type: str | None = None,
        current_state: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[WorkflowInstance], int]:
        return await self._instances.list_all(
            entity_type=entity_type,
            current_state=current_state,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def get_available_transitions(self, instance_id: str) -> list[dict]:
        """Get list of available actions from current state."""
        instance = await self.get_instance(instance_id)
        defn = await self._definitions.get_by_id(instance.definition_id)
        if not defn:
            return []
        available = []
        for action_name, transition in defn.transitions.items():
            if instance.current_state in transition.get("from", []):
                available.append({
                    "action": action_name,
                    "to_state": transition["to"],
                    "label": transition.get("label", action_name),
                    "requires_comment": transition.get("requires_comment", False),
                    "requires_signature": transition.get("requires_signature", False),
                })
        return available

    def _validate_definition(self, states: dict, transitions: dict) -> None:
        if not states:
            raise ValidationError("Workflow must have at least one state")
        initial_states = [k for k, v in states.items() if v.get("is_initial")]
        if len(initial_states) != 1:
            raise ValidationError("Workflow must have exactly one initial state")
        for action, transition in transitions.items():
            if "from" not in transition or "to" not in transition:
                raise ValidationError(f"Transition '{action}' must have 'from' and 'to'")
            for from_state in transition["from"]:
                if from_state not in states:
                    raise ValidationError(f"Unknown state '{from_state}' in transition '{action}'")
            if transition["to"] not in states:
                raise ValidationError(f"Unknown state '{transition['to']}' in transition '{action}'")

    def _get_initial_state(self, states: dict) -> str:
        for state_name, config in states.items():
            if config.get("is_initial"):
                return state_name
        raise ValidationError("No initial state found in workflow definition")
