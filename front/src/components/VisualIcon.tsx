import {
  BookOpen, FileText, LayoutTemplate, Library, LogOut, MessageSquare,
  Search, Trash2, UserRound,
} from 'lucide-react'

const icons = {
  note: FileText, review: BookOpen, template: LayoutTemplate, folder: Library,
  logout: LogOut, chat: MessageSquare, search: Search, trash: Trash2, user: UserRound,
}

export default function VisualIcon({
  name, size = 20, className,
}: { name: keyof typeof icons; size?: number; className?: string }) {
  const Icon = icons[name]
  return <Icon size={size} strokeWidth={1.8} className={className} aria-hidden="true" />
}
