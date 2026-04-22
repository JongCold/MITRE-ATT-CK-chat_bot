// =====================================================
// MITRE 분석기 설정 파일
// Cloudflare 터널 주소가 바뀔 때 이 파일만 수정하세요.
// =====================================================

const CONFIG = {
    // Cloudflare Tunnel 실행 후 발급된 주소로 교체하세요.
    // 예: 'https://abc-def-ghi.trycloudflare.com'
    WEBHOOK_URL: 'YOUR_CLOUDFLARE_URL',
    WEBHOOK_PATH: '/webhook/consult-security',

    // n8n 웹훅에 설정한 Basic Auth 인증 정보
    AUTH_USER: 'admin',
    AUTH_PASS: 'password',
};
