"use client";

import { motion } from "motion/react";

/** The customer's message: a purple bubble on the right. */
export function UserMessage({ text }: { text: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="ml-auto max-w-[85%] rounded-2xl rounded-br-md bg-brand px-4 py-2.5 whitespace-pre-wrap text-white shadow-sm sm:max-w-[70%]"
    >
      {text}
    </motion.div>
  );
}
