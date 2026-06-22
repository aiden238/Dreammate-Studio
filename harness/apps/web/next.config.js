/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // Phase 34 S2 — rewrites 프록시 타임아웃 상향(기본 30s → 120s).
  //   배경: cross-provider critic(Claude 판정)으로 generate 가 ~40~60s 소요 → 기본 30s 에서
  //   프록시가 끊어 500(Internal Server Error). 백엔드는 정상 완료하므로 프록시 한도만 늘린다.
  //   (장기적으로는 SSE/비동기 폴링으로 전환 검토 — ADR-0022 progress 채널 존재.)
  experimental: { proxyTimeout: 120_000 },
  // Phase 1 Slice 6: 단순한 설정. Service Worker / PWA 캐싱은 후속 Slice (7+)에서 도입.
  // 동일-출처 프록시: 브라우저의 /api/* 호출을 백엔드(FastAPI)로 서버사이드 프록시.
  //   → 프론트(:3000)와 API 가 같은 출처가 되어 원격(cloudflare 터널)·LAN·localhost/127.0.0.1
  //     어디서든 동작하고, auth 쿠키가 1st-party 라 SameSite/CORS 교차-출처 문제가 사라진다.
  //   BACKEND_PROXY_URL 로 백엔드 주소 override 가능(기본 http://localhost:8000).
  async rewrites() {
    const backend = process.env.BACKEND_PROXY_URL || "http://localhost:8000";
    return [{ source: "/api/:path*", destination: `${backend}/api/:path*` }];
  },
};

module.exports = nextConfig;
