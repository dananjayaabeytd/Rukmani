"use client";

/**
 * One chat in the sidebar. Tap to open; the pencil renames it in place;
 * the bin asks "Delete this chat?" before deleting.
 */

import { useState, type FormEvent } from "react";
import { Check, Pencil, Trash2, X } from "lucide-react";
import { useLanguage } from "@/components/LanguageProvider";
import type { ChatSummary } from "@/lib/types";

interface ChatListItemProps {
  chat: ChatSummary;
  active: boolean;
  onSelect: () => void;
  onRename: (title: string) => void;
  onDelete: () => void;
}

type Mode = "view" | "rename" | "confirmDelete";

export function ChatListItem({ chat, active, onSelect, onRename, onDelete }: ChatListItemProps) {
  const { t } = useLanguage();
  const [mode, setMode] = useState<Mode>("view");
  const [title, setTitle] = useState(chat.title);

  function saveTitle(event: FormEvent) {
    event.preventDefault();
    const trimmed = title.trim();
    if (trimmed && trimmed !== chat.title) onRename(trimmed);
    setMode("view");
  }

  if (mode === "rename") {
    return (
      <form onSubmit={saveTitle} className="flex items-center gap-1 rounded-xl bg-white/10 p-1.5 ring-1 ring-sun">
        <input
          autoFocus
          value={title}
          maxLength={80}
          onChange={(event) => setTitle(event.target.value)}
          aria-label={t.renameChat}
          className="min-w-0 flex-1 bg-transparent px-1.5 text-sm text-white outline-none"
        />
        <button type="submit" aria-label={t.save} className="rounded-lg p-1 text-sun hover:bg-white/10">
          <Check className="size-4" aria-hidden />
        </button>
        <button
          type="button"
          aria-label={t.cancel}
          onClick={() => {
            setTitle(chat.title);
            setMode("view");
          }}
          className="rounded-lg p-1 text-white/70 hover:bg-white/10"
        >
          <X className="size-4" aria-hidden />
        </button>
      </form>
    );
  }

  if (mode === "confirmDelete") {
    return (
      <div className="flex items-center gap-2 rounded-xl bg-white px-3 py-2 text-sm text-red-800 shadow-md">
        <span className="flex-1">{t.confirmDelete}</span>
        <button type="button" onClick={onDelete} className="rounded-lg bg-red-600 px-2 py-0.5 text-xs font-semibold text-white">
          {t.yes}
        </button>
        <button type="button" onClick={() => setMode("view")} className="rounded-lg px-2 py-0.5 text-xs font-semibold text-ink">
          {t.no}
        </button>
      </div>
    );
  }

  return (
    <div
      className={`group relative flex items-center rounded-xl transition ${
        active ? "bg-white/15 text-white shadow-inner" : "text-white/75 hover:bg-white/10 hover:text-white"
      }`}
    >
      {/* The open chat gets a small yellow marker, like the smile in Kapruka's logo. */}
      {active && <span aria-hidden className="absolute inset-y-2 left-0 w-1 rounded-full bg-sun" />}
      <button
        type="button"
        onClick={onSelect}
        aria-current={active ? "page" : undefined}
        className="min-w-0 flex-1 truncate px-3 py-2 text-left text-sm"
      >
        {chat.title}
      </button>
      {/* Edit and delete appear on hover (desktop) and are always there for the open chat. */}
      <div className={`flex shrink-0 pr-1 ${active ? "" : "opacity-0 group-hover:opacity-100 focus-within:opacity-100"}`}>
        <button
          type="button"
          onClick={() => setMode("rename")}
          aria-label={t.renameChat}
          className="rounded-lg p-1.5 hover:bg-white/15"
        >
          <Pencil className="size-3.5" aria-hidden />
        </button>
        <button
          type="button"
          onClick={() => setMode("confirmDelete")}
          aria-label={t.deleteChat}
          className="rounded-lg p-1.5 hover:bg-white/15"
        >
          <Trash2 className="size-3.5" aria-hidden />
        </button>
      </div>
    </div>
  );
}
