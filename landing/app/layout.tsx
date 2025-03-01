// app/layout.tsx or wrap your pages/_app.tsx content
import "./globals.css";
import { Space_Grotesk } from "next/font/google";
import type { Metadata } from "next";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk",
  display: "swap",
  weight: ["300", "400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Meziani - Innovation Platform",
  description: "Join our community of innovators and simplify your workflow",
  keywords: "platform, collaboration, innovation, workflow",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${spaceGrotesk.variable} h-full`}>
      <body className="flex flex-col min-h-screen">{children}</body>
    </html>
  );
}
