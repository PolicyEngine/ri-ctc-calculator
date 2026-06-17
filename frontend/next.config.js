/** @type {import('next').NextConfig} */
const basePath = process.env.NEXT_PUBLIC_BASE_PATH !== undefined
  ? process.env.NEXT_PUBLIC_BASE_PATH
  : '/us/rhode-island-ctc-calculator';

const LOCAL_API_URL = 'http://localhost:8080';
// Modal is the canonical backend (see scripts/modal_serve.py +
// .github/workflows/deploy-modal.yml). The asgi app is labelled `ri-ctc-api`,
// so its deployed URL is `https://<workspace>--ri-ctc-api.modal.run`. Vercel
// should set NEXT_PUBLIC_API_URL explicitly; this is only the fallback.
const DEFAULT_REMOTE_API_URL = 'https://policyengine--ri-ctc-api.modal.run';
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
