import Image from "next/image";
import Link from "next/link";

import { LogoutForm } from "./logout-form";
import { Icon } from "./icons";

export function Sidebar({ active }: { active: "tenants" | "observability" }) {
  const base = "flex items-center px-3 py-2.5 rounded-lg font-medium transition-colors";
  const selected = "bg-white text-[var(--brand-900)] shadow-sm border border-[var(--brand-200)]";
  const idle = "text-[var(--brand-800)] hover:bg-white/60";

  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-[var(--brand-200)] bg-[var(--brand-100)] md:flex">
      <div className="flex h-16 items-center border-b border-[var(--brand-200)] px-6">
        <Image
          src="/moda-interact-logo.jpg"
          alt="Moda Interact"
          width={32}
          height={32}
          className="h-8 w-8 rounded-md object-cover shadow-sm"
          priority
        />
        <span className="ml-3 text-lg font-bold tracking-tight text-[var(--brand-900)]">Moda Interact</span>
      </div>
      <nav className="flex-1 space-y-2 px-4 py-6" aria-label="Administration navigation">
        <Link href="/" className={`${base} ${active === "tenants" ? selected : idle}`}>
          <Icon name="users" className="mr-3 h-5 w-5 text-[var(--brand-700)]" />
          Tenant Directory
        </Link>
        <Link href="/observability" className={`${base} ${active === "observability" ? selected : idle}`}>
          <Icon name="chart" className="mr-3 h-5 w-5 text-[var(--brand-600)]" />
          Observability
        </Link>
      </nav>
      <div className="border-t border-[var(--brand-200)] p-4">
        <LogoutForm />
      </div>
    </aside>
  );
}
