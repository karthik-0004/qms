"""SCIM 2.0 Schemas — RFC 7643 / RFC 7644 compliant Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ── SCIM Meta ────────────────────────────────────────────────────────────────

class SCIMMeta(BaseModel):
    resourceType: str
    created: datetime | None = None
    lastModified: datetime | None = None
    location: str | None = None
    version: str | None = None


# ── SCIM Name ────────────────────────────────────────────────────────────────

class SCIMName(BaseModel):
    formatted: str | None = None
    familyName: str | None = None
    givenName: str | None = None


# ── SCIM Email ───────────────────────────────────────────────────────────────

class SCIMEmail(BaseModel):
    value: str
    type: str = "work"
    primary: bool = True


# ── SCIM Phone ───────────────────────────────────────────────────────────────

class SCIMPhoneNumber(BaseModel):
    value: str
    type: str = "work"


# ── SCIM Group Member ───────────────────────────────────────────────────────

class SCIMGroupMember(BaseModel):
    value: str
    display: str | None = None
    ref: str | None = Field(default=None, alias="$ref")


# ── SCIM User Resource ──────────────────────────────────────────────────────

class SCIMUserResource(BaseModel):
    schemas: list[str] = ["urn:ietf:params:scim:schemas:core:2.0:User"]
    id: str | None = None
    externalId: str | None = None
    userName: str
    name: SCIMName | None = None
    displayName: str | None = None
    emails: list[SCIMEmail] = []
    phoneNumbers: list[SCIMPhoneNumber] = []
    active: bool = True
    title: str | None = None
    department: str | None = None
    groups: list[SCIMGroupMember] = []
    meta: SCIMMeta | None = None

    model_config = {"populate_by_name": True}


# ── SCIM Group Resource ─────────────────────────────────────────────────────

class SCIMGroupResource(BaseModel):
    schemas: list[str] = ["urn:ietf:params:scim:schemas:core:2.0:Group"]
    id: str | None = None
    displayName: str
    members: list[SCIMGroupMember] = []
    meta: SCIMMeta | None = None

    model_config = {"populate_by_name": True}


# ── SCIM List Response ───────────────────────────────────────────────────────

class SCIMListResponse(BaseModel):
    schemas: list[str] = ["urn:ietf:params:scim:api:messages:2.0:ListResponse"]
    totalResults: int
    startIndex: int = 1
    itemsPerPage: int = 20
    Resources: list[dict[str, Any]] = Field(default_factory=list)


# ── SCIM Error Response ─────────────────────────────────────────────────────

class SCIMErrorResponse(BaseModel):
    schemas: list[str] = ["urn:ietf:params:scim:api:messages:2.0:Error"]
    detail: str
    status: str
    scimType: str | None = None


# ── SCIM Patch Operation ────────────────────────────────────────────────────

class SCIMPatchOp(BaseModel):
    op: Literal["add", "remove", "replace"]
    path: str | None = None
    value: Any = None


class SCIMPatchRequest(BaseModel):
    schemas: list[str] = ["urn:ietf:params:scim:api:messages:2.0:PatchOp"]
    Operations: list[SCIMPatchOp]


# ── SCIM Service Provider Config ────────────────────────────────────────────

class SCIMBulkConfig(BaseModel):
    supported: bool = False
    maxOperations: int = 0
    maxPayloadSize: int = 0


class SCIMFilterConfig(BaseModel):
    supported: bool = True
    maxResults: int = 200


class SCIMChangePasswordConfig(BaseModel):
    supported: bool = False


class SCIMSortConfig(BaseModel):
    supported: bool = False


class SCIMETagConfig(BaseModel):
    supported: bool = False


class SCIMAuthScheme(BaseModel):
    type: str = "oauthbearertoken"
    name: str = "OAuth Bearer Token"
    description: str = "Authentication scheme using the OAuth Bearer Token Standard"
    specUri: str = "https://tools.ietf.org/html/rfc6750"
    primary: bool = True


class SCIMServiceProviderConfig(BaseModel):
    schemas: list[str] = ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"]
    documentationUri: str = "https://docs.rainertek.com/scim"
    patch: dict[str, bool] = {"supported": True}
    bulk: SCIMBulkConfig = SCIMBulkConfig()
    filter: SCIMFilterConfig = SCIMFilterConfig()
    changePassword: SCIMChangePasswordConfig = SCIMChangePasswordConfig()
    sort: SCIMSortConfig = SCIMSortConfig()
    etag: SCIMETagConfig = SCIMETagConfig()
    authenticationSchemes: list[SCIMAuthScheme] = [SCIMAuthScheme()]
    meta: SCIMMeta = SCIMMeta(resourceType="ServiceProviderConfig")


# ── SCIM ResourceType ───────────────────────────────────────────────────────

class SCIMSchemaExtension(BaseModel):
    schema_: str = Field(alias="schema")
    required: bool = False


class SCIMResourceType(BaseModel):
    schemas: list[str] = ["urn:ietf:params:scim:schemas:core:2.0:ResourceType"]
    id: str
    name: str
    description: str
    endpoint: str
    schema_: str = Field(alias="schema")
    meta: SCIMMeta

    model_config = {"populate_by_name": True}
