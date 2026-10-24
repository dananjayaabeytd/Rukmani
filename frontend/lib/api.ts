/**
 * Client for the Rukmani backend.
 *
 *   streamChat       POST /api/chat      — a message; the reply streams back
 *   confirmCheckout  POST /api/checkout  — the customer confirmed; place the order
 *
 * POST /api/chat answers with Server-Sent Events. The browser's EventSource
 * only supports GET, so we read the response stream ourselves and parse the
 * SSE format: events are separated by a blank line, and each event's
 * payload is on lines starting with "data:".
 */

import type { Order, StreamEvent } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Send one message and call `onEvent` for every event in the reply.
 * Resolves when the stream ends. Throws if the server can't be reached.
 */
export async function streamChat(
  threadId: string,
  message: string,
  onEvent: (event: StreamEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ thread_id: threadId, message }),
    signal,
  });
  if (!response.ok || !response.body) {
    throw new Error(`Chat request failed (${response.status})`);
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
export async function confirmCheckout(threadId: string): Promise<Order> {
  const response = await fetch(`${API_URL}/api/checkout`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ thread_id: threadId }),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.detail ?? "Couldn't place the order. Please try again.");
  }
  return body as Order;
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
