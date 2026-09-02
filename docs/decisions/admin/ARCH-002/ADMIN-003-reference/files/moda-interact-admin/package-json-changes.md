# package.json changes

Pin Auth.js exactly during `ADMIN-003` after compatibility validation with the
current Next.js 16 runtime. The architecture reference was prepared against the
current Auth.js v5 API.

At the time this reference was prepared, the current v5 beta published tag was:

```json
"next-auth": "5.0.0-beta.32"
```

Add a provisioning command:

```json
"admin:provision": "node scripts/provision-platform-admin.mjs"
```

During `ADMIN-007`, also consume the accepted shared logger exactly:

```json
"@modainteract/moda-interact-shared": "0.3.0"
```

Do not hand-edit package-lock entries. Use npm and commit the resulting lockfile.

Provision/enable an administrator after the database migration is deployed:

```bash
npm run admin:provision -- --email admin@example.com --role SUPER_ADMIN
```

Disable an administrator immediately:

```bash
npm run admin:provision -- --email admin@example.com --disable
```
