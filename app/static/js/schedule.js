document.addEventListener("DOMContentLoaded", () => {
    let currentDate = new Date(); // 오늘 날짜

    renderWeek(currentDate);

    document.getElementById("prev-week").addEventListener("click", () => {
        currentDate.setDate(currentDate.getDate() - 7);
        renderWeek(currentDate);
    });

    document.getElementById("next-week").addEventListener("click", () => {
        currentDate.setDate(currentDate.getDate() + 7);
        renderWeek(currentDate);
    });
});

// 이번 주 월요일 구하기
function getMonday(date) {
    const d = new Date(date);
    const day = d.getDay(); // 0 = 일요일
    const diff = (day === 0 ? -6 : 1 - day); // 월요일 기준
    d.setDate(d.getDate() + diff);
    return d;
}

// 날짜 포맷
function formatDate(d) {
    return `${d.getMonth() + 1}/${d.getDate()}`;
}

// 요일명
const dayLabels = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"];

function renderWeek(date) {
    const monday = getMonday(date);
    const days = [];

    for (let i = 0; i < 7; i++) {
        const temp = new Date(monday);
        temp.setDate(monday.getDate() + i);
        days.push(temp);
    }

    // 주간 범위 표시
    document.getElementById("week-range").innerText =
        `${formatDate(days[0])} ~ ${formatDate(days[6])}`;

    // 요일 헤더 채우기
    const weekDaysDiv = document.querySelector(".week-days");
    weekDaysDiv.innerHTML = "";
   dayLabels.forEach((label, i) => {
    let cls = "";

    if (i === 6) cls = "sun";  // 일요일
    if (i === 5) cls = "sat";  // 토요일

    weekDaysDiv.innerHTML += `
        <div class="${cls}">
            ${label}<br>${formatDate(days[i])}
        </div>`;
});

    // 스케줄 그리드 채우기
    const scheduleGrid = document.getElementById("schedule-grid");
    scheduleGrid.innerHTML = "";

    days.forEach((day) => {
        const col = document.createElement("div");
        col.className = "day-column";

        col.innerHTML = `
            <div class="schedule-card">예시 근무 10:00 ~ 17:00</div>
            <div class="schedule-card">예시 근무 14:00 ~ 23:00</div>
        `;

        scheduleGrid.appendChild(col);
    });
}