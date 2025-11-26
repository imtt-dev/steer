import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { FontLoader } from "@/components/font-loader";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Steer Mission Control",
  description: "Smoke & Mirrors Demo - AI Agent Mission Control",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} font-sans antialiased`}
        style={{
          fontFamily: 'var(--font-inter), system-ui, sans-serif',
        }}
      >
        <FontLoader />
        {children}
      </body>
    </html>
  );
}
