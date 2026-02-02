/** @type {import('next').NextConfig} */
const nextConfig = {
    trailingSlash: false,
    rewrites: async () => {
        return [
            {
                source: '/api/:path*',
                destination: 'http://127.0.0.1:8000/api/v1/:path*',
            },
        ]
    },
}

module.exports = nextConfig
