import TenantEditForm from "./tenant-edit-form";

export default async function AdminTenantEditPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return <TenantEditForm slug={slug} />;
}
