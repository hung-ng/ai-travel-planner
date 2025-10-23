/**@type {import('next').NextConfig} */

const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
        permanent: false, // Added the required permanent property
      },
    ]
  },
}

module.exports = nextConfig
