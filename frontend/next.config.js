/**@type {import('next').NextConfig} */

const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      {
        source: '/api/:path*',
        destination: '/api/proxy/:path*',
      },
    ]
  },
}

module.exports = nextConfig
