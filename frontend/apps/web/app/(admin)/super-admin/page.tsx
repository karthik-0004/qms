// Renders the admin dashboard at the /super-admin URL.
// (admin)/layout.tsx guards authentication. The rewrite in next.config.ts
// maps /super-admin/:path+ → /admin/:path+ for all sub-pages; this file
// handles the root /super-admin entry point.
export { default } from "../admin/page";
