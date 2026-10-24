"use client";

import { motion } from "motion/react";
import { ArrowUpRight, Sparkles } from "lucide-react";
import { useLanguage } from "@/components/LanguageProvider";
import { OccasionBanner } from "./OccasionBanner";
import { RukmaniAvatar } from "./RukmaniAvatar";

interface WelcomeProps {
  onPick: (suggestion: string) => void;
}

/** First screen: a greeting and one-tap suggestions, in the chosen language. */
export function Welcome({ onPick }: WelcomeProps) {
  const { t } = useLanguage();

  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="mx-auto flex max-w-2xl flex-col items-center px-4 pt-10 pb-8 text-center sm:pt-16"
    >
      <RukmaniAvatar size="lg" />
      <h1 className="mt-6 bg-linear-to-r from-brand-deep via-brand-light to-brand bg-clip-text pb-1 text-3xl font-bold text-transparent sm:text-4xl">
        {t.welcomeTitle}
      </h1>
      <p className="mt-2 flex items-center gap-1.5 text-base font-medium text-brand-light">
        <Sparkles className="size-4 text-gold" aria-hidden />
        {t.welcomeLanguages}
      </p>
      <p className="mt-4 max-w-md text-ink-soft">{t.welcomeIntro}</p>

      <OccasionBanner onPick={onPick} />

      <div className="mt-6 grid w-full gap-3 sm:grid-cols-2">
        {t.suggestions.map((suggestion, index) => (
          <motion.button
            key={suggestion}
            type="button"
            onClick={() => onPick(suggestion)}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 + index * 0.08 }}
            className="group flex items-center gap-3 rounded-2xl bg-white/75 px-4 py-3 text-left text-sm text-ink shadow-md shadow-brand/5 ring-1 ring-white/70 backdrop-blur-xl transition hover:-translate-y-0.5 hover:shadow-lg hover:shadow-brand/15 hover:ring-brand/30"
          >
            <span className="flex-1">{suggestion}</span>
            <ArrowUpRight
              className="size-4 shrink-0 text-brand-muted transition group-hover:translate-x-0.5 group-hover:-translate-y-0.5 group-hover:text-brand"
              aria-hidden
            />
          </motion.button>
        ))}
      </div>
    </motion.section>
  );
}
