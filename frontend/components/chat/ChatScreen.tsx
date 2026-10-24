"use client";

/**
 * The full-screen chat: the chat list on the left (collapsible on desktop,
 * a slide-in panel on phones), and the open conversation on the right —
 * header, messages over an animated particle background, and a floating
 * message box. Before the first message, a welcome screen takes the
 * conversation's place.
 *
 * The cart shown in the header is simply the newest cart card in the
 * conversation: every cart change produces one (reopened chats get one too).
 */

import { useEffect, useMemo, useState } from "react";
import { useChat } from "@/hooks/useChat";
import { useChats } from "@/hooks/useChats";
import { loadSidebarCollapsed, saveSidebarCollapsed } from "@/lib/storage";
import type { Cart, ChatMessage } from "@/lib/types";
import { CartDrawer } from "./CartDrawer";
import { ChatActionsContext } from "./ChatActions";
import { Composer } from "./Composer";
import { Header } from "./Header";
import { MemoryPanel } from "./MemoryPanel";
import { MessageList } from "./MessageList";
import { ParticleField } from "./ParticleField";
import { Sidebar } from "./Sidebar";
import { Welcome } from "./Welcome";

export function ChatScreen() {
  const { chats, refresh, rename, remove } = useChats();
  const { chatId, messages, summary, isReplying, isLoading, send, confirmCheckout, open, newChat } =
    useChat({ onTurnFinished: refresh });
  const [cartOpen, setCartOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [memoryOpen, setMemoryOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const hasStarted = messages.length > 0;

  // The collapsed/expanded choice is remembered in the browser (read after
  // the first render, which is pre-built without browser storage).
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- one-time restore after load
    setSidebarCollapsed(loadSidebarCollapsed());
  }, []);

  function toggleSidebar() {
    setSidebarCollapsed((collapsed) => {
      saveSidebarCollapsed(!collapsed);
      return !collapsed;
    });
  }

  const cart = useMemo(() => latestCart(messages), [messages]);
  const latestCheckoutKey = useMemo(() => latestCheckout(messages), [messages]);
  const actions = useMemo(
    () => ({ send, confirmCheckout, isReplying, latestCheckoutKey }),
    [send, confirmCheckout, isReplying, latestCheckoutKey],
  );

  async function deleteChat(id: string) {
    await remove(id);
    if (id === chatId) newChat(); // the open chat is gone: start a fresh one
  }

  return (
    <ChatActionsContext.Provider value={actions}>
      <div className="flex h-dvh">
        <Sidebar
          chats={chats}
          activeChatId={chatId}
          onSelect={(id) => void open(id)}
          onNewChat={newChat}
          onRename={(id, title) => void rename(id, title)}
          onDelete={(id) => void deleteChat(id)}
          onOpenMemory={() => setMemoryOpen(true)}
          collapsed={sidebarCollapsed}
          onToggleCollapsed={toggleSidebar}
          mobileOpen={sidebarOpen}
          onCloseMobile={() => setSidebarOpen(false)}
        />

        <div className="flex min-w-0 flex-1 flex-col">
          <Header
            onOpenChats={() => setSidebarOpen(true)}
            cartCount={cart.items.reduce((sum, item) => sum + item.quantity, 0)}
            onOpenCart={() => setCartOpen(true)}
          />

          {/* Soft lavender glow + drifting particles behind the conversation. */}
          <div className="chat-backdrop relative flex min-h-0 flex-1 flex-col">
            <ParticleField />
            <main className="relative flex-1 overflow-y-auto" aria-busy={isLoading}>
              {isLoading ? (
                <LoadingChat />
              ) : hasStarted ? (
                <MessageList messages={messages} summary={summary} />
              ) : (
                <Welcome onPick={send} />
              )}
            </main>

            <Composer onSend={send} disabled={isReplying || isLoading} />
          </div>
        </div>
      </div>

      <CartDrawer open={cartOpen} cart={cart} onClose={() => setCartOpen(false)} />
      <MemoryPanel open={memoryOpen} onClose={() => setMemoryOpen(false)} />
    </ChatActionsContext.Provider>
  );
}

/** Placeholder bubbles while a saved chat loads. */
function LoadingChat() {
  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 px-4 py-6">
      <div className="ml-auto h-10 w-1/2 animate-pulse rounded-2xl bg-brand-muted/30" />
      <div className="h-40 w-3/4 animate-pulse rounded-2xl bg-white/70" />
      <div className="ml-auto h-10 w-1/3 animate-pulse rounded-2xl bg-brand-muted/30" />
    </div>
  );
}

/** The newest cart in the conversation (empty before anything was added). */
function latestCart(messages: ChatMessage[]): Cart {
  for (const message of [...messages].reverse()) {
    const cartArtifact = [...message.artifacts].reverse().find((a) => a.kind === "cart");
    if (cartArtifact) return cartArtifact.cart;
  }
  return { items: [] };
}

/** Key of the newest checkout summary, so older ones can't be confirmed. */
function latestCheckout(messages: ChatMessage[]): string | null {
  let key: string | null = null;
  for (const message of messages) {
    message.artifacts.forEach((artifact, index) => {
      if (artifact.kind === "checkout") key = `${message.id}:${index}`;
    });
  }
  return key;
}
