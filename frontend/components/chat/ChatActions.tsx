"use client";

/**
 * Actions that cards deep inside the conversation need (e.g. "Add to cart",
 * "Confirm"), shared through React context so they don't have to be passed
 * down through every component in between.
 */

import { createContext, useContext } from "react";
import type { Order } from "@/lib/types";

export interface ChatActions {
  /** Send a message to Rukmani as if the customer typed it. */
  send: (text: string) => void;
  /** Place the order for the pending checkout. */
  confirmCheckout: () => Promise<Order>;
  /** True while Rukmani is replying; cards disable their buttons meanwhile. */
  isReplying: boolean;
  /**
   * Key of the newest checkout card ("<messageId>:<index>"). Older summaries
   * are out of date, so only this one may be confirmed.
   */
  latestCheckoutKey: string | null;
}

export const ChatActionsContext = createContext<ChatActions | null>(null);

export function useChatActions(): ChatActions {
  const actions = useContext(ChatActionsContext);
  if (!actions) throw new Error("useChatActions must be used inside ChatScreen");
  return actions;
}
