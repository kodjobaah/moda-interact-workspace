import { PrismaClient, PlatformAdminRole } from "@prisma/client";

const prisma = new PrismaClient();

function argument(name) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

function hasFlag(name) {
  return process.argv.includes(`--${name}`);
}

function normaliseEmail(value) {
  const email = String(value ?? "").trim().toLowerCase();
  if (!email || !email.includes("@")) {
    throw new Error("--email must contain a valid administrator email address.");
  }
  return email;
}

async function main() {
  const email = normaliseEmail(argument("email"));

  if (hasFlag("disable")) {
    const existing = await prisma.platformAdmin.findUnique({ where: { email } });
    if (!existing) throw new Error(`No PlatformAdmin exists for ${email}.`);

    const disabled = await prisma.platformAdmin.update({
      where: { email },
      data: { active: false },
      select: { id: true, email: true, role: true, active: true },
    });

    console.log(JSON.stringify(disabled, null, 2));
    console.log("Administrator disabled. No credential material was changed or stored.");
    return;
  }

  const rawRole = String(argument("role") ?? "ADMIN").trim().toUpperCase();
  if (!Object.values(PlatformAdminRole).includes(rawRole)) {
    throw new Error(`--role must be one of: ${Object.values(PlatformAdminRole).join(", ")}`);
  }

  const admin = await prisma.platformAdmin.upsert({
    where: { email },
    create: {
      email,
      provider: "google",
      role: rawRole,
      active: true,
    },
    update: {
      role: rawRole,
      active: true,
    },
    select: {
      id: true,
      email: true,
      provider: true,
      providerSubject: true,
      role: true,
      active: true,
    },
  });

  console.log(JSON.stringify(admin, null, 2));
  console.log("No password or OAuth credential was stored.");
}

main()
  .catch((error) => {
    console.error(error instanceof Error ? error.message : "Platform admin provisioning failed.");
    process.exitCode = 1;
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
