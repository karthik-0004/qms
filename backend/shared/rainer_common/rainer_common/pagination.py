"""Rainer Common — Pagination helpers for FastAPI query params."""

from fastapi import Query
from pydantic import BaseModel, field_validator


class PaginationParams(BaseModel):
    """Standard pagination query parameters."""

    page: int = 1
    page_size: int = 20
    sort: str | None = None

    @field_validator("page")
    @classmethod
    def page_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("page must be >= 1")
        return v

    @field_validator("page_size")
    @classmethod
    def page_size_must_be_valid(cls, v: int) -> int:
        if v < 1:
            raise ValueError("page_size must be >= 1")
        if v > 200:
            raise ValueError("page_size must be <= 200")
        return v

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

    def get_sort_column_and_direction(
        self, allowed_columns: list[str]
    ) -> tuple[str | None, str]:
        """Parse sort param like '-created_at' into (column, direction)."""
        if not self.sort:
            return None, "desc"
        direction = "desc" if self.sort.startswith("-") else "asc"
        column = self.sort.lstrip("-")
        if column not in allowed_columns:
            return None, "desc"
        return column, direction


def pagination_params(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=200, description="Items per page"),
    sort: str | None = Query(default=None, description="Sort field, prefix with - for desc"),
) -> PaginationParams:
    """FastAPI dependency for pagination parameters."""
    return PaginationParams(page=page, page_size=page_size, sort=sort)

