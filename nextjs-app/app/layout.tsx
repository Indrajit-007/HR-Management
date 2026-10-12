import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG-MCP Assistant",
  description: "An intelligent assistant for employee data, policies, and announcements.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
