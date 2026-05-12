import type { NextConfig } from "next";
import path from "node:path";
import { fileURLToPath } from "node:url";

/** App directory — avoids Turbopack picking a parent folder (e.g. user home) when multiple lockfiles exist. */
const turbopackRoot = path.dirname(fileURLToPath(import.meta.url));

const nextConfig: NextConfig = {
  output: "standalone",
  turbopack: {
    root: turbopackRoot,
  },
  typedRoutes: true,
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.rainer.io" },
      { protocol: "http", hostname: "localhost" },
    ],
  },

  async redirects() {
    return [
      // Old /login → new /signin (backwards-compat)
      {
        source: "/login",
        destination: "/signin",
        permanent: false,
      },
      // Old /admin panel → new /super-admin panel
      {
        source: "/admin",
        destination: "/super-admin",
        permanent: false,
      },
      {
        source: "/admin/:path+",
        destination: "/super-admin/:path+",
        permanent: false,
      },
    ];
  },

  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return {
      // afterFiles: run AFTER file-system page matching.
      // /super-admin/:path+ only rewrites when no file matches (e.g. /super-admin/tenants/*
      // has no page file, so it falls through to the existing /admin/* pages).
      // /super-admin/signin IS matched by a file, so this rewrite never fires for it.
      afterFiles: [
        {
          source: "/super-admin/:path+",
          destination: "/admin/:path+",
        },
      ],
      beforeFiles: [],
      fallback: [
        {
          source: "/api/platform/:path*",
          destination: `${apiUrl}/api/v1/:path*`,
        },
      ],
    };
  },
};

export default nextConfig;
