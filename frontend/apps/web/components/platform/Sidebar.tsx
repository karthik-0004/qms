"use client";

import type { Session } from "next-auth";
import type { Route } from "next";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  FileText,
  AlertTriangle,
  ClipboardList,
  GraduationCap,
  Wrench,
  FlaskConical,
  BookOpen,
  Briefcase,
  FileCheck,
  Settings,
  ChevronLeft,
  Shield,
  BarChart3,
  Users,
  HardHat,
  DollarSign,
  Crown,
  Building2,
} from "lucide-react";
import { useUIStore } from "@/lib/stores/ui.store";

const QMS_NAV = [
  { href: "/qms/documents", icon: FileText, label: "Documents" },
  { href: "/qms/quality-events", icon: AlertTriangle, label: "Quality Events" },
  { href: "/qms/capa", icon: ClipboardList, label: "CAPA" },
  { href: "/qms/training", icon: GraduationCap, label: "Training" },
  { href: "/qms/training/my-training", icon: BookOpen, label: "My training" },
  { href: "/qms/equipment", icon: Wrench, label: "Equipment" },
  { href: "/qms/analytics", icon: BarChart3, label: "Analytics" },
];

const EM_NAV = [
  { href: "/em/plates", icon: FlaskConical, label: "Plates" },
  { href: "/em/jobs", icon: ClipboardList, label: "Jobs" },
  { href: "/em/analytics", icon: BarChart3, label: "Analytics" },
];

const CCV_NAV = [
  { href: "/ccv/crm", icon: Briefcase, label: "CRM" },
  { href: "/ccv/contracts", icon: FileCheck, label: "Contracts" },
  { href: "/ccv/work-orders", icon: ClipboardList, label: "Work Orders" },
  { href: "/ccv/technicians", icon: HardHat, label: "Technicians" },
  { href: "/ccv/billing", icon: DollarSign, label: "Billing" },
  { href: "/ccv/certificates", icon: Shield, label: "Certificates" },
  { href: "/ccv/analytics", icon: BarChart3, label: "Analytics" },
];

interface NavEntry {
  href: string;
  icon: React.ElementType;
  label: string;
}

function getPlatformNav(role: string, companyId: string | null): NavEntry[] {
  const items: NavEntry[] = [{ href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" }];

  if (role === "tenant_admin") {
    items.push({ href: "/settings/users", icon: Users, label: "Users" });
    items.push({ href: "/settings/companies", icon: Building2, label: "Companies" });
  } else if (role === "company_admin") {
    if (companyId) {
      items.push({
        href: `/settings/companies/${companyId}`,
        icon: Building2,
        label: "My Company",
      });
    }
  }

  items.push({ href: "/settings", icon: Settings, label: "Settings" });
  return items;
}

interface SidebarProps {
  session: Session;
}

export function Sidebar({ session }: SidebarProps) {
  const pathname = usePathname();
  const { sidebarCollapsed, setSidebarCollapsed, activeProduct } = useUIStore();

  const userRole = session.user.role;
  const isSuperAdmin = userRole === "super_admin";

  const platformNavItems = isSuperAdmin
    ? [{ href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" }]
    : getPlatformNav(userRole, session.user.company_id ?? null);

  const productNav =
    activeProduct === "qms"
      ? QMS_NAV
      : activeProduct === "em"
        ? EM_NAV
        : activeProduct === "ccv"
          ? CCV_NAV
          : [];

  return (
    <aside
      className={cn(
        "flex flex-col bg-slate-900 text-white border-r border-slate-800 transition-all duration-200",
        sidebarCollapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b border-slate-800">
        {!sidebarCollapsed && (
          <span className="text-lg font-bold text-white truncate">
            Rainer Platform
          </span>
        )}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className={cn(
            "ml-auto p-1.5 rounded-lg hover:bg-slate-800 transition",
            sidebarCollapsed && "mx-auto"
          )}
        >
          <ChevronLeft
            size={18}
            className={cn("transition-transform", sidebarCollapsed && "rotate-180")}
          />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 space-y-1 px-2">
        {platformNavItems.map((item) => (
          <NavItem
            key={item.href}
            href={item.href as Route}
            icon={item.icon}
            label={item.label}
            isActive={pathname.startsWith(item.href) && (item.href !== "/dashboard" || pathname === "/dashboard")}
            collapsed={sidebarCollapsed}
          />
        ))}

        {isSuperAdmin && (
          <>
            <div className="my-3 border-t border-slate-700" />
            <NavItem
              href={"/super-admin/tenants" as Route}
              icon={Building2}
              label="Tenants"
              isActive={pathname.startsWith("/super-admin/tenants")}
              collapsed={sidebarCollapsed}
            />
            <NavItem
              href={"/super-admin" as Route}
              icon={Crown}
              label="Platform admin"
              isActive={pathname === "/super-admin"}
              collapsed={sidebarCollapsed}
              highlight
            />
          </>
        )}

        {!isSuperAdmin && productNav.length > 0 && (
          <>
            <div className="my-3 border-t border-slate-700" />
            {productNav.map((item) => (
              <NavItem
                key={item.href}
                href={item.href as Route}
                icon={item.icon}
                label={item.label}
                isActive={pathname.startsWith(item.href)}
                collapsed={sidebarCollapsed}
              />
            ))}
          </>
        )}
      </nav>

      {/* User info */}
      {!sidebarCollapsed && (
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-sm font-medium">
              {session.user?.email?.charAt(0).toUpperCase() ?? "U"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {session.user?.email ?? ""}
              </p>
              <p className="text-xs text-slate-400 truncate">{session.user.role}</p>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}

function NavItem({
  href,
  icon: Icon,
  label,
  isActive,
  collapsed,
  highlight = false,
}: {
  href: Route;
  icon: React.ElementType;
  label: string;
  isActive: boolean;
  collapsed: boolean;
  highlight?: boolean;
}) {
  return (
    <Link
      href={href}
      title={collapsed ? label : undefined}
      className={cn(
        "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
        isActive
          ? highlight
            ? "bg-red-600 text-white"
            : "bg-blue-600 text-white"
          : highlight
            ? "text-red-400 hover:bg-red-900/30 hover:text-red-300"
            : "text-slate-400 hover:bg-slate-800 hover:text-white",
        collapsed && "justify-center px-2"
      )}
    >
      <Icon size={18} className="shrink-0" />
      {!collapsed && <span className="truncate">{label}</span>}
    </Link>
  );
}
