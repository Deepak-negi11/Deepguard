import path from 'node:path';
import { fileURLToPath } from 'node:url';

import type { NextConfig } from 'next';

const currentDir = path.dirname(fileURLToPath(import.meta.url));

const nextConfig: NextConfig = {
  outputFileTracingRoot: path.join(currentDir, '..'),
  allowedDevOrigins: ['localhost', '127.0.0.1'],
  experimental: {
    optimizePackageImports: ['lucide-react'],
  },
};

export default nextConfig;
