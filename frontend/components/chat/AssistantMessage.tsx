"use client";

import { motion } from "motion/react";
import Markdown from "react-markdown";
import type { Artifact, ChatMessage } from "@/lib/types";
import { DeliveryCard } from "@/components/cards/DeliveryCard";
import { ProductCarousel } from "@/components/cards/ProductCarousel";
import { ProductDetailCard } from "@/components/cards/ProductDetailCard";
import { RukmaniAvatar } from "./RukmaniAvatar";
import { StatusPill } from "./StatusPill";

/**
 * One reply from Rukmani: what she found (cards) first, then what she says.
 * While she is still working, a status pill shows the current step.
 */
export function AssistantMessage({ message }: { message: ChatMessage }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-start gap-3"
    >
      <RukmaniAvatar />

      <div className="flex min-w-0 flex-1 flex-col gap-3">
        {message.artifacts.map((artifact, index) => (
          <ArtifactView key={index} artifact={artifact} />
        ))}

        {message.text && (
          <div
            className={`w-fit max-w-full rounded-2xl rounded-tl-md px-4 py-2.5 shadow-sm sm:max-w-[85%] ${
              message.failed ? "bg-red-50 text-red-800" : "bg-white text-ink"
            }`}
          >
            <Markdown
              components={{
                p: (props) => <p className="my-1 leading-relaxed" {...props} />,
                strong: (props) => <strong className="font-semibold text-brand" {...props} />,
                ul: (props) => <ul className="my-1 list-disc space-y-1 pl-5" {...props} />,
                ol: (props) => <ol className="my-1 list-decimal space-y-1 pl-5" {...props} />,
                a: (props) => (
                  <a className="text-brand-light underline" target="_blank" rel="noreferrer" {...props} />
                ),
              }}
            >
              {message.text}
            </Markdown>
          </div>
        )}

        {message.status && <StatusPill label={message.status} />}
      </div>
    </motion.div>
  );
}

/** Pick the right card for each kind of tool result. */
function ArtifactView({ artifact }: { artifact: Artifact }) {
  switch (artifact.kind) {
    case "products":
      return <ProductCarousel products={artifact.products} />;
    case "product_detail":
      return <ProductDetailCard product={artifact.product} />;
    case "delivery":
      return <DeliveryCard delivery={artifact.delivery} />;
  }
}
