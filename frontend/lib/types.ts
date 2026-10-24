/**
 * Types shared with the backend.
 *
 * These mirror backend/src/kapruka_agent/kapruka/models.py (data) and
 * backend/src/kapruka_agent/api/events.py (stream events). When the backend
 * changes shape, update this file to match.
 */

// ── Kapruka data ─────────────────────────────────────────────────────

export interface Money {
  amount: number | null;
  currency: string;
}

export interface Product {
  id: string;
  name: string;
  price: Money;
  compare_at_price: Money | null; // pre-discount price, when on sale
  in_stock: boolean;
  stock_level: "low" | "medium" | "high" | null;
  image_url: string | null;
  url: string;
}

export interface ProductDetail extends Product {
  description: string;
  images: string[];
  delivery: {
    island_wide: boolean;
    deliverable_city_count: number | null;
    deliverable_cities: string[];
  } | null;
}

export interface DeliveryCheck {
  city: string;
  checked_date: string; // YYYY-MM-DD
  available: boolean;
  delivery_fee: number | null;
  fee_currency: string;
  fee_basis: "cart" | "max" | "fixed" | null; // "max" means "up to"
  reason: string | null;
  next_available_date: string | null;
  item_deliverable: boolean | null;
  deliverable_cities: string[];
  perishable_warning: string | null;
}

// ── Artifacts: data a tool produced for the UI to show ───────────────

export type Artifact =
  | { kind: "products"; query: string; products: Product[] }
  | { kind: "product_detail"; product: ProductDetail }
  | { kind: "delivery"; product_id: string | null; delivery: DeliveryCheck };

// ── Events streamed from POST /api/chat ──────────────────────────────

export type StreamEvent =
  | { type: "token"; text: string }
  | { type: "tool"; tool: string; label: string }
  | { type: "artifact"; artifact: Artifact }
  | { type: "done" }
  | { type: "error"; message: string };

// ── Chat messages as the UI keeps them ───────────────────────────────

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  artifacts: Artifact[];
  /** What Rukmani is doing right now, e.g. "Searching Kapruka for gifts". */
  status: string | null;
  failed: boolean;
}
