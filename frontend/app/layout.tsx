import type { Metadata, Viewport } from "next";
import { Noto_Sans_Sinhala, Noto_Sans_Tamil, Roboto } from "next/font/google";
import "./globals.css";

// Roboto is Kapruka's own font. Noto Sans Sinhala and Noto Sans Tamil render
// those scripts cleanly; the browser picks the right one per character.
const roboto = Roboto({ subsets: ["latin"], variable: "--font-roboto" });
const sinhala = Noto_Sans_Sinhala({ subsets: ["sinhala"], variable: "--font-sinhala" });
const tamil = Noto_Sans_Tamil({ subsets: ["tamil"], variable: "--font-tamil" });

export const metadata: Metadata = {
  title: "Rukmani · Kapruka gift concierge",
  description:
    "Find the perfect gift on Kapruka by chatting in Sinhala, Tamil, Singlish, Tanglish or English.",
};

export const viewport: Viewport = {
  themeColor: "#442a73",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${roboto.variable} ${sinhala.variable} ${tamil.variable}`}>
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
