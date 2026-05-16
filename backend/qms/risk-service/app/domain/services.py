"""Risk Service — Risk management domain service."""

import structlog

from rainer_common.exceptions import ForbiddenError, NotFoundError

from ..infra.db.models import Risk
from ..infra.db.repositories import RiskRepository

logger = structlog.get_logger(__name__)


class RiskDomainService:
    """Risk lifecycle management: identification, scoring, mitigation, closure."""

    def __init__(self, risk_repo: RiskRepository, tenant_id: str) -> None:
        self._risks = risk_repo
        self._tenant_id = tenant_id

    async def list_risks(
        self,
        category: str | None = None,
        status: str | None = None,
        owner_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Risk], int]:
        return await self._risks.list_risks(
            tenant_id=self._tenant_id,
            category=category, status=status, owner_id=owner_id,
            offset=(page - 1) * page_size, limit=page_size,
        )

    async def create_risk(
        self,
        risk_id: str,
        category: str,
        description: str,
        severity: int,
        likelihood: int,
        created_by: str,
        mitigation_plan: str | None = None,
        owner_id: str | None = None,
        review_date=None,
    ) -> Risk:
        risk = await self._risks.create(
            tenant_id=self._tenant_id,
            risk_id=risk_id,
            category=category,
            description=description,
            severity=severity,
            likelihood=likelihood,
            created_by=created_by,
            mitigation_plan=mitigation_plan,
            owner_id=owner_id or created_by,
            review_date=review_date,
        )
        logger.info("risk_created", risk_db_id=risk.id, tenant=self._tenant_id)
        return risk

    async def get_risk(self, risk_db_id: str) -> Risk:
        risk = await self._risks.get_by_id(risk_db_id)
        if not risk:
            raise NotFoundError("Risk", risk_db_id)
        if risk.tenant_id != self._tenant_id:
            raise ForbiddenError("Access denied to this risk")
        return risk

    async def update_risk(self, risk_db_id: str, **fields) -> Risk:
        await self.get_risk(risk_db_id)
        allowed = {"category", "description", "severity", "likelihood",
                   "mitigation_plan", "owner_id", "status", "review_date"}
        filtered = {k: v for k, v in fields.items() if k in allowed and v is not None}
        if filtered:
            await self._risks.update(risk_db_id, **filtered)
        return await self.get_risk(risk_db_id)

    async def get_risk_matrix(self) -> list[dict]:
        """Return 5x5 matrix data: list of {severity, likelihood, count, risk_ids[]}."""
        all_risks = await self._risks.list_all_for_matrix(self._tenant_id)
        matrix: dict[tuple[int, int], dict] = {}
        for s in range(1, 6):
            for l in range(1, 6):
                matrix[(s, l)] = {"severity": s, "likelihood": l, "count": 0, "risk_ids": []}
        for risk in all_risks:
            key = (risk.severity, risk.likelihood)
            if key in matrix:
                matrix[key]["count"] += 1
                matrix[key]["risk_ids"].append(risk.id)
        return list(matrix.values())
