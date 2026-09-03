
/* ==========================================================
   Logout
========================================================== */

async function logout() {

    try {

        await fetch(`${BASE_URL}/auth/logout/`, {
            method: "POST",
            credentials: "include"
        });

    } catch (error) {

        console.error("Logout failed:", error);

    } finally {

        localStorage.removeItem("userData");

        window.location.href = "/staff/login/";

    }

}


/* =====================================
   USER
===================================== */

async function loadUser() {

    try {

        const user = await apiRequest("/api/accounts/me/");

        document.getElementById("userName").textContent =
            user.full_name;

        document.getElementById("avatar").textContent =
            user.full_name.charAt(0).toUpperCase();

    } catch (error) {

        console.error(error);

        logout();

    }

}

/* =====================================
   CLOCK
===================================== */

function startClock() {

    const clock = document.getElementById("clock");

    function update() {

        const now = new Date();

        clock.innerHTML = `
            <strong>${now.toLocaleTimeString()}</strong>
            <span>${now.toDateString()}</span>
        `;

    }

    update();

    setInterval(update, 1000);

}


/* =====================================
   DASHBOARD
===================================== */

async function loadDashboard() {

    try {

        const data = await apiRequest("/api/dashboard/manager/");

        renderStats(data.stats);
        renderBookings(data.bookings);
        renderStaff(data.staffs);
        renderTimeline(data.timeline);

    } catch (error) {

        console.error(error);

        alert(error.detail || "Unable to load dashboard.");

    }

}

/* =====================================
   STATS
===================================== */

function renderStats(stats) {

    document.getElementById("todayBookings").textContent =
        stats.today_bookings;

    document.getElementById("staffCount").textContent =
        stats.active_staff;

    document.getElementById("activeBreaks").textContent =
        stats.breaks;

    document.getElementById("completedBookings").textContent =
        stats.completed_bookings;

}

/* =====================================
   BOOKINGS
===================================== */

function renderBookings(bookings) {

    const body = document.getElementById("bookingTable");

    body.innerHTML = "";

    bookings.forEach(b => {

        body.innerHTML += `
<tr>

    <td>${b.start_time}</td>

    <td>${b.customer_name}</td>

    <td>${b.service}</td>

    <td>${b.staff}</td>

    <td>
        <span class="badge badge-${badge(b.status)}">
            ${b.status}
        </span>
    </td>

</tr>
`;

    });

}


function badge(status) {

    status = status.toLowerCase();

    if (status === "confirmed") return "confirmed";
    if (status === "completed") return "completed";
    if (status === "cancelled") return "cancelled";

    return "progress";

}


/* =====================================
   STAFF
===================================== */

function renderStaff(staffs) {

    const wrapper = document.getElementById("staffContainer");

    wrapper.innerHTML = "";

    staffs.forEach(st => {

        wrapper.innerHTML += `
            <div class="staff-item">

                <div class="staff-info">

                    <div class="staff-avatar">
                        ${st.name.charAt(0).toUpperCase()}
                    </div>

                    <div>
                        <h4>${st.name}</h4>
                        <p>${st.department}</p>
                    </div>

                </div>

                <div class="${availabilityClass(st.status)}">
                    ${st.status}
                </div>

            </div>
        `;

    });

}

function availabilityClass(status) {

    status = status.toLowerCase();

    if (status === "available") return "available";
    if (status === "break") return "break";

    return "busy";

}

/* =====================================
   TIMELINE
===================================== */

function renderTimeline(events) {

    const box = document.getElementById("timelineContainer");

    box.innerHTML = "";

    events.forEach(e => {

        box.innerHTML += `
            <div class="timeline-item">

                <div class="timeline-time">
                    ${e.time}
                </div>

                <div class="timeline-content">
                    <strong>${e.title}</strong>
                    <p>${e.description}</p>
                </div>

            </div>
        `;

    });

}

/* =====================================
   BOOKING DETAILS
===================================== */

async function viewBooking(id) {

    try {

        const booking = await apiRequest(`/api/bookings/${id}/`);

        alert(`Booking Reference: ${booking.booking_reference}

Customer: ${booking.customer_name}

Phone: ${booking.phone_number}

Service: ${booking.service}

Staff: ${booking.barber}

Date: ${booking.booking_date}

Time:
${booking.start_time} - ${booking.end_time}

Status:
${booking.status}`);

    } catch (error) {

        console.error(error);

        alert("Unable to load booking.");

    }

}

/* =====================================
   AUTO REFRESH
===================================== */

/*setInterval(loadDashboard, 30000);*/

setInterval(() => {

    const dashboard =
        document.getElementById("dashboardPage");

    if (!dashboard.hidden) {

        loadDashboard();

    }

}, 30000);

/* =====================================
   START
===================================== */

document.addEventListener("DOMContentLoaded", () => {

    loadUser();

    loadDashboard();

    startClock();

});

