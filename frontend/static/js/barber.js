
 const API = "http://127.0.0.1:8000/api";
// const API_BASE = "https://untyped-hippopotamic-rosa.ngrok-free.dev/api"

/* CLOCK */
setInterval(() => {
    document.getElementById("clock").innerText =
        new Date().toLocaleTimeString();
}, 1000);

/* INIT */

async function init() {
    loadJobs();
}

/* LOAD JOBS */

async function loadJobs() {

    const res = await fetch(`${API}/barber/me/jobs/`);
    const data = await res.json();

    const current = data.current;
    const next = data.next;

    document.getElementById("currentJob").innerHTML = current
        ? renderJob(current, true)
        : "<p>No active job</p>";

    document.getElementById("nextJob").innerHTML = next
        ? renderJob(next, false)
        : "<p>No upcoming job</p>";
}

/* RENDER */

function renderJob(job, active) {

    return `
        <div class="job-card">
            <b>${job.customer_name}</b><br>
            ${job.service}<br>
            ${job.start_time}

            ${active ? `
                <div style="margin-top:10px;">
                    <button onclick="startJob(${job.id})">Start</button>
                    <button onclick="finishJob(${job.id})">Finish</button>
                </div>
            ` : ""}
        </div>
    `;
}

/* START */

async function startJob(id) {

    await fetch(`${API}/bookings/${id}/start/`, {
        method: "PATCH"
    });

    loadJobs();
}

/* FINISH */

async function finishJob(id) {

    await fetch(`${API}/bookings/${id}/finish/`, {
        method: "PATCH"
    });

    loadJobs();
}

/* STATUS */

async function setStatus(status) {

    await fetch(`${API}/barbers/status/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status })
    });

    alert("Status updated");
}

init();