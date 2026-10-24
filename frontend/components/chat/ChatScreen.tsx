"use client";

/**
 * The full-screen chat: header on top, conversation in the middle,
 * message box at the bottom. Before the first message, a welcome screen
 * with suggestions takes the conversation's place.
 *
 * The cart shown in the header is simply the newest cart card in the
 * conversation: every cart change produces one.
 */

import { useMemo, useState } from "react";
import { useChat } from "@/hooks/useChat";
import type { Cart, ChatMessage } from "@/lib/types";
import { CartDrawer } from "./CartDrawer";
import { ChatActionsContext } from "./ChatActions";
import { Composer } from "./Composer";
import { Header } from "./Header";
import { MessageList } from "./MessageList";
import { Welcome } from "./Welcome";

export function ChatScreen() {
  const { messages, isReplying, send, confirmCheckout, reset } = useChat();
  const [cartOpen, setCartOpen] = useState(false);
  const hasStarted = messages.length > 0;

  const cart = useMemo(() => latestCart(messages), [messages]);
  const latestCheckoutKey = useMemo(() => latestCheckout(messages), [messages]);
  const actions = useMemo(
    () => ({ send, confirmCheckout, isReplying, latestCheckoutKey }),
    [send, confirmCheckout, isReplying, latestCheckoutKey],
  );

  return (
    <ChatActionsContext.Provider value={actions}>
      <div className="flex h-dvh flex-col">
        <Header
          onNewChat={reset}
          canReset={hasStarted}
          cartCount={cart.items.reduce((sum, item) => sum + item.quantity, 0)}
          onOpenCart={() => setCartOpen(true)}
        />

        <main className="flex-1 overflow-y-auto">
          {hasStarted ? <MessageList messages={messages} /> : <Welcome onPick={send} />}
        </main>

        <Composer onSend={send} disabled={isReplying} />
      </div>

      <CartDrawer open={cartOpen} cart={cart} onClose={() => setCartOpen(false)} />
    </ChatActionsContext.Provider>
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
