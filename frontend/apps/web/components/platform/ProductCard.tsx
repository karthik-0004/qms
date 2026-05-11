"use client";

import type { Route } from "next";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { ArrowRight, FlaskConical, Shield, Wrench, type LucideIcon } from "lucide-react";
import { motion } from "framer-motion";
import { useUIStore } from "@/lib/stores/ui.store";

interface ProductStat {
  label: string;
  value: string | number;
}

interface Product {
  id: "qms" | "em" | "ccv";
  name: string;
  description: string;
  href: string;
  color: "blue" | "green" | "orange";
  available: boolean;
  stats: ProductStat[];
}

const COLOR_MAP = {
  blue: {
    bg: "bg-blue-50 dark:bg-blue-950/30",
    icon: "bg-blue-600 text-white",
    border: "border-blue-200 dark:border-blue-800/50",
    hover: "hover:border-blue-400 dark:hover:border-blue-600",
    badge: "bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-400",
  },
  green: {
    bg: "bg-emerald-50 dark:bg-emerald-950/30",
    icon: "bg-emerald-600 text-white",
    border: "border-emerald-200 dark:border-emerald-800/50",
    hover: "hover:border-emerald-400 dark:hover:border-emerald-600",
    badge: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-400",
  },
  orange: {
    bg: "bg-orange-50 dark:bg-orange-950/30",
    icon: "bg-orange-600 text-white",
    border: "border-orange-200 dark:border-orange-800/50",
    hover: "hover:border-orange-400 dark:hover:border-orange-600",
    badge: "bg-orange-100 text-orange-700 dark:bg-orange-900/50 dark:text-orange-400",
  },
} as const;

const PRODUCT_ICON_MAP: Record<Product["id"], LucideIcon> = {
  qms: Shield,
  em: FlaskConical,
  ccv: Wrench,
};

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  const { setActiveProduct } = useUIStore();
  const colors = COLOR_MAP[product.color];
  const IconComponent = PRODUCT_ICON_MAP[product.id];

  if (!product.available) {
    return (
      <div
        className={cn(
          "rounded-xl border p-6 bg-muted/30 opacity-50 cursor-not-allowed",
          colors.border
        )}
      >
        <div className="flex items-start gap-4">
          <div className={cn("p-3 rounded-xl", colors.icon)}>
            <IconComponent size={24} />
          </div>
          <div>
            <h3 className="font-semibold text-foreground">{product.name}</h3>
            <p className="text-sm text-muted-foreground mt-1">
              Not available in your plan
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      whileHover={{ y: -2 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <Link
        href={product.href as Route}
        onClick={() => setActiveProduct(product.id)}
        className={cn(
          "block rounded-xl border p-6 transition-all duration-200 group",
          colors.bg,
          colors.border,
          colors.hover,
          "hover:shadow-md"
        )}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className={cn("p-3 rounded-xl shrink-0", colors.icon)}>
              <IconComponent size={24} />
            </div>
            <div>
              <h3 className="font-semibold text-foreground">{product.name}</h3>
              <p className="text-sm text-muted-foreground mt-1 leading-relaxed">
                {product.description}
              </p>
            </div>
          </div>
          <ArrowRight
            size={18}
            className="shrink-0 text-muted-foreground group-hover:text-foreground group-hover:translate-x-1 transition-all"
          />
        </div>

        <div className="mt-6 grid grid-cols-3 gap-3">
          {product.stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-lg font-bold text-foreground">{stat.value}</div>
              <div className="text-xs text-muted-foreground mt-0.5">{stat.label}</div>
            </div>
          ))}
        </div>
      </Link>
    </motion.div>
  );
}
