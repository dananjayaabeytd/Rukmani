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
    <form
      onSubmit={submit}
      className="border-t border-brand-muted/30 bg-white/90 backdrop-blur"
    >
      <div className="mx-auto flex max-w-4xl items-end gap-2 px-4 py-3">
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          maxLength={2000}
          placeholder={t.placeholder}
          aria-label={t.messageLabel}
          className="field-sizing-content max-h-40 min-h-11 flex-1 resize-none rounded-2xl border border-brand-muted/50 bg-brand-tint px-4 py-2.5 text-ink outline-none placeholder:text-ink-soft/60 focus:border-brand focus:ring-2 focus:ring-brand/20"
        />
        <button
          type="submit"
          disabled={!canSend}
          aria-label={t.send}
          className="flex size-11 shrink-0 items-center justify-center rounded-full bg-sun text-brand shadow-sm transition hover:brightness-95 disabled:bg-brand-mist disabled:text-brand-muted"
        >
          <SendHorizontal className="size-5" aria-hidden />
        </button>
      </div>
    </form>
  );
}
