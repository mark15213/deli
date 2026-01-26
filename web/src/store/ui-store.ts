import { create } from "zustand";

interface UIState {
    // Sidebar state
    sidebarOpen: boolean;
    setSidebarOpen: (open: boolean) => void;
    toggleSidebar: () => void;

    // Active module
    activeModule: "sources" | "inbox" | "study";
    setActiveModule: (module: "sources" | "inbox" | "study") => void;

    // Selected items
    selectedSourceId: string | null;
    setSelectedSourceId: (id: string | null) => void;

    selectedInboxItemId: string | null;
    setSelectedInboxItemId: (id: string | null) => void;

    // Slide-over state
    slideOverOpen: boolean;
    slideOverContent: "source-detail" | "quick-add" | null;
    openSlideOver: (content: "source-detail" | "quick-add") => void;
    closeSlideOver: () => void;

    // Command palette (Cmd+K)
    commandPaletteOpen: boolean;
    setCommandPaletteOpen: (open: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
    // Sidebar
    sidebarOpen: true,
    setSidebarOpen: (open) => set({ sidebarOpen: open }),
    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

    // Active module
    activeModule: "sources",
    setActiveModule: (module) => set({ activeModule: module }),

    // Selected items
    selectedSourceId: null,
    setSelectedSourceId: (id) => set({ selectedSourceId: id }),

    selectedInboxItemId: null,
    setSelectedInboxItemId: (id) => set({ selectedInboxItemId: id }),

    // Slide-over
    slideOverOpen: false,
    slideOverContent: null,
    openSlideOver: (content) => set({ slideOverOpen: true, slideOverContent: content }),
    closeSlideOver: () => set({ slideOverOpen: false, slideOverContent: null }),

    // Command palette
    commandPaletteOpen: false,
    setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
}));
