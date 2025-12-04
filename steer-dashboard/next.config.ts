import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export', // <--- Tells Next.js to generate static HTML
  
  // Disable image optimization since we won't have a Node server to process images
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
