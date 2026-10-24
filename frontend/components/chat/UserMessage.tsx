"use client";

import { motion } from "motion/react";

/** The customer's message: a purple bubble on the right. */
export function UserMessage({ text }: { text: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className="ml-auto max-w-[85%] rounded-3xl rounded-br-md bg-linear-to-br from-brand-light to-brand px-4 py-2.5 whitespace-pre-wrap text-white shadow-lg shadow-brand/20 sm:max-w-[70%]"
    >
      {text}
    </motion.div>
  );
}
