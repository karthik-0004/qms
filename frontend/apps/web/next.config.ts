import type { NextConfig } from "next";
import path from "node:path";
import { fileURLToPath } from "node:url";

/** App directory — avoids Turbopack picking a parent folder (e.g. user home) when multiple lockfiles exist. */
const turbopackRoot = path.dirname(fileURLToPath(import.meta.url));

const nextConfig: NextConfig = {
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
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: "/api/platform/:path*",
        destination: `${apiUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
