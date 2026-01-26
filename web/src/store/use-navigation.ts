import { create } from 'zustand'

export type ViewType = 'sources' | 'inbox' | 'study'
export type StudyType = 'flashcard' | 'audio'

interface NavigationState {
    currentView: ViewType
    setCurrentView: (view: ViewType) => void
    activeInboxId: string | null
    setActiveInboxId: (id: string | null) => void
    activeStudyType: StudyType | null
    setActiveStudyType: (type: StudyType | null) => void
}

export const useNavigationStore = create<NavigationState>((set) => ({
    currentView: 'sources',
    setCurrentView: (view) => set({ currentView: view }),
    activeInboxId: null,
    setActiveInboxId: (id) => set({ activeInboxId: id }),
    activeStudyType: null,
    setActiveStudyType: (type) => set({ activeStudyType: type }),
}))
