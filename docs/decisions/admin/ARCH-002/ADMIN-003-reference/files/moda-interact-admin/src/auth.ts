import NextAuth from "next-auth";
import Google from "next-auth/providers/google";

import { prisma } from "@/lib/prisma";
import { assertPlatformAdminAuthConfiguration } from "@/lib/auth/environment";

type GoogleProfile = {
  sub?: unknown;
  email?: unknown;
  email_verified?: unknown;
  name?: unknown;
};

function normaliseEmail(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const email = value.trim().toLowerCase();
  return email && email.includes("@") ? email : null;
}

function stringValue(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

async function authoriseGoogleProfile(rawProfile: unknown): Promise<boolean> {
  const profile = (rawProfile ?? {}) as GoogleProfile;
  const email = normaliseEmail(profile.email);
  const subject = stringValue(profile.sub);
  const displayName = stringValue(profile.name);

  if (!email || !subject || profile.email_verified !== true) return false;

  const admin = await prisma.platformAdmin.findUnique({ where: { email } });
  if (!admin || !admin.active || admin.provider !== "google") return false;

  if (admin.providerSubject && admin.providerSubject !== subject) return false;

  if (!admin.providerSubject) {
    const bound = await prisma.platformAdmin.updateMany({
      where: {
        id: admin.id,
        active: true,
        provider: "google",
        providerSubject: null,
      },
      data: {
        providerSubject: subject,
        displayName: admin.displayName ?? displayName,
        lastLoginAt: new Date(),
      },
    });

    if (bound.count !== 1) {
      const current = await prisma.platformAdmin.findUnique({ where: { id: admin.id } });
      return Boolean(
        current?.active &&
          current.provider === "google" &&
          current.providerSubject === subject,
      );
    }

    return true;
  }

  await prisma.platformAdmin.update({
    where: { id: admin.id },
    data: {
      displayName: admin.displayName ?? displayName,
      lastLoginAt: new Date(),
    },
  });

  return true;
}

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [Google],
  pages: {
    signIn: "/login",
  },
  session: {
    strategy: "jwt",
    maxAge: 8 * 60 * 60,
  },
  callbacks: {
    async signIn({ account, profile }) {
      assertPlatformAdminAuthConfiguration();

      if (account?.provider !== "google") return false;
      return authoriseGoogleProfile(profile);
    },
  },
});
