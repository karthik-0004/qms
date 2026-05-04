import { redirect } from "next/navigation";

import { getCachedSession } from "@/lib/auth/get-cached-session";



export default async function QMSLayout({

  children,

}: {

  children: React.ReactNode;

}) {

  const session = await getCachedSession();

  if (!session?.user) redirect("/login");



  return <>{children}</>;

}

