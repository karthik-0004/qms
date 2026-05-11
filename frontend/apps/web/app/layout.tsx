import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { getCachedSession } from "@/lib/auth/get-cached-session";
import { AppSessionProvider } from "@/components/providers/AppSessionProvider";
import { Toaster } from "sonner";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { ThemeProvider } from "@/components/providers/ThemeProvider";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: {
    default: "Rainer Platform",
    template: "%s | Rainer Platform",
  },
  description: "Enterprise Quality Management & Compliance Platform",
  icons: { icon: "/favicon.ico" },
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getCachedSession();

  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <AppSessionProvider session={session}>
          <QueryProvider>
            <ThemeProvider>
              {children}
              <Toaster position="top-right" richColors closeButton />
            </ThemeProvider>
          </QueryProvider>
        </AppSessionProvider>
      </body>
    </html>
  );
}
