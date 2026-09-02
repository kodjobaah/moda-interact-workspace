import { signOut } from "@/auth";
import { isDevelopmentAuthBypass } from "@/lib/auth/environment";

export function LogoutForm() {
  if (isDevelopmentAuthBypass()) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-medium text-amber-900">
        Development mode · authentication bypassed
      </div>
    );
  }

  async function logout() {
    "use server";
    await signOut({ redirectTo: "/login" });
  }

  return (
    <form action={logout}>
      <button
        type="submit"
        className="w-full rounded-lg border border-[var(--brand-300)] bg-white px-3 py-2 text-left text-sm font-medium text-[var(--brand-900)] hover:bg-[var(--brand-50)]"
      >
        Sign out
      </button>
    </form>
  );
}
