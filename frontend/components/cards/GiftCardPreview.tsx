import { Heart } from "lucide-react";

interface GiftCardPreviewProps {
  message: string;
  to: string;
  from: string;
}

/** A preview of the greeting card that travels with the gift, as the recipient will see it. */
export function GiftCardPreview({ message, to, from }: GiftCardPreviewProps) {
  return (
    <figure className="relative overflow-hidden rounded-xl border border-gold/40 bg-cream px-5 pt-6 pb-4 shadow-inner">
      {/* Kapruka-yellow ribbon across the top of the card */}
      <div className="absolute inset-x-0 top-0 h-1.5 bg-sun" aria-hidden />
      <Heart className="absolute top-3 right-3 size-4 fill-sun text-gold" aria-hidden />

      <p className="text-xs text-ink-soft">Dear {to},</p>
      <blockquote className="mt-2 text-base leading-relaxed whitespace-pre-wrap text-ink italic">
        {message}
      </blockquote>
      <figcaption className="mt-3 text-right text-sm font-medium text-brand">— {from}</figcaption>
    </figure>
  );
}
