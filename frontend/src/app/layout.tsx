import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Syncora",
  description: "Collaborative rich-text editor",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`h-full antialiased font-sans`}
    >
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
