"use client";

import { useState, type FormEvent, type KeyboardEvent } from "react";
import { SendHorizontal } from "lucide-react";
import { useLanguage } from "@/components/LanguageProvider";

interface ComposerProps {
  onSend: (text: string) => void;
  disabled: boolean;
}

/** The message box. Enter sends; Shift+Enter adds a new line. */
export function Composer({ onSend, disabled }: ComposerProps) {
  const { t } = useLanguage();
  const [text, setText] = useState("");
  const canSend = text.trim().length > 0 && !disabled;

  function submit(event?: FormEvent) {
    event?.preventDefault();
    if (!canSend) return;
    onSend(text);
    setText("");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit();
    }
  }

  return (
    // A floating pill over the particles, rather than a bar across the screen.
    <form onSubmit={submit} className="relative px-3 pt-1 pb-3 sm:px-4 sm:pb-5">
      <div className="mx-auto flex max-w-4xl items-end gap-2 rounded-3xl bg-white/85 p-1.5 pl-2 shadow-xl shadow-brand/10 ring-1 ring-brand-muted/30 backdrop-blur-xl transition focus-within:ring-2 focus-within:ring-brand/40">
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          maxLength={2000}
          placeholder={t.placeholder}
          aria-label={t.messageLabel}
          className="field-sizing-content max-h-40 min-h-11 flex-1 resize-none bg-transparent px-3 py-2.5 text-ink outline-none placeholder:text-ink-soft/60"
        />
        <button
          type="submit"
          disabled={!canSend}
          aria-label={t.send}
          className="flex size-11 shrink-0 items-center justify-center rounded-full bg-linear-to-br from-sun to-gold text-brand shadow-md shadow-gold/30 transition hover:scale-105 active:scale-95 disabled:scale-100 disabled:from-brand-mist disabled:to-brand-mist disabled:text-brand-muted disabled:shadow-none"
        >
          <SendHorizontal className="size-5" aria-hidden />
        </button>
      </div>
    </form>
  );
}
