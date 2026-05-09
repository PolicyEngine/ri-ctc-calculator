/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
  },
  // Pin the workspace root so Turbopack does not pick up a stray lockfile from
  // a parent directory.
  turbopack: {
    root: process.cwd(),
  },
}

module.exports = nextConfig
