"use client";

import { useState } from "react";
import { getSession, signIn, signOut } from "next-auth/react";
import { useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { motion } from "framer-motion";
import Link from "next/link";

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

const mfaSchema = z.object({
  mfa_code: z
    .string()
    .trim()
    .regex(/^\d{6}$/, "MFA code must be exactly 6 digits"),
});

type LoginFormData = z.infer<typeof loginSchema>;
type MFAFormData = z.infer<typeof mfaSchema>;

function signInFailureMessage(code: string | undefined): string {
  switch (code) {
    case "auth_timeout":
      return "Sign-in timed out waiting for the auth service. Check that it is running and AUTH_SERVICE_URL in .env.local.";
    case "auth_unreachable":
      return "Could not reach the auth service. Confirm AUTH_SERVICE_URL (e.g. http://localhost:8001 when running auth-service locally).";
    case "auth_misconfigured":
      return "Server is missing AUTH_SERVICE_URL. Set it in .env.local (see .env.example).";
    default:
      return "Invalid email or password";
  }
}

export default function SignInPage() {
  const searchParams = useSearchParams();
  const callbackUrl = searchParams.get("callbackUrl") ?? "/dashboard";

  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [requiresMFA, setRequiresMFA] = useState(false);
  const [savedCredentials, setSavedCredentials] = useState<LoginFormData | null>(null);

  const loginForm = useForm<LoginFormData>({ resolver: zodResolver(loginSchema) });
  const mfaForm = useForm<MFAFormData>({ resolver: zodResolver(mfaSchema) });

  async function handleLogin(data: LoginFormData) {
    setIsLoading(true);
    try {
      const result = await signIn("credentials", {
        ...data,
        redirect: false,
      });

      if (result?.code === "MFA_REQUIRED") {
        setSavedCredentials(data);
        setRequiresMFA(true);
        return;
      }

      if (result?.error) {
        toast.error(signInFailureMessage(result.code ?? undefined));
        return;
      }

      const session = await getSession();
      const role = session?.user?.role;

      if (role === "super_admin") {
        await signOut({ redirect: false });
        toast.error(
          "Super admin accounts must sign in at /super-admin/signin.",
          { duration: 6000 }
        );
        return;
      }

      window.location.href = callbackUrl || "/dashboard";
    } catch {
      toast.error("An unexpected error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleMFA(data: MFAFormData) {
    if (!savedCredentials) return;
    setIsLoading(true);
    try {
      const result = await signIn("credentials", {
        ...savedCredentials,
        mfa_code: data.mfa_code,
        redirect: false,
      });

      if (result?.error) {
        if (
          result.code === "auth_timeout" ||
          result.code === "auth_unreachable" ||
          result.code === "auth_misconfigured"
        ) {
          toast.error(signInFailureMessage(result.code));
        } else {
          toast.error("Invalid MFA code. Please try again.");
        }
        return;
      }

      const session = await getSession();
      const role = session?.user?.role;

      if (role === "super_admin") {
        await signOut({ redirect: false });
        toast.error(
          "Super admin accounts must sign in at /super-admin/signin.",
          { duration: 6000 }
        );
        setRequiresMFA(false);
        setSavedCredentials(null);
        return;
      }

      window.location.href = callbackUrl || "/dashboard";
    } catch {
      toast.error("An unexpected error occurred");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-600 mb-4 shadow-lg shadow-blue-500/25">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white">Rainer Platform</h1>
          <p className="text-slate-400 mt-1 text-sm">
            Enterprise Quality Management
          </p>
        </div>

        {/* Card */}
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
          {!requiresMFA ? (
            <>
              <h2 className="text-xl font-semibold text-white mb-6">Sign in to your account</h2>
              <form onSubmit={loginForm.handleSubmit(handleLogin)} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">
                    Email address
                  </label>
                  <input
                    {...loginForm.register("email")}
                    type="email"
                    autoComplete="email"
                    className="w-full px-4 py-2.5 rounded-lg bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                    placeholder="you@company.com"
                  />
                  {loginForm.formState.errors.email && (
                    <p className="text-red-400 text-xs mt-1">
                      {loginForm.formState.errors.email.message}
                    </p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">
                    Password
                  </label>
                  <div className="relative">
                    <input
                      {...loginForm.register("password")}
                      type={showPassword ? "text" : "password"}
                      autoComplete="current-password"
                      className="w-full px-4 py-2.5 rounded-lg bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition pr-10"
                      placeholder="••••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition"
                    >
                      {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                  {loginForm.formState.errors.password && (
                    <p className="text-red-400 text-xs mt-1">
                      {loginForm.formState.errors.password.message}
                    </p>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isLoading && <Loader2 size={16} className="animate-spin" />}
                  {isLoading ? "Signing in..." : "Sign in"}
                </button>
              </form>
            </>
          ) : (
            <>
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-white">Two-factor authentication</h2>
                <p className="text-slate-400 text-sm mt-1">
                  Enter the 6-digit code from your authenticator app
                </p>
              </div>
              <form onSubmit={mfaForm.handleSubmit(handleMFA)} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">
                    Authentication code
                  </label>
                  <input
                    {...mfaForm.register("mfa_code")}
                    type="text"
                    maxLength={6}
                    autoComplete="one-time-code"
                    inputMode="numeric"
                    className="w-full px-4 py-2.5 rounded-lg bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-center text-2xl tracking-widest"
                    placeholder="000000"
                  />
                  {mfaForm.formState.errors.mfa_code && (
                    <p className="text-red-400 text-xs mt-1">
                      {mfaForm.formState.errors.mfa_code.message}
                    </p>
                  )}
                </div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full py-2.5 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isLoading && <Loader2 size={16} className="animate-spin" />}
                  Verify
                </button>
                <button
                  type="button"
                  onClick={() => { setRequiresMFA(false); setSavedCredentials(null); }}
                  className="w-full text-sm text-slate-400 hover:text-white transition"
                >
                  Back to sign in
                </button>
              </form>
            </>
          )}
        </div>

        <p className="text-center text-slate-500 text-xs mt-4">
          Super admin?{" "}
          <Link href="/super-admin/signin" className="text-slate-400 hover:text-white transition underline underline-offset-2">
            Sign in here
          </Link>
        </p>
        <p className="text-center text-slate-500 text-xs mt-2">
          © {new Date().getFullYear()} RainerTek. All rights reserved.
        </p>
      </motion.div>
    </div>
  );
}
