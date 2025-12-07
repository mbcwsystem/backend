// 페이지 로딩 시
document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("access_token");

    if (!token) {
        alert("로그인이 필요합니다!");
        window.location.href = "/";
        return;
    }

    const res = await fetch("/api/auth/me", {
        headers: { "Authorization": `Bearer ${token}` }
    });

    if (res.status !== 200) {
        alert("로그인이 필요합니다!");
        window.location.href = "/";
        return;
    }

    const user = await res.json();
    window.currentUser = user;

    document.getElementById("welcome-name").innerText = `${user.name}님`;
    loadPosts();
});

// 게시글 목록
async function loadPosts() {
    const token = localStorage.getItem("access_token");

    const res = await fetch(`/api/community/posts`, {
        headers: { "Authorization": `Bearer ${token}` },
    });

    const posts = await res.json();
    const postList = document.getElementById("post-list");
    postList.innerHTML = "";

    posts.forEach(post => {
        const li = document.createElement("li");
        li.classList.add("post-item");

        li.innerHTML = `
            <h3 onclick="openPost(${post.id})">${post.title}</h3>
            <span>${post.author_name} · ${formatDate(post.created_at)} · ${post.category}</span>
        `;

        postList.appendChild(li);
    });

}

// 게시글 생성
async function createPost() {
    const token = localStorage.getItem("access_token");

    const data = {
        title: document.getElementById("post-title").value.trim(),
        content: document.getElementById("post-content").value.trim(),
        category: document.getElementById("post-category").value
    };

    if (!data.title || !data.content) {
        alert("제목과 내용을 입력해주세요.");
        return;
    }

    const res = await fetch(`/api/community/posts`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(data)
    });

    const msg = await res.json();

    if (res.status === 200 || res.status === 201) {
        alert("등록 완료!");
        document.getElementById("post-title").value = "";
        document.getElementById("post-content").value = "";
        loadPosts();
    } else {
        console.log(msg); // 디버깅용

        if (Array.isArray(msg.detail)) {
            alert(msg.detail[0].msg);
        } else if (typeof msg.detail === "string") {
            alert(msg.detail);
        } else {
            alert(JSON.stringify(msg));
        }
    }
}


// 게시글 상세 조회
async function openPost(postId) {
    const token = localStorage.getItem("access_token");
    window.currentPostId = postId;

    const res = await fetch(`/api/community/posts/${postId}`, {
        headers: { "Authorization": `Bearer ${token}` }
    });

    const post = await res.json();

    document.getElementById("modal-title").innerText = post.title;
    document.getElementById("modal-author").innerText = `${post.author_name} (${post.author_position})`;
    document.getElementById("modal-content").innerText = post.content;
    document.getElementById("modal-time").innerText = formatDate(post.created_at);

    const deleteButton = document.getElementById("delete-post-btn");
    deleteButton.style.display = (post.author_id === currentUser.id) ? "block" : "none";
    deleteButton.onclick = () => deletePost(post.id);

    renderComments(post.comments);

    document.getElementById("post-modal").style.display = "flex";
}

// 댓글 렌더링
function renderComments(comments) {
    const list = document.getElementById("comment-list");
    list.innerHTML = "";

    comments.forEach(c => {
        const li = document.createElement("li");
        li.innerHTML = `
            <b>${c.author_name}</b> : ${c.content} (${formatDate(c.created_at)})
            ${c.author_id === currentUser.id ? `<button onclick="deleteComment(${c.id})">삭제</button>` : ""}
        `;
        list.appendChild(li);
    });
}

// 댓글 작성
async function createComment() {
    const token = localStorage.getItem("access_token");
    const text = document.getElementById("comment-input").value.trim();

    if (!text) return alert("댓글을 입력하세요.");

    const res = await fetch(`/api/community/posts/${currentPostId}/comments`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ content: text })
    });

    if (res.status === 200) {
        document.getElementById("comment-input").value = "";
        openPost(currentPostId);
    }
}

// 게시글 삭제
async function deletePost(id) {
    const token = localStorage.getItem("access_token");
    if (!confirm("정말 삭제하시겠습니까?")) return;

    const res = await fetch(`/api/community/posts/${id}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
    });

    if (res.status === 200) {
        alert("삭제 완료!");
        closeModal();
        loadPosts();
    }
}

// 댓글 삭제
async function deleteComment(id) {
    const token = localStorage.getItem("access_token");

    const res = await fetch(`/api/community/comments/${id}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
    });

    if (res.status === 200) openPost(currentPostId);
}

// 포맷팅
function formatDate(time) {
    return new Date(time).toLocaleString("ko-KR", { hour12: false });
}

// 뒤로가기
function goBack() {
    window.location.href = "/";
}

// 모달 닫기
function closeModal() {
    document.getElementById("post-modal").style.display = "none";
}
