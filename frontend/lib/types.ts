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

// ── Cart, checkout and order (backend/src/kapruka_agent/kapruka/orders.py) ──

export interface CartItem {
  product_id: string;
  name: string;
  price: Money; // price of one item
  image_url: string | null;
  url: string | null;
  quantity: number;
  icing_text: string | null;
}

export interface Cart {
  items: CartItem[];
}

export interface CheckoutDetails {
  recipient_name: string;
  recipient_phone: string;
  address: string;
  city: string;
  delivery_date: string; // YYYY-MM-DD
  location_type: "house" | "apartment" | "office" | "other";
  instructions: string | null;
  sender_name: string;
  anonymous: boolean;
  gift_message: string | null;
}

export interface CheckoutQuote {
  cart: Cart;
  details: CheckoutDetails;
  items_total: Money;
  delivery_fee: Money;
  grand_total: Money;
}

export interface Order {
  checkout_url: string; // the customer opens this to pay
  order_ref: string;
  items_total: Money;
  delivery_fee: Money;
  grand_total: Money;
  delivery_date: string;
  expires_at: string; // ISO 8601 — the pay link stops working after this
}

/** A paid order's progress (recipient phone/address are deliberately not included). */
export interface OrderStatus {
  order_number: string;
  status: string; // received | confirmed | shipped | delivered | cancelled | ...
  status_display: string;
  order_date: string | null;
  delivery_date: string | null;
  shipped_date: string | null;
  recipient_name: string | null;
  recipient_city: string | null;
  progress: { step: string; timestamp: string | null }[];
  items: { name: string; quantity: number }[];
  has_delivery_photo: boolean;
}

// ── Artifacts: data a tool produced for the UI to show ───────────────

export type Artifact =
  | { kind: "products"; query: string; products: Product[] }
  | { kind: "product_detail"; product: ProductDetail }
  | { kind: "delivery"; product_id: string | null; delivery: DeliveryCheck }
  | { kind: "cart"; cart: Cart; total: Money }
  | { kind: "checkout"; quote: CheckoutQuote }
  | { kind: "tracking"; order: OrderStatus };

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
  /** What Rukmani is doing right now: "thinking" or the running tool's name (null when done). */
  status: string | null;
  failed: boolean;
}
