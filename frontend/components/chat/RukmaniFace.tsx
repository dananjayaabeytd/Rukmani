"use client";

import { useId } from "react";

/**
 * Rukmani as a friendly cartoon: a young Sri Lankan woman with her hair in a
 * bun and a yellow flower, gold earrings and a gold saree, on Kapruka purple.
 * Plain SVG, so it stays sharp at every size and needs no image file.
 */
export function RukmaniFace({ className }: { className?: string }) {
  // Unique gradient ids, so several avatars on one page don't clash.
  const id = useId();
  const bg = `${id}-bg`;
  const skin = `${id}-skin`;
  const saree = `${id}-saree`;
  const round = `${id}-round`;

  return (
    <svg viewBox="0 0 100 100" className={className} aria-hidden>
      <defs>
        <linearGradient id={bg} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#573b91" />
          <stop offset="100%" stopColor="#2c1c52" />
        </linearGradient>
        <linearGradient id={skin} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#c98f68" />
          <stop offset="100%" stopColor="#b57a54" />
        </linearGradient>
        <linearGradient id={saree} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#f8da08" />
          <stop offset="100%" stopColor="#ffb800" />
        </linearGradient>
        <clipPath id={round}>
          <circle cx="50" cy="50" r="50" />
        </clipPath>
      </defs>

      {/* Everything is cut to a circle. */}
      <g clipPath={`url(#${round})`}>
        {/* Background */}
        <circle cx="50" cy="50" r="50" fill={`url(#${bg})`} />

        {/* Hair behind the head and shoulders */}
        <path d="M24 52 C22 30 36 18 50 18 C64 18 78 30 76 52 L78 74 C70 78 30 78 22 74 Z" fill="#1d1428" />

        {/* Shoulders and saree */}
        <path d="M14 100 C16 82 32 74 50 74 C68 74 84 82 86 100 Z" fill={`url(#${saree})`} />
        <path d="M50 74 C60 74 70 77 77 82 L58 100 L46 100 Z" fill="#573b91" opacity="0.85" />
        <path d="M50 74 C60 74 70 77 77 82" stroke="#ffb800" strokeWidth="1.5" fill="none" />

        {/* Neck */}
        <path d="M43 64 L57 64 L58 77 C53 80 47 80 42 77 Z" fill="#b07350" />

        {/* Face */}
        <ellipse cx="50" cy="49" rx="19" ry="21.5" fill={`url(#${skin})`} />

        {/* Ears and gold earrings */}
        <ellipse cx="31" cy="51" rx="3" ry="4.5" fill="#b57a54" />
        <ellipse cx="69" cy="51" rx="3" ry="4.5" fill="#b57a54" />
        <circle cx="31" cy="58" r="2.6" fill="#ffb800" />
        <circle cx="69" cy="58" r="2.6" fill="#ffb800" />

        {/* Hair on top, parted, with a bun */}
        <circle cx="50" cy="17" r="10" fill="#1d1428" />
        <path d="M30 46 C29 30 38 25 50 25 C62 25 71 30 70 46 C66 37 58 33 50 33 C42 33 34 37 30 46 Z" fill="#1d1428" />
        <path d="M50 25 L50 33" stroke="#3a2a4f" strokeWidth="1" />

        {/* A yellow flower in the hair */}
        <g transform="translate(61 14)">
          <circle cx="0" cy="-4" r="3.2" fill="#f8da08" />
          <circle cx="3.8" cy="-1.2" r="3.2" fill="#f8da08" />
          <circle cx="2.4" cy="3.3" r="3.2" fill="#f8da08" />
          <circle cx="-2.4" cy="3.3" r="3.2" fill="#f8da08" />
          <circle cx="-3.8" cy="-1.2" r="3.2" fill="#f8da08" />
          <circle cx="0" cy="0" r="2" fill="#ffb800" />
        </g>

        {/* Eyebrows */}
        <path d="M38 41 C40 39 44 39 46 40.5" stroke="#1d1428" strokeWidth="1.6" strokeLinecap="round" fill="none" />
        <path d="M54 40.5 C56 39 60 39 62 41" stroke="#1d1428" strokeWidth="1.6" strokeLinecap="round" fill="none" />

        {/* Eyes with a sparkle */}
        <ellipse cx="42" cy="48" rx="3" ry="3.6" fill="#1d1428" />
        <ellipse cx="58" cy="48" rx="3" ry="3.6" fill="#1d1428" />
        <circle cx="43.1" cy="46.6" r="1.1" fill="#ffffff" />
        <circle cx="59.1" cy="46.6" r="1.1" fill="#ffffff" />

        {/* Cheeks */}
        <ellipse cx="37" cy="56" rx="4" ry="2.4" fill="#e0607e" opacity="0.35" />
        <ellipse cx="63" cy="56" rx="4" ry="2.4" fill="#e0607e" opacity="0.35" />

        {/* Smile */}
        <path d="M43 58 C46 63 54 63 57 58 C54 60 46 60 43 58 Z" fill="#8f2d3c" />
        <path d="M43 58 C46 63 54 63 57 58" stroke="#7a2232" strokeWidth="1.2" strokeLinecap="round" fill="none" />
      </g>
    </svg>
  );
}
