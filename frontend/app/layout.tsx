import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "InsightOS",
  description: "AI investment research workspace skeleton"
};

export default function RootLayout({
  children
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <head>
        {/* The in-app preview can block Next's /_next/static/css path; this public CSS keeps previews styled. */}
        {/* eslint-disable-next-line @next/next/no-css-tags */}
        <link href="/insightos.css" rel="stylesheet" />
      </head>
      <body>{children}</body>
    </html>
  );
}
