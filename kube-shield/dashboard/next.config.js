/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  env: {
    AUDIT_SERVICE_URL: process.env.AUDIT_SERVICE_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
