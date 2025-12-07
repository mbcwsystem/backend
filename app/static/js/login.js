function showLogin() {
    document.getElementById("login-box").style.display = "flex";
    document.getElementById("signup-box").style.display = "none";
    document.getElementById("login-tab").classList.add("active");
    document.getElementById("signup-tab").classList.remove("active");
}

function showSignup() {
    document.getElementById("login-box").style.display = "none";
    document.getElementById("signup-box").style.display = "flex";
    document.getElementById("login-tab").classList.remove("active");
    document.getElementById("signup-tab").classList.add("active");
}

/* -------------------
   로그인
-------------------- */
async function login() {
    const payload = {
        username: document.getElementById("login-username").value,
        password: document.getElementById("login-password").value,
    };

    const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (res.status === 200) {
        document.getElementById("login-msg").style.color = "green";
        document.getElementById("login-msg").innerText = "로그인 성공!";
        localStorage.setItem("access_token", data.access_token);
    } else {
        document.getElementById("login-msg").innerText = data.detail || "로그인 실패";
    }
}

/* -------------------
   회원가입
-------------------- */
async function signup() {
    const payload = {
        username: document.getElementById("signup-username").value,
        password: document.getElementById("signup-password").value,
        name: document.getElementById("signup-name").value,
        position: document.getElementById("signup-position").value,
        gender: document.getElementById("signup-gender").value,
        phone: document.getElementById("signup-phone").value,
        email: document.getElementById("signup-email").value,
        is_active: true
    };

    const token = localStorage.getItem("access_token");  // 🔥 로그인에서 받은 관리자 토큰

    const res = await fetch("/api/admin/users/create", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`    // 🔥 반드시 필요
        },
        body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (res.status === 201 || res.status === 200) {
        document.getElementById("signup-msg").style.color = "green";
        document.getElementById("signup-msg").innerText = "회원가입 성공!";
    } else {
        document.getElementById("signup-msg").innerText = data.detail || "회원가입 실패";
    }
}


function goMainPage() {
    window.location.href = "/main";
}

function goSchedulePage() {
    window.location.href = "/schedule";
}

function goCommunityPage() {
    window.location.href = "/community";
}

