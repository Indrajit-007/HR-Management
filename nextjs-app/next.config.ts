import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The chat route starts local Python MCP servers as child processes.
  serverExternalPackages: ["@modelcontextprotocol/client", "groq-sdk"],
  output: 'export'
};

export default nextConfig;
