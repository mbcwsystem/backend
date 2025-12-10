let currentUser = null;
let currentPostId = null;
let currentFilterCategory = "all";


document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("access_token");

    // 토큰 없으면 로그인 페이지로 이동
    if (!token) {
        alert("로그인이 필요한 페이지입니다. 로그인 후 다시 시도해주세요.");
        window.location.href = "/login";
        return;
    }

    try {
        const res = await fetch("/api/auth/me", {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!res.ok) {
            // 토큰이 만료되었거나 유효하지 않은 경우
            localStorage.removeItem("access_token");
            alert("로그인 정보가 만료되었습니다. 다시 로그인해주세요.");
            window.location.href = "/login";
            return;
        }

        const user = await res.json();
        currentUser = user;
        document.getElementById("welcome-name").innerText = `${user.name}님`;
        const commentBtn = document.getElementById("comment-submit-btn");
        if (commentBtn) {
            commentBtn.addEventListener("click", (e) => {
                e.preventDefault();
                createComment();
            });
        }

        await loadPosts();
    } catch (error) {
        console.error(error);
        alert("사용자 정보를 불러오는 중 오류가 발생했습니다.");
        window.location.href = "/login";
    }
});

async function loadPosts() {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    try {
        let url = "/api/community/posts";
        if (currentFilterCategory !== "all") {
            url += `?category=${encodeURIComponent(currentFilterCategory)}`;
        }

        const res = await fetch(url, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!res.ok) {
            console.error("게시글 목록 조회 실패", res.status);
            alert("게시글 목록을 불러오지 못했습니다.");
            return;
        }

        const posts = await res.json();
        const list = document.getElementById("post-list");
        const emptyMessage = document.getElementById("empty-message");

        list.innerHTML = "";

        if (!posts || posts.length === 0) {
            emptyMessage.style.display = "block";
            return;
        } else {
            emptyMessage.style.display = "none";
        }

        posts.forEach(post => {
            const li = document.createElement("li");
            li.classList.add("post-item");
            li.onclick = () => openPost(post.id);

            li.innerHTML = `
                <div class="post-title-row">
                    <span class="badge">${formatCategory(post.category)}</span>
                    <h3 class="post-title">${escapeHtml(post.title)}</h3>
                </div>
                <div class="post-meta">
                    ${escapeHtml(post.author_name)} · ${formatDate(post.created_at)}
                </div>
            `;

            list.appendChild(li);
        });
    } catch (error) {
        console.error(error);
        alert("게시글 목록을 불러오는 중 오류가 발생했습니다.");
    }
}

async function createPost() {
    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("로그인이 필요합니다.");
        window.location.href = "/login";
        return;
    }

    const titleEl = document.getElementById("post-title");
    const contentEl = document.getElementById("post-content");
    const categoryEl = document.getElementById("post-category");

    const title = titleEl.value.trim();
    const content = contentEl.value.trim();
    const category = categoryEl.value;

    if (!title) {
        alert("제목을 입력해주세요.");
        titleEl.focus();
        return;
    }
    if (!content) {
        alert("내용을 입력해주세요.");
        contentEl.focus();
        return;
    }

    const data = { title, content, category };

    try {
        const res = await fetch("/api/community/posts", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(data)
        });

        if (res.status === 201) {
            alert("게시글이 등록되었습니다.");
            // 입력값 초기화
            titleEl.value = "";
            contentEl.value = "";
            categoryEl.value = "free_board";
            await loadPosts();
        } else {
            const errorData = await safeParseJson(res);
            const msg = errorData && errorData.detail
                ? errorData.detail
                : "게시글 등록에 실패했습니다.";
            alert(msg);
        }
    } catch (error) {
        console.error(error);
        alert("게시글 등록 중 오류가 발생했습니다.");
    }
}

async function openPost(id) {
    const token = localStorage.getItem("access_token");
    window.currentPostId = id;
    if (!token) {
        alert("로그인이 필요합니다.");
        window.location.href = "/login";
        return;
    }

    currentPostId = id;

    try {
        const res = await fetch(`/api/community/posts/${id}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!res.ok) {
            alert("게시글을 불러오지 못했습니다.");
            return;
        }

        const post = await res.json();

        document.getElementById("modal-title").innerText = post.title;
        document.getElementById("modal-author").innerText =
            `${post.author_name} (${post.author_position})`;
        document.getElementById("modal-time").innerText = formatDate(post.created_at);
        document.getElementById("modal-content").innerText = post.content;
        document.getElementById("modal-category-badge").innerText =
            formatCategory(post.category);

        const btn = document.getElementById("delete-post-btn");
        // 작성자 본인인 경우에만 삭제 버튼 표시 (관리자 권한은 백엔드에서 검증)
        btn.style.display = (post.author_id === currentUser.id) ? "inline-block" : "none";
        btn.onclick = () => deletePost(id);

        renderComments(post.comments);
        document.getElementById("post-modal").style.display = "flex";
    } catch (error) {
        console.error(error);
        alert("게시글 상세 조회 중 오류가 발생했습니다.");
    }
}

function renderComments(comments) {
    const list = document.getElementById("comment-list");
    list.innerHTML = "";

    if (!comments || comments.length === 0) {
        const li = document.createElement("li");
        li.classList.add("comment-item");
        li.innerHTML = `<div class="comment-body">첫 번째 댓글을 남겨보세요!</div>`;
        list.appendChild(li);
        return;
    }

    comments.forEach(c => {
        const li = document.createElement("li");
        li.classList.add("comment-item");

        li.innerHTML = `
            <div class="comment-header">
                <span class="comment-author">${escapeHtml(c.author_name)} (${escapeHtml(c.author_position)})</span>
                <span class="comment-date">${formatDate(c.created_at)}</span>
            </div>
            <div class="comment-body">${escapeHtml(c.content)}</div>
            ${
                c.author_id === currentUser.id
                    ? `<button class="comment-delete" onclick="deleteComment(${c.id})">삭제</button>`
                    : ""
            }
        `;

        list.appendChild(li);
    });
}

async function createComment() {
    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("로그인이 필요합니다.");
        window.location.href = "/";
        return;
    }

    if (!currentPostId) {
        alert("댓글을 작성할 게시글을 찾을 수 없습니다.");
        return;
    }

    const input = document.getElementById("comment-input");
    const text = input.value.trim();

    if (!text) {
        alert("댓글 내용을 입력해주세요.");
        input.focus();
        return;
    }

    try {
        const res = await fetch(`/api/community/posts/${currentPostId}/comments`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ content: text })
        });

        if (!res.ok) {
            const errorData = await safeParseJson(res);
            const msg = errorData && errorData.detail
                ? errorData.detail
                : "댓글 등록에 실패했습니다.";
            alert(msg);
            return;
        }

        input.value = "";
        await openPost(currentPostId);
    } catch (error) {
        console.error(error);
        alert("댓글 등록 중 오류가 발생했습니다.");
    }
}

function closeModal() {
    document.getElementById("post-modal").style.display = "none";
}

function formatDate(t) {
    if (!t) return "";
    const d = new Date(t);
    if (Number.isNaN(d.getTime())) return "";
    return d.toLocaleString("ko-KR", { hour12: false });
}

function goBack() {
    window.location.href = "/";
}

async function deletePost(id) {
    if (!confirm("정말 이 게시글을 삭제하시겠습니까?")) return;

    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("로그인이 필요합니다.");
        window.location.href = "/login";
        return;
    }

    try {
        const res = await fetch(`/api/community/posts/${id}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!res.ok) {
            const errorData = await safeParseJson(res);
            const msg = errorData && errorData.detail
                ? errorData.detail
                : "게시글 삭제에 실패했습니다.";
            alert(msg);
            return;
        }

        alert("게시글이 삭제되었습니다.");
        closeModal();
        await loadPosts();
    } catch (error) {
        console.error(error);
        alert("게시글 삭제 중 오류가 발생했습니다.");
    }
}

async function deleteComment(id) {
    if (!confirm("댓글을 삭제하시겠습니까?")) return;

    const token = localStorage.getItem("access_token");
    if (!token) {
        alert("로그인이 필요합니다.");
        window.location.href = "/login";
        return;
    }

    try {
        const res = await fetch(`/api/community/comments/${id}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!res.ok) {
            const errorData = await safeParseJson(res);
            const msg = errorData && errorData.detail
                ? errorData.detail
                : "댓글 삭제에 실패했습니다.";
            alert(msg);
            return;
        }

        await openPost(currentPostId);
    } catch (error) {
        console.error(error);
        alert("댓글 삭제 중 오류가 발생했습니다.");
    }
}

/* 카테고리 필터 변경 */
function changeCategoryFilter() {
    const select = document.getElementById("filter-category");
    currentFilterCategory = select.value;
    loadPosts();
}

/* 카테고리 표기 변환 */
function formatCategory(category) {
    switch (category) {
        case "notice":
            return "📢 공지사항";
        case "free_board":
            return "자유게시판";
        case "shift":
            return "🔁 근무교대";
        case "dayoff":
            return "🌴 휴무신청";
        default:
            return category || "";
    }
}

/* 에러 응답 json 안전 파싱 */
async function safeParseJson(res) {
    try {
        return await res.json();
    } catch {
        return null;
    }
}

/* XSS 방지용 이스케이프 */
function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}