import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Sidebar } from '@/components/Sidebar';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
  title: "Gulp - Info Flow & Knowledge Platform",
  description: "Consume information, generate knowledge, gulp it down.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable}`}>
      <head>
        {/* KaTeX CSS for rendering math formulas */}
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css"
          integrity="sha384-GvrOXuhMATgEsSwCs4smul74iXGOixntILdUW9XmUC6+HX0sLNAK3q71bZlhw5uS"
          crossOrigin="anonymous"
        />
      </head>
      <body className={`${inter.className} min-h-screen bg-zinc-50 text-zinc-900 antialiased flex relative overflow-hidden font-sans selection:bg-zinc-200`}>
        {/* Background elements */}
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-[0.03] mix-blend-multiply pointer-events-none" />
        <div className="absolute top-[-20%] left-[-10%] w-[70vw] h-[70vw] rounded-full bg-gradient-to-br from-blue-100/40 to-transparent blur-3xl pointer-events-none" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[60vw] h-[60vw] rounded-full bg-gradient-to-tl from-stone-200/50 to-transparent blur-3xl pointer-events-none" />

        <div className="relative z-10 flex w-full h-full">
          <Sidebar />
          <main className="flex-1 flex flex-col h-screen overflow-hidden">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
