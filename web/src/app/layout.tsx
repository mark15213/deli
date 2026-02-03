import type { Metadata } from "next";
import "./globals.css";
import 'katex/dist/katex.min.css';
import { MainLayout } from "@/components/layout/MainLayout";
import { AuthProvider } from "@/lib/auth-context";

export const metadata: Metadata = {
    title: "Gulp",
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
                <AuthProvider>
                    <MainLayout>{children}</MainLayout>
                </AuthProvider>
            </body>
        </html>
    );
}
