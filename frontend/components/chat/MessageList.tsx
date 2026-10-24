"use client";

import { useEffect, useRef } from "react";
import { History } from "lucide-react";
import { useLanguage } from "@/components/LanguageProvider";
import type { ChatMessage } from "@/lib/types";
import { AssistantMessage } from "./AssistantMessage";
import { UserMessage } from "./UserMessage";

interface MessageListProps {
  messages: ChatMessage[];
  /** In long chats, older messages are condensed into this summary. */
  summary: string | null;
}

/** The conversation. Keeps the newest message in view as replies stream in. */
export function MessageList({ messages, summary }: MessageListProps) {
  const { t } = useLanguage();
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages]);

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 px-4 py-6">
      {summary && (
        <aside className="flex gap-2 rounded-2xl border border-dashed border-brand-muted/50 bg-white/60 px-4 py-3 text-sm text-ink-soft backdrop-blur-xl">
          <History className="mt-0.5 size-4 shrink-0 text-brand-muted" aria-hidden />
          <p>
            <span className="font-medium text-brand">{t.earlierInChat}: </span>
            {summary}
          </p>
        </aside>
      )}
      {messages.map((message) =>
        message.role === "user" ? (
          <UserMessage key={message.id} text={message.text} />
        ) : (
          <AssistantMessage key={message.id} message={message} />
        ),
      )}
      <div ref={bottom} />
    </div>
  );
}
