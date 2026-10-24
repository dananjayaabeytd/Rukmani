"use client";

/**
 * A short "unboxing" moment when the order is created: a Kapruka-purple
 * gift box with a yellow ribbon pops in, its lid flies off with a few
 * sparkles, and then the content (the pay card) rises out of it.
 *
 * Respects "reduce motion": people who turned animations off in their
 * system settings see the content straight away.
 */

import { useEffect, useState, type ReactNode } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";

const UNBOX_MS = 1600;
const SPARKLES = [
  { x: -70, y: -60 },
  { x: 70, y: -70 },
  { x: -40, y: -95 },
  { x: 45, y: -100 },
  { x: 0, y: -115 },
];

export function GiftUnboxing({ children }: { children: ReactNode }) {
  const reduceMotion = useReducedMotion();
  const [opened, setOpened] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setOpened(true), UNBOX_MS);
    return () => clearTimeout(timer);
  }, []);

  if (reduceMotion) return <>{children}</>;

  return (
    <AnimatePresence mode="wait">
      {opened ? (
        <motion.div
          key="content"
          initial={{ opacity: 0, y: 24, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ type: "spring", damping: 18, stiffness: 220 }}
          className="w-full max-w-md"
        >
          {children}
        </motion.div>
      ) : (
        <motion.div
          key="box"
          aria-hidden
          exit={{ opacity: 0, scale: 0.8 }}
          className="relative flex h-44 w-full max-w-md items-end justify-center"
        >
          {/* Box body with a vertical ribbon */}
          <motion.div
            initial={{ scale: 0, rotate: -8 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", damping: 12, stiffness: 200 }}
            className="relative h-24 w-28 rounded-b-lg bg-brand shadow-lg"
          >
            <div className="absolute inset-y-0 left-1/2 w-4 -translate-x-1/2 bg-sun" />
          </motion.div>

          {/* Lid: sits on the box, then flies up and spins away */}
          <motion.div
            initial={{ y: 0, rotate: 0, opacity: 1 }}
            animate={{ y: [0, 0, -110], rotate: [0, -4, -28], opacity: [1, 1, 0] }}
            transition={{ duration: 1.1, delay: 0.5, times: [0, 0.3, 1], ease: "easeOut" }}
            className="absolute bottom-24 h-7 w-32 rounded-md bg-brand-light shadow-md"
          >
            <div className="absolute inset-y-0 left-1/2 w-4 -translate-x-1/2 bg-sun" />
            {/* Bow */}
            <div className="absolute -top-4 left-1/2 flex -translate-x-1/2 gap-0.5">
              <span className="block size-5 rotate-45 rounded-tl-full rounded-br-full bg-sun" />
              <span className="block size-5 -rotate-45 rounded-tr-full rounded-bl-full bg-sun" />
            </div>
          </motion.div>

          {/* Sparkles burst out as the lid opens */}
          {SPARKLES.map((spark, index) => (
            <motion.span
              key={index}
              className="absolute bottom-24 text-xl"
              initial={{ x: 0, y: 0, opacity: 0, scale: 0.4 }}
              animate={{ x: spark.x, y: spark.y, opacity: [0, 1, 0], scale: 1 }}
              transition={{ duration: 0.9, delay: 0.8 + index * 0.05 }}
            >
              ✨
            </motion.span>
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
