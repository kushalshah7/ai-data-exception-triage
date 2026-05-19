import type { NextConfig } from "next";

const isProd = process.env.NODE_ENV === "production";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  basePath: isProd ? "/ai-data-exception-triage" : "",
  assetPrefix: isProd ? "/ai-data-exception-triage/" : "",
};

export default nextConfig;
