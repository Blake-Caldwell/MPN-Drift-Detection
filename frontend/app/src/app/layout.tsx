import type { Metadata } from "next";
import { Inter as FontSans} from "next/font/google";
import "./globals.css";

const fontSans = FontSans({
  subsets: ["latin"],
  variable: "--font-sans",
})

export const metadata: Metadata = {
  title: "MPN Visuals",
  description: "MPN model visualization for idoba",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${fontSans.className} bg-gradient-to-br from-slate-500 to-slate-800 text-white min-h-screen cn(
          "min-h-screen bg-background font-sans antialiased",
          fontSans.variable
        )`}>
        {children}
      </body>
    </html>
  );
}