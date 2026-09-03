
// const API = "http://localhost:8000/api";
const API_BASE = "https://untyped-hippopotamic-rosa.ngrok-free.dev/api"

/* CLOCK */
setInterval(() => {
    document.getElementById("clock").innerText =
        new Date().toLocaleTimeString();
}, 1000);

/* LOAD INITIAL DATA */

async function init() {
    loadQueue();
    loadDropdowns();
}

/* QUEUE */

async function loadQueue() {

    const res = await fetch(`${API}/bookings/today/`);
    const data = await res.json();

    document.getElementById("queue").innerHTML = data.map(b => `
        <div class="item">
            <div>
                <b>${b.full_name}</b><br>
                ${b.service.name}
            </div>

            <div>
                ${b.barber.name}<br>
                <small>${b.start_time}</small>
            </div>

            <div>
                <button onclick="startJob(${b.id})">Start</button>
                <button onclick="finishJob(${b.id})">End</button>
            </div>
        </div>
    `).join("");

    document.getElementById("activeJobs").innerText =
        data.filter(x => x.status === "IN_PROGRESS").length;

    document.getElementById("totalBookings").innerText = data.length;
}

/* START JOB */

async function startJob(id) {

    await fetch(`${API}/bookings/${id}/start/`, {
        method: "PATCH"
    });

    loadQueue();
}

/* FINISH JOB */

async function finishJob(id) {

    await fetch(`${API}/bookings/${id}/finish/`, {
        method: "PATCH"
    });

    loadQueue();
}

/* DROPDOWNS */

async function loadDropdowns() {

    const services = await fetch(`${API}/services/`).then(r => r.json());
    const barbers = await fetch(`${API}/barbers/`).then(r => r.json());

    document.getElementById("w_service").innerHTML =
        services.map(s => `<option value="${s.id}">${s.name}</option>`).join("");

    document.getElementById("w_barber").innerHTML =
        barbers.map(b => `<option value="${b.id}">${b.name}</option>`).join("");
}

/* WALK-IN */

async function createWalkIn() {

    const payload = {
        full_name: document.getElementById("w_name").value,
        phone: document.getElementById("w_phone").value,
        service: document.getElementById("w_service").value,
        barber: document.getElementById("w_barber").value,
        walk_in: true
    };

    await fetch(`${API}/bookings/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    loadQueue();
}

init();