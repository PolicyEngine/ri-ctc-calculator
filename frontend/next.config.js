/** @type {import('next').NextConfig} */
const basePath = process.env.NEXT_PUBLIC_BASE_PATH !== undefined
  ? process.env.NEXT_PUBLIC_BASE_PATH
  : '/us/rhode-island-ctc-calculator';

const LOCAL_API_URL = 'http://localhost:8080';
const DEFAULT_REMOTE_API_URL = 'https://ri-ctc-calculator-backend-5yhj7qazcq-uc.a.run.app';
const isVercelBuild = process.env.VERCEL === '1';
const apiUrl = process.env.NEXT_PUBLIC_API_URL || (
  isVercelBuild ? DEFAULT_REMOTE_API_URL : LOCAL_API_URL
);

if (!apiUrl) {
  throw new Error(
    'NEXT_PUBLIC_API_URL must be set for Vercel deployments of ri-ctc-calculator.',
  );
}

if (isVercelBuild && apiUrl.includes('localhost')) {
  throw new Error(
    'NEXT_PUBLIC_API_URL must point to the deployed API, not localhost.',
  );
}

const nextConfig = {
  ...(basePath ? { basePath } : {}),
  output: 'standalone',
  env: {
    NEXT_PUBLIC_BASE_PATH: basePath,
    NEXT_PUBLIC_API_URL: apiUrl,
  },
  // Pin the workspace root so Turbopack does not pick up a stray lockfile from
  // a parent directory.
  turbopack: {
    root: process.cwd(),
  },
}

module.exports = nextConfig
