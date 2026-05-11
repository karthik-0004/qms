import TenantSettingsForm from "./tenant-settings-form";

export default async function AdminTenantSettingsPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  return <TenantSettingsForm slug={slug} />;
}
