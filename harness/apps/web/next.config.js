/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // Phase 1 Slice 6: 단순한 설정. Service Worker / PWA 캐싱은 후속 Slice (7+)에서 도입.
};

module.exports = nextConfig;
