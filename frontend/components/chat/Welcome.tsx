"use client";

import { motion } from "motion/react";
import { RukmaniAvatar } from "./RukmaniAvatar";

// Starter questions in all three languages Rukmani speaks.
const SUGGESTIONS = [
  "අම්මට birthday cake එකක් ඕනේ",
  "Valentine's roses for my wife",
  "Kandy walata heta chocolate hamper ekak yawanna puluwanda?",
  "A get-well-soon gift under LKR 5,000",
];

interface WelcomeProps {
  onPick: (suggestion: string) => void;
}

/** First screen: a greeting and one-tap suggestions. */
export function Welcome({ onPick }: WelcomeProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="mx-auto flex max-w-2xl flex-col items-center px-4 pt-14 pb-8 text-center sm:pt-20"
    >
      <RukmaniAvatar size="lg" />
      <h1 className="mt-5 text-2xl font-bold text-brand sm:text-3xl">
        Ayubowan! I&apos;m Rukmani
      </h1>
      <p className="mt-2 text-lg text-brand-light">ආයුබෝවන්! මම රුක්මණී</p>
      <p className="mt-4 max-w-md text-ink-soft">
        Tell me who the gift is for, the occasion and when it should arrive. Ask in Sinhala,
        Singlish or English, and I&apos;ll find something lovely on Kapruka.
      </p>

      <div className="mt-8 grid w-full gap-3 sm:grid-cols-2">
        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            onClick={() => onPick(suggestion)}
            className="rounded-2xl border border-brand-muted/40 bg-white px-4 py-3 text-left text-sm text-ink shadow-sm transition hover:-translate-y-0.5 hover:border-brand hover:shadow-md"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </motion.section>
  );
}
