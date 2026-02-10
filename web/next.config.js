/** @type {import('next').NextConfig} */
const nextConfig = {
    trailingSlash: false,
    rewrites: async () => {
        let backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

        // Ensure the URL has a protocol prefix
        if (backendUrl && !backendUrl.startsWith('http://') && !backendUrl.startsWith('https://')) {
            backendUrl = `https://${backendUrl}`;
        }

        return [
            {
                source: '/api/:path*',
                destination: `${backendUrl}/api/v1/:path*`,
            },
        ]
    },
}

module.exports = nextConfig
