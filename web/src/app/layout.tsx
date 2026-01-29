import type { Metadata } from "next";
import "./globals.css";
import 'katex/dist/katex.min.css';
import { MainLayout } from "@/components/layout/MainLayout";

export const metadata: Metadata = {
    title: "Deli Admin",
    description: "Manage your knowledge quizzes",
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body className="antialiased">
                <MainLayout>{children}</MainLayout>
            </body>
        </html>
    );
}
