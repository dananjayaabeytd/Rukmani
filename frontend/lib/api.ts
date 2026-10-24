/**
 * Client for the Rukmani backend. Every request carries this browser's
 * private visitor id (X-Visitor-Id), which owns its chats and memories.
 *
 *   streamChat       POST   /api/chat           a message; the reply streams back
 *   confirmCheckout  POST   /api/checkout       the customer confirmed; place the order
 *   listChats        GET    /api/chats          this visitor's chats
 *   getChat          GET    /api/chats/{id}     one chat, rebuilt for the screen
 *   renameChat       PATCH  /api/chats/{id}
 *   deleteChat       DELETE /api/chats/{id}
 *   listMemory       GET    /api/memory         what Rukmani remembers
 *   forgetFact       DELETE /api/memory/{id}
 *   forgetEverything DELETE /api/memory
 *
 * POST /api/chat answers with Server-Sent Events. The browser's EventSource
 * only supports GET, so we read the response stream ourselves and parse the
 * SSE format: events are separated by a blank line, and each event's
 * payload is on lines starting with "data:".
 */

import { getVisitorId } from "./storage";
import type { ChatHistory, ChatSummary, Order, RememberedFact, StreamEvent } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** An error our server explained (e.g. rate limit). Its message is safe to show customers. */
export class ApiError extends Error {}

/** Throw an ApiError carrying the server's explanation ({"detail": "..."}). */
async function throwApiError(response: Response, fallback: string): Promise<never> {
  const body = await response.json().catch(() => ({}));
  const detail = typeof body.detail === "string" ? body.detail : fallback;
  throw new ApiError(detail);
}

/** fetch() against the API, with the visitor id and JSON headers added. */
function call(path: string, init: RequestInit = {}): Promise<Response> {
  return fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Visitor-Id": getVisitorId(),
      ...init.headers,
    },
  });
}

async function json<T>(response: Response, fallback: string): Promise<T> {
  if (!response.ok) await throwApiError(response, fallback);
  return (await response.json()) as T;
}

async function ok(response: Response, fallback: string): Promise<void> {
  if (!response.ok) await throwApiError(response, fallback);
}

// ── Conversation ─────────────────────────────────────────────────────

/**
 * Send one message and call `onEvent` for every event in the reply.
 * Resolves when the stream ends. Throws ApiError if the server refused the
 * message, or a plain Error if it couldn't be reached.
 */
export async function streamChat(
  chatId: string,
  message: string,
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const response = await call("/api/chat", {
    method: "POST",
    body: JSON.stringify({ thread_id: chatId, message }),
    signal,
  });
  if (!response.ok || !response.body) {
    return throwApiError(response, "Rukmani couldn't take that message. Please try again.");
  }

  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    // Normalise line endings, then handle every complete event in the buffer.
    buffer += value.replace(/\r\n/g, "\n");
    let boundary: number;
    while ((boundary = buffer.indexOf("\n\n")) !== -1) {
      const rawEvent = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);

      const event = parseEvent(rawEvent);
      if (event) onEvent(event);
    }
  }
}

/**
 * The customer tapped "Confirm" on the checkout summary: place the order.
 * Returns the order with its pay link, or throws with the reason it failed.
 */
export async function confirmCheckout(chatId: string): Promise<Order> {
  const response = await call("/api/checkout", {
    method: "POST",
    body: JSON.stringify({ thread_id: chatId }),
  });
  return json<Order>(response, "Couldn't place the order. Please try again.");
}

// ── Chats ────────────────────────────────────────────────────────────

export async function listChats(): Promise<ChatSummary[]> {
  return json(await call("/api/chats"), "Couldn't load your chats.");
}

export async function getChat(chatId: string): Promise<ChatHistory> {
  return json(await call(`/api/chats/${chatId}`), "Couldn't open that chat.");
}

export async function renameChat(chatId: string, title: string): Promise<void> {
  const response = await call(`/api/chats/${chatId}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });
  await ok(response, "Couldn't rename the chat.");
}

export async function deleteChat(chatId: string): Promise<void> {
  await ok(await call(`/api/chats/${chatId}`, { method: "DELETE" }), "Couldn't delete the chat.");
}

// ── Memory ───────────────────────────────────────────────────────────

export async function listMemory(): Promise<RememberedFact[]> {
  return json(await call("/api/memory"), "Couldn't load what Rukmani remembers.");
}

export async function forgetFact(factId: string): Promise<void> {
  await ok(await call(`/api/memory/${factId}`, { method: "DELETE" }), "Couldn't forget that.");
}

export async function forgetEverything(): Promise<void> {
  await ok(await call("/api/memory", { method: "DELETE" }), "Couldn't clear the memory.");
}

/** Turn one raw SSE block into an event. Comments and pings return null. */
function parseEvent(rawEvent: string): StreamEvent | null {
  const data = rawEvent
    .split("\n")
    .filter((line) => line.startsWith("data:"))
    .map((line) => line.slice(5).trimStart())
    .join("\n");
  return data ? (JSON.parse(data) as StreamEvent) : null;
}
