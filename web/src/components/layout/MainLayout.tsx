"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { useAuth } from "@/lib/auth-context";

export function MainLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const router = useRouter();
    const { user, isLoading, isAuthenticated } = useAuth();

    const isPublic = pathname === "/login" || pathname === "/register" || pathname.startsWith("/auth");

    useEffect(() => {
        if (!isLoading) {
            if (!isAuthenticated && !isPublic) {
                router.push("/login");
            } else if (isAuthenticated && isPublic) {
                router.push("/");
            }
        }
    }, [isLoading, isAuthenticated, isPublic, router]);

    if (isLoading) {
        return (
            <div className="flex h-screen items-center justify-center bg-background">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
        );
    }

    if (isPublic) {
        return <div className="min-h-screen bg-background">{children}</div>;
    }

    if (!isAuthenticated) {
        return null; // Will redirect via useEffect
    }

    return (
        <div className="flex h-screen bg-background overflow-hidden">
            <Sidebar />
            <main className="flex-1 overflow-y-auto min-h-0 relative">
                {children}
            </main>
        </div>
    )
}
