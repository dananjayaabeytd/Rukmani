"use client";

/**
 * The chat list: "New chat", the visitor's chats (open, rename, delete) and
 * a link to what Rukmani remembers. A fixed column on desktop; a slide-in
 * panel on phones, opened from the menu button in the header.
 */

import { AnimatePresence, motion } from "motion/react";
import { Brain, MessageSquarePlus, X } from "lucide-react";
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
  /** Phones only: whether the slide-in panel is showing. */
  mobileOpen: boolean;
  onCloseMobile: () => void;
}

export function Sidebar(props: SidebarProps) {
  const { mobileOpen, onCloseMobile } = props;
  const { t } = useLanguage();

  return (
    <>
      {/* Desktop: always visible */}
      <aside className="hidden w-72 shrink-0 border-r border-brand-muted/20 bg-white md:flex md:flex-col">
        <SidebarContent {...props} />
      </aside>

      {/* Phones: slide-in panel */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              className="fixed inset-0 z-40 bg-ink/40 md:hidden"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={onCloseMobile}
            />
            <motion.aside
              role="dialog"
              aria-label={t.yourChats}
              className="fixed inset-y-0 left-0 z-50 flex w-80 max-w-[85%] flex-col bg-white shadow-2xl md:hidden"
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 30, stiffness: 300 }}
            >
              <button
                type="button"
                onClick={onCloseMobile}
                aria-label={t.closeChats}
                className="absolute top-3 right-3 rounded-full p-1.5 text-ink-soft hover:bg-brand-mist"
              >
                <X className="size-5" aria-hidden />
              </button>
              <SidebarContent {...props} />
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
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
  onCloseMobile,
}: SidebarProps) {
  const { t } = useLanguage();

  // On phones, close the panel after choosing something.
  function andClose(action: () => void) {
    return () => {
      action();
      onCloseMobile();
    };
  }

  return (
    <div className="flex h-full flex-col gap-3 p-3">
      <button
        type="button"
        onClick={andClose(onNewChat)}
        className="mt-1 flex items-center justify-center gap-2 rounded-xl bg-sun py-2.5 text-sm font-semibold text-brand transition hover:brightness-95"
      >
        <MessageSquarePlus className="size-4" aria-hidden />
        {t.newChat}
      </button>

      <p className="px-1 pt-2 text-xs font-semibold tracking-wide text-ink-soft uppercase">{t.yourChats}</p>

      <nav className="-mx-1 flex-1 overflow-y-auto px-1">
        {chats.length === 0 ? (
          <p className="px-2 py-4 text-sm text-ink-soft">{t.noChats}</p>
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
        className="flex items-center gap-2 rounded-xl px-3 py-2.5 text-sm text-brand transition hover:bg-brand-mist"
      >
        <Brain className="size-4" aria-hidden />
        {t.memoryButton}
      </button>
    </div>
  );
}
