# Route move plan

After adding `(protected)/layout.tsx`, move the existing privileged pages:

```text
src/app/page.tsx
    -> src/app/(protected)/page.tsx

src/app/observability/page.tsx
    -> src/app/(protected)/observability/page.tsx
```

Next.js route groups do not change the public URL, so the URLs remain:

```text
/
/observability
```

Do not leave both old and new page files in place; that creates duplicate route
ownership.

Do not move:

```text
src/app/login/page.tsx
src/app/api/auth/[...nextauth]/route.ts
src/app/api/health/*
```

Health/readiness routes needed by infrastructure remain outside the privileged
page layout and must remain data-minimal.

The reference protected page files also call `requirePlatformAdminPage()` directly, and `src/lib/admin/data.ts` calls `requirePlatformAdminRead()` in every exported privileged data function. The layout is defence in depth, not the sole data-access security boundary.
