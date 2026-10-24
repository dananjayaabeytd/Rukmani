"use client";

/**
 * The chat list: "New chat", the visitor's chats (open, rename, delete) and
 * a link to what Rukmani remembers. Deep Kapruka purple, so together with
 * the header it frames the conversation.
 *
 * Desktop: a column that collapses to a slim rail of icons (remembered in
 * the browser). Phones: a slide-in panel, opened from the header's menu button.
 */

import { AnimatePresence, motion } from "motion/react";
import { Brain, MessageSquarePlus, PanelLeftClose, PanelLeftOpen, X } from "lucide-react";
import { useLanguage } from "@/components/LanguageProvider";
import type { ChatSummary } from "@/lib/types";
import { ChatListItem } from "./ChatListItem";

interface SidebarProps {
  chats: ChatSummary[];
  activeChatId: string | null;
  onSelect: (chatId: string) => void;
  onNewChat: () => void;
  onRename: (chatId: string, title: string) => void;
  onDelete: (chatId: string) => void;
  onOpenMemory: () => void;
  /** Desktop: shrunk to the icon rail. */
  collapsed: boolean;
  onToggleCollapsed: () => void;
  /** Phones only: whether the slide-in panel is showing. */
  mobileOpen: boolean;
  onCloseMobile: () => void;
}

const PANEL = "bg-linear-to-b from-brand-logo via-brand to-brand-deep text-white";

export function Sidebar(props: SidebarProps) {
  const { collapsed, mobileOpen, onCloseMobile } = props;
  const { t } = useLanguage();

  return (
    <>
      {/* Desktop: a column, or a slim rail when collapsed */}
      <motion.aside
        className={`relative z-10 hidden shrink-0 overflow-hidden shadow-xl md:flex md:flex-col ${PANEL}`}
        initial={false}
        animate={{ width: collapsed ? 68 : 288 }}
        transition={{ type: "spring", damping: 30, stiffness: 260 }}
      >
        {collapsed ? <Rail {...props} /> : <SidebarContent {...props} />}
      </motion.aside>

      {/* Phones: slide-in panel */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              className="fixed inset-0 z-40 bg-ink/50 backdrop-blur-sm md:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={onCloseMobile}
            />
            <motion.aside
              role="dialog"
              aria-label={t.yourChats}
              className={`fixed inset-y-0 left-0 z-50 flex w-80 max-w-[85%] flex-col shadow-2xl md:hidden ${PANEL}`}
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 30, stiffness: 300 }}
            >
              <SidebarContent {...props} onToggleCollapsed={onCloseMobile} mobile />
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}

/** The collapsed rail: expand, new chat and memory, as icons. */
function Rail({ onToggleCollapsed, onNewChat, onOpenMemory }: SidebarProps) {
  const { t } = useLanguage();

  return (
    <div className="flex h-full flex-col items-center gap-3 py-4">
      <IconButton label={t.openChats} onClick={onToggleCollapsed}>
        <PanelLeftOpen className="size-5" aria-hidden />
      </IconButton>
      <button
        type="button"
        onClick={onNewChat}
        aria-label={t.newChat}
        title={t.newChat}
        className="flex size-10 items-center justify-center rounded-full bg-sun text-brand shadow-lg shadow-sun/20 transition hover:scale-105"
      >
        <MessageSquarePlus className="size-5" aria-hidden />
      </button>
      <div className="flex-1" />
      <IconButton label={t.memoryButton} onClick={onOpenMemory}>
        <Brain className="size-5" aria-hidden />
      </IconButton>
    </div>
  );
}

function SidebarContent({
  chats,
  activeChatId,
  onSelect,
  onNewChat,
  onRename,
  onDelete,
  onOpenMemory,
  onToggleCollapsed,
  onCloseMobile,
  mobile = false,
}: SidebarProps & { mobile?: boolean }) {
  const { t } = useLanguage();

  // On phones, close the panel after choosing something.
  function andClose(action: () => void) {
    return () => {
      action();
      onCloseMobile();
    };
  }

  return (
    <div className="flex h-full w-72 flex-col gap-3 p-3 max-md:w-full">
      <div className="flex items-center justify-between pt-1 pl-2">
        <p className="text-xs font-semibold tracking-widest text-white/60 uppercase">{t.yourChats}</p>
        <IconButton label={t.closeChats} onClick={onToggleCollapsed}>
          {mobile ? <X className="size-5" aria-hidden /> : <PanelLeftClose className="size-5" aria-hidden />}
        </IconButton>
      </div>

      <button
        type="button"
        onClick={andClose(onNewChat)}
        className="flex items-center justify-center gap-2 rounded-xl bg-sun py-2.5 text-sm font-semibold text-brand shadow-lg shadow-sun/20 transition hover:-translate-y-0.5 hover:brightness-105"
      >
        <MessageSquarePlus className="size-4" aria-hidden />
        {t.newChat}
      </button>

      <nav className="-mx-1 mt-1 flex-1 overflow-y-auto px-1">
        {chats.length === 0 ? (
          <p className="px-2 py-4 text-sm text-white/60">{t.noChats}</p>
        ) : (
          <ul className="flex flex-col gap-1">
            {chats.map((chat) => (
              <li key={chat.id}>
                <ChatListItem
                  chat={chat}
                  active={chat.id === activeChatId}
                  onSelect={andClose(() => onSelect(chat.id))}
                  onRename={(title) => onRename(chat.id, title)}
                  onDelete={() => onDelete(chat.id)}
                />
              </li>
            ))}
          </ul>
        )}
      </nav>

      <button
        type="button"
        onClick={andClose(onOpenMemory)}
        className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2.5 text-sm text-white/85 transition hover:bg-white/10 hover:text-white"
      >
        <Brain className="size-4 text-sun" aria-hidden />
        {t.memoryButton}
      </button>
    </div>
  );
}

function IconButton({
  label,
  onClick,
  children,
}: {
  label: string;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      title={label}
      className="rounded-xl p-2 text-white/75 transition hover:bg-white/10 hover:text-white"
    >
      {children}
    </button>
  );
}
