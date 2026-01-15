import type { Metadata } from "next";
import "./globals.css";

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
            <body className="antialiased">{children}</body>
        </html>
    );
}
