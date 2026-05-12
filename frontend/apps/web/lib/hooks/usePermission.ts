"use client";

import { useSession } from "next-auth/react";
import { useMemo } from "react";

export type Role = "super_admin" | "tenant_admin" | "tenant_user" | "company_admin" | "company_user";

export type Permission =
  // Platform
  | "tenant:read" | "tenant:write" | "tenant:delete"
  | "user:read" | "user:write" | "user:delete"
  | "role:read" | "role:write"
  | "audit:read" | "audit:export"
  | "config:read" | "config:write"
  // Company management
  | "company:read" | "company:write" | "company:delete"
  | "company_user:read" | "company_user:write" | "company_user:delete"
  // QMS
  | "document:read" | "document:write" | "document:approve" | "document:delete"
  | "quality_event:read" | "quality_event:write"
  | "capa:read" | "capa:write" | "capa:approve"
  | "training:read" | "training:write" | "training:assign"
  | "equipment:read" | "equipment:write"
  // EM
  | "plate:read" | "plate:write"
  | "job:read" | "job:write"
  | "qa_review:read" | "qa_review:write" | "qa_review:approve"
  // CCV
  | "crm:read" | "crm:write"
  | "contract:read" | "contract:write"
  | "workorder:read" | "workorder:write" | "workorder:execute"
  | "certificate:read" | "certificate:write" | "certificate:issue"
  | "billing:read" | "billing:write"
  // Reporting
  | "report:read" | "report:generate"
  | "analytics:read";

const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  super_admin: [
    "tenant:read", "tenant:write", "tenant:delete",
    "user:read", "user:write", "user:delete",
    "role:read", "role:write",
    "audit:read", "audit:export",
    "config:read", "config:write",
    "company:read", "company:write", "company:delete",
    "company_user:read", "company_user:write", "company_user:delete",
    "document:read", "document:write", "document:approve", "document:delete",
    "quality_event:read", "quality_event:write",
    "capa:read", "capa:write", "capa:approve",
    "training:read", "training:write", "training:assign",
    "equipment:read", "equipment:write",
    "plate:read", "plate:write",
    "job:read", "job:write",
    "qa_review:read", "qa_review:write", "qa_review:approve",
    "crm:read", "crm:write",
    "contract:read", "contract:write",
    "workorder:read", "workorder:write", "workorder:execute",
    "certificate:read", "certificate:write", "certificate:issue",
    "billing:read", "billing:write",
    "report:read", "report:generate",
    "analytics:read",
  ],
  tenant_admin: [
    "user:read", "user:write", "user:delete",
    "role:read", "role:write",
    "audit:read", "audit:export",
    "config:read", "config:write",
    "company:read", "company:write", "company:delete",
    "company_user:read", "company_user:write", "company_user:delete",
    "document:read", "document:write", "document:approve", "document:delete",
    "quality_event:read", "quality_event:write",
    "capa:read", "capa:write", "capa:approve",
    "training:read", "training:write", "training:assign",
    "equipment:read", "equipment:write",
    "plate:read", "plate:write",
    "job:read", "job:write",
    "qa_review:read", "qa_review:write", "qa_review:approve",
    "crm:read", "crm:write",
    "contract:read", "contract:write",
    "workorder:read", "workorder:write",
    "certificate:read", "certificate:write", "certificate:issue",
    "billing:read", "billing:write",
    "report:read", "report:generate",
    "analytics:read",
  ],
  tenant_user: [
    "document:read",
    "quality_event:read",
    "capa:read",
    "training:read",
    "equipment:read",
    "plate:read",
    "job:read",
    "qa_review:read",
    "crm:read",
    "contract:read",
    "workorder:read",
    "certificate:read",
    "report:read",
    "analytics:read",
  ],
  company_admin: [
    "company:read",
    "company_user:read", "company_user:write", "company_user:delete",
    "role:read", "role:write",
    "audit:read",
    "document:read", "document:write", "document:approve", "document:delete",
    "quality_event:read", "quality_event:write",
    "capa:read", "capa:write", "capa:approve",
    "training:read", "training:write", "training:assign",
    "equipment:read", "equipment:write",
    "plate:read", "plate:write",
    "job:read", "job:write",
    "qa_review:read", "qa_review:write", "qa_review:approve",
    "crm:read", "crm:write",
    "contract:read", "contract:write",
    "workorder:read", "workorder:write", "workorder:execute",
    "certificate:read", "certificate:write", "certificate:issue",
    "billing:read",
    "report:read", "report:generate",
    "analytics:read",
  ],
  company_user: [
    "document:read",
    "quality_event:read",
    "capa:read",
    "training:read",
    "equipment:read",
    "plate:read",
    "job:read",
    "qa_review:read",
    "crm:read",
    "contract:read",
    "workorder:read",
    "certificate:read",
    "report:read",
    "analytics:read",
  ],
};

interface UsePermissionReturn {
  role: Role | null;
  hasPermission: (permission: Permission) => boolean;
  hasAnyPermission: (permissions: Permission[]) => boolean;
  hasAllPermissions: (permissions: Permission[]) => boolean;
  isSuperAdmin: boolean;
  isTenantAdmin: boolean;
  isCompanyAdmin: boolean;
  isCompanyUser: boolean;
  isLoading: boolean;
}

export function usePermission(): UsePermissionReturn {
  const { data: session, status } = useSession();

  const role = useMemo(() => {
    if (!session?.user) return null;
    const r = session.user.role as Role | undefined;
    return r ?? "tenant_user";
  }, [session]);

  const permissions = useMemo(() => {
    if (!role) return new Set<Permission>();
    return new Set(ROLE_PERMISSIONS[role] ?? []);
  }, [role]);

  const hasPermission = (permission: Permission) => permissions.has(permission);
  const hasAnyPermission = (perms: Permission[]) => perms.some((p) => permissions.has(p));
  const hasAllPermissions = (perms: Permission[]) => perms.every((p) => permissions.has(p));

  return {
    role,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    isSuperAdmin: role === "super_admin",
    isTenantAdmin: role === "tenant_admin" || role === "super_admin",
    isCompanyAdmin: role === "company_admin",
    isCompanyUser: role === "company_user",
    isLoading: status === "loading",
  };
}
