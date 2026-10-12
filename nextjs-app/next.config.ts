import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The chat route starts local Python MCP servers as child processes.
  serverExternalPackages: ["@modelcontextprotocol/client", "groq-sdk"],
  output: 'export',
  basePath: '/HR-Management',
  images: {
    unoptimized: true,
  }
};

export default nextConfig;
