"""PT Service — Proficiency testing domain service."""

import math

import structlog

from rainer_common.exceptions import ForbiddenError, NotFoundError, ValidationError

from ..infra.db.models import PTProgram, PTRound
from ..infra.db.repositories import PTProgramRepository, PTRoundRepository

logger = structlog.get_logger(__name__)


def _calculate_z_score(reported: float, reference: float, sigma: float | None = None) -> float:
    """z = (reported - reference) / sigma; sigma defaults to reference * 0.1."""
    s = sigma if sigma is not None else abs(reference) * 0.1
    if s == 0:
        return 0.0
    return (reported - reference) / s


def _calculate_en_number(reported: float, reference: float) -> float:
    """Simplified En = |reported - reference| / (reference * 0.02)."""
    denominator = abs(reference) * 0.02
    if denominator == 0:
        return 0.0
    return abs(reported - reference) / denominator


class PTDomainService:
    """Proficiency testing lifecycle: programs, rounds, scoring."""

    def __init__(
        self,
        program_repo: PTProgramRepository,
        round_repo: PTRoundRepository,
        tenant_id: str,
    ) -> None:
        self._programs = program_repo
        self._rounds = round_repo
        self._tenant_id = tenant_id

    async def list_programs(self, page: int = 1, page_size: int = 20) -> tuple[list[PTProgram], int]:
        return await self._programs.list_programs(
            tenant_id=self._tenant_id,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def create_program(
        self,
        provider: str,
        scheme_name: str,
        parameter: str,
        frequency_months: int,
        created_by: str,
    ) -> PTProgram:
        program = await self._programs.create(
            tenant_id=self._tenant_id,
            provider=provider,
            scheme_name=scheme_name,
            parameter=parameter,
            frequency_months=frequency_months,
            created_by=created_by,
        )
        logger.info("pt_program_created", program_id=program.id, tenant=self._tenant_id)
        return program

    async def get_program(self, program_id: str) -> PTProgram:
        program = await self._programs.get_by_id(program_id)
        if not program:
            raise NotFoundError("PTProgram", program_id)
        if program.tenant_id != self._tenant_id:
            raise ForbiddenError("Access denied to this PT program")
        return program

    async def list_rounds_for_program(self, program_id: str) -> list[PTRound]:
        await self.get_program(program_id)
        return await self._rounds.list_by_program(program_id)

    async def create_round(
        self,
        program_id: str,
        round_id: str,
        created_by: str,
        sample_received_date=None,
        result_due_date=None,
        notes: str | None = None,
    ) -> PTRound:
        await self.get_program(program_id)
        pt_round = await self._rounds.create(
            tenant_id=self._tenant_id,
            program_id=program_id,
            round_id=round_id,
            created_by=created_by,
            sample_received_date=sample_received_date,
            result_due_date=result_due_date,
            notes=notes,
        )
        logger.info("pt_round_created", round_id=pt_round.id, program_id=program_id)
        return pt_round

    async def get_round(self, round_id: str) -> PTRound:
        pt_round = await self._rounds.get_by_id(round_id)
        if not pt_round:
            raise NotFoundError("PTRound", round_id)
        if pt_round.tenant_id != self._tenant_id:
            raise ForbiddenError("Access denied to this PT round")
        return pt_round

    async def update_round(self, round_id: str, **fields) -> PTRound:
        await self.get_round(round_id)
        allowed = {"sample_received_date", "result_due_date", "reported_result",
                   "reference_value", "z_score", "en_number", "status", "capa_id", "notes"}
        filtered = {k: v for k, v in fields.items() if k in allowed and v is not None}
        if filtered:
            await self._rounds.update(round_id, **filtered)
        return await self.get_round(round_id)

    async def calculate_scores(self, round_id: str) -> dict:
        """Calculate z-score and En from round data. Returns dict with computed values."""
        pt_round = await self.get_round(round_id)
        if pt_round.reported_result is None or pt_round.reference_value is None:
            raise ValidationError("Both reported_result and reference_value must be set before calculating scores")
        z_score = _calculate_z_score(pt_round.reported_result, pt_round.reference_value)
        en_number = _calculate_en_number(pt_round.reported_result, pt_round.reference_value)
        # Persist scores
        await self._rounds.update(round_id, z_score=z_score, en_number=en_number, status="scored")
        return {
            "round_id": round_id,
            "reported_result": pt_round.reported_result,
            "reference_value": pt_round.reference_value,
            "z_score": round(z_score, 4),
            "en_number": round(en_number, 4),
            "z_score_pass": abs(z_score) <= 2.0,
            "en_number_pass": en_number <= 1.0,
        }
