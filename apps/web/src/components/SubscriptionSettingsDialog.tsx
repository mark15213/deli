import { useState } from "react"
import { Settings, Save } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"

interface SubscriptionSettingsDialogProps {
    subscription: any;
}

export function SubscriptionSettingsDialog({ subscription }: SubscriptionSettingsDialogProps) {
    const [syncFrequency, setSyncFrequency] = useState("daily")
    const [filterTags, setFilterTags] = useState("")

    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 transition-colors">
                    <Settings className="h-4 w-4" />
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Subscription Settings</DialogTitle>
                    <DialogDescription>
                        Configure sync frequency and filters for {subscription.title}.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                        <label htmlFor="frequency" className="text-right text-sm font-medium text-zinc-700">
                            Frequency
                        </label>
                        <select
                            id="frequency"
                            value={syncFrequency}
                            onChange={(e) => setSyncFrequency(e.target.value)}
                            className="col-span-3 flex h-10 w-full items-center justify-between rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 shadow-sm outline-none focus:ring-1 focus:ring-zinc-900"
                        >
                            <option value="realtime">Real-time</option>
                            <option value="hourly">Hourly</option>
                            <option value="daily">Daily</option>
                            <option value="weekly">Weekly</option>
                        </select>
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                        <label htmlFor="filters" className="text-right text-sm font-medium text-zinc-700">
                            Keywords
                        </label>
                        <Input
                            id="filters"
                            value={filterTags}
                            onChange={(e) => setFilterTags(e.target.value)}
                            placeholder="e.g. AI, Machine Learning"
                            className="col-span-3"
                        />
                    </div>
                </div>
                <DialogFooter>
                    <DialogTrigger asChild>
                        <Button type="submit" className="gap-2">
                            <Save className="h-4 w-4" /> Save changes
                        </Button>
                    </DialogTrigger>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
