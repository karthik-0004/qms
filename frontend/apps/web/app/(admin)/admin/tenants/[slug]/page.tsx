import { TenantDetailView } from "./tenant-detail-view";

export default async function AdminTenantBySlugPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return <TenantDetailView slug={slug} />;
}
