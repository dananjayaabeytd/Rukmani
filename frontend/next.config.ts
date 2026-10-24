import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  // Product photos come from Kapruka's image servers (e.g. static2.kapruka.com).
  images: {
    remotePatterns: [{ protocol: "https", hostname: "**.kapruka.com" }],
  },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
