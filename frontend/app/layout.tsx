import type { Metadata, Viewport } from "next";
import { Noto_Sans_Sinhala, Roboto } from "next/font/google";
import "./globals.css";

// Roboto is Kapruka's own font. Noto Sans Sinhala renders Sinhala script cleanly.
const roboto = Roboto({ subsets: ["latin"], variable: "--font-roboto" });
const sinhala = Noto_Sans_Sinhala({ subsets: ["sinhala"], variable: "--font-sinhala" });

export const metadata: Metadata = {
  title: "Rukmani · Kapruka gift concierge",
  description:
    "Find the perfect gift on Kapruka by chatting in Sinhala, Singlish or English.",
};

export const viewport: Viewport = {
  themeColor: "#402970",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${roboto.variable} ${sinhala.variable}`}>
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
