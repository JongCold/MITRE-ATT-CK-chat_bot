// =====================================================
// MITRE 분석기 설정 파일
// Cloudflare 터널 주소가 바뀔 때 이 파일만 수정하세요.
// =====================================================

const CONFIG = {
    // 1. 최신 Cloudflare 주소 딱 1개만 입력
    WEBHOOK_URL: "https://sticky-coast-driver-feeling.trycloudflare.com",
    
    // 2. n8n Webhook 경로 유지
    WEBHOOK_PATH: "/webhook/consult-security",
    
    
    // 3. n8n Authentication을 'None'으로 설정했다면 빈 값 유지
    AUTH_USER: "", 
    AUTH_PASS: ""
};
