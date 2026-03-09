import { useState } from "react"
import { Settings, Save, Trash2 } from "lucide-react"
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
import { api } from "@/lib/api"

interface SubscriptionSettingsDialogProps {
    subscription: any
    onUpdate?: () => void
}

export function SubscriptionSettingsDialog({ subscription, onUpdate }: SubscriptionSettingsDialogProps) {
    const [open, setOpen] = useState(false)
    const [frequency, setFrequency] = useState(subscription.frequency)
    const [title, setTitle] = useState(subscription.title)
    const [saving, setSaving] = useState(false)
    const [deleting, setDeleting] = useState(false)

    const handleSave = async () => {
        setSaving(true)
        try {
            await api.updateSubscription(subscription.id, {
                title,
                frequency
            })
            setOpen(false)
            onUpdate?.()
        } catch (error: any) {
            alert(error.message || '更新失败')
        } finally {
            setSaving(false)
        }
    }

    const handleDelete = async () => {
        if (!confirm('确定要删除这个订阅源吗?')) return

        setDeleting(true)
        try {
            await api.deleteSubscription(subscription.id)
            setOpen(false)
            onUpdate?.()
        } catch (error: any) {
            alert(error.message || '删除失败')
        } finally {
            setDeleting(false)
        }
    }

    const handleFetch = async () => {
        try {
            // Trigger manual fetch
            alert('手动抓取功能暂未实现')
        } catch (error: any) {
            alert(error.message || '抓取失败')
        }
    }

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 transition-colors">
                    <Settings className="h-4 w-4" />
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Subscription Settings</DialogTitle>
                    <DialogDescription>
                        Configure settings for {subscription.title}.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div>
                        <label className="text-sm font-medium text-zinc-700">Title</label>
                        <Input
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            className="mt-1"
                        />
                    </div>

                    <div>
                        <label className="text-sm font-medium text-zinc-700">Frequency</label>
                        <select
                            value={frequency}
                            onChange={(e) => setFrequency(e.target.value)}
                            className="mt-1 flex h-10 w-full items-center justify-between rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 shadow-sm outline-none focus:ring-1 focus:ring-zinc-900"
                        >
                            <option value="Daily">Daily</option>
                            <option value="Weekly">Weekly</option>
                            <option value="Manual">Manual</option>
                        </select>
                    </div>

                    <div>
                        <label className="text-sm font-medium text-zinc-700">URL</label>
                        <Input
                            value={subscription.url}
                            disabled
                            className="mt-1 bg-zinc-50"
                        />
                    </div>

                    <div className="pt-2">
                        <Button
                            variant="outline"
                            onClick={handleFetch}
                            className="w-full"
                        >
                            Fetch Now
                        </Button>
                    </div>
                </div>
                <DialogFooter className="flex justify-between">
                    <Button
                        variant="destructive"
                        onClick={handleDelete}
                        disabled={deleting}
                        className="mr-auto"
                    >
                        {deleting ? 'Deleting...' : <><Trash2 className="h-4 w-4 mr-2" /> Delete</>}
                    </Button>
                    <div className="flex gap-2">
                        <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
                        <Button onClick={handleSave} disabled={saving}>
                            {saving ? 'Saving...' : <><Save className="h-4 w-4 mr-2" /> Save</>}
                        </Button>
                    </div>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
