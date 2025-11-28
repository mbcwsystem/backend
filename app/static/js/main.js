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

function showMessage(text, color="black") {
    const box = document.getElementById("action-message");
    box.style.color = color;
    box.innerText = text;
}

// 공통 함수: 현재 시간 포맷팅
function nowTime() {
    const now = new Date();
    return now.toLocaleString("ko-KR", {
        hour12: false,
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
    });
}

// 공통 함수: 메인페이지 입력 정보 가져오기
function getFormPayload() {
    return {
        username: document.getElementById("main-username").value,
        password: document.getElementById("main-password").value
    };
}

// 공통 함수: 서버에 POST 요청 보내는 함수
async function sendAttendance(endpoint) {
    const payload = getFormPayload();

    if (!payload.username || !payload.password) {
        alert("아이디와 비밀번호를 입력해주세요.");
        return null;
    }

    const res = await fetch(`/api/attendance/${endpoint}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    });

    const data = await res.json();
    return { status: res.status, data };
}

// 출근
async function checkIn() {
    const { status, data } = await sendAttendance("check-in");
    if (!status) return;

    if (status === 200) {
        showMessage(
            `출근 완료!\n아이디: ${data.user_id}\n이름: ${data.user_name}\n시간: ${nowTime()}`,
            "green"
        );
    } else {
        showMessage(`출근 실패 ❌\n${data.detail}`, "red");
    }
}

// 휴식 시작
async function startBreak() {
    const { status, data } = await sendAttendance("break-start");
    if (!status) return;

    if (status === 200) {
        showMessage(
            `휴식 시작!\n아이디: ${data.user_id}\n이름: ${data.user_name}\n시간: ${nowTime()}`,
            "orange"
        );
    } else {
        showMessage(`휴식 시작 실패 ❌\n${data.detail}`, "red");
    }
}

// 휴식 복귀
async function endBreak() {
    const { status, data } = await sendAttendance("break-end");
    if (!status) return;

    if (status === 200) {
        showMessage(
            `휴식 복귀!\n아이디: ${data.user_id}\n이름: ${data.user_name}\n시간: ${nowTime()}`,
            "blue"
        );
    } else {
        showMessage(`복귀 실패 ❌\n${data.detail}`, "red");
    }
}

// 퇴근
async function checkOut() {
    const { status, data } = await sendAttendance("check-out");
    if (!status) return;

    if (status === 200) {
        showMessage(
            `퇴근 완료!\n아이디: ${data.user_id}\n이름: ${data.user_name}\n시간: ${nowTime()}`,
            "purple"
        );
    } else {
        showMessage(`퇴근 실패 ❌\n${data.detail}`, "red");
    }
}