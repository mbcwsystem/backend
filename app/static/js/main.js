// 메인 페이지 접근 시 사용자 이름 표시
document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
        alert("로그인이 필요합니다!");
        window.location.href = "/";
        return;
    }

    // /api/auth/me 로 사용자 정보 확인
    const res = await fetch("/api/auth/me", {
        headers: { "Authorization": `Bearer ${token}` }
    });

    if (res.status !== 200) {
        alert("로그인이 필요합니다!");
        window.location.href = "/";
        return;
    }

    const user = await res.json();
    document.getElementById("welcome-text").innerText = `${user.name}님 환영합니다!`;
});

// --- 출근 / 휴식 / 복귀 / 퇴근 버튼 기능 (추후 API 연동 가능) ---

function checkIn() {
    alert("출근 처리!");
}

function startBreak() {
    alert("휴식 시작!");
}

function endBreak() {
    alert("휴식 복귀!");
}

function checkOut() {
    alert("퇴근 처리!");
}