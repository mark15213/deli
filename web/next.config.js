/** @type {import('next').NextConfig} */
const nextConfig = {
    trailingSlash: false,
    rewrites: async () => {
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
        return [
            {
                source: '/api/:path*',
                destination: `${backendUrl}/api/v1/:path*`,
            },
        ]
    },
}

module.exports = nextConfig
