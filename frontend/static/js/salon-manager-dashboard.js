/* ==========================================================
    salon-manager-dashboard.js
========================================================== */

/* ==========================================================
   DASHBOARD INITIALIZATION
========================================================== */

window.initDashboardPage = function () {

    loadDashboard();

    const bookingBtn = document.getElementById("dashboardNewBookingBtn");

    if (bookingBtn && !bookingBtn.dataset.bound) {

        bookingBtn.dataset.bound = "true";

        bookingBtn.addEventListener("click", () => {

            window.location.href = "/bookings/";

        });

    }

    const staffBtn = document.getElementById("dashboardNewStaffBtn");

    if (staffBtn && !staffBtn.dataset.bound) {

        staffBtn.dataset.bound = "true";

        staffBtn.addEventListener("click", () => {

            location.hash = "#staff";

        });

    }

    const reportsBtn = document.getElementById("dashboardReportsBtn");

    if (reportsBtn && !reportsBtn.dataset.bound) {

        reportsBtn.dataset.bound = "true";

        reportsBtn.addEventListener("click", () => {

            location.hash = "#reports";

        });

    }

    const viewBookingsBtn = document.getElementById("viewAllBookingsBtn");

    if (viewBookingsBtn && !viewBookingsBtn.dataset.bound) {

        viewBookingsBtn.dataset.bound = "true";

        viewBookingsBtn.addEventListener("click", () => {

            location.hash = "#bookings";

        });

    }

};


/* ==========================================================
   LOAD DASHBOARD
========================================================== */

window.loadDashboard = async function () {

    try {

        await Promise.allSettled([

            loadDashboardStatistics(),
            loadTodayBookings(),
            loadDashboardStaff(),
            loadDashboardActiveBreakMiniDetails(),

        ]);

    }

    catch (error) {

        console.error(error);

        alert("Unable to load dashboard.");

    }

}


/* ==========================================================
   DASHBOARD STATISTICS
========================================================== */

window.loadDashboardStatistics = async function () {

    try {

        const stats = await apiRequest("/dashboard/admin/stats/");

        document.getElementById("userName").textContent = stats.username ?? "unknown";

        document.getElementById("todayBookings").textContent = stats.today_bookings_count ?? 0;

        document.getElementById("staffCount").textContent = stats.active_staffs_count ?? 0;

        document.getElementById("activeBreaks").textContent = stats.active_breaks ?? 0;

        document.getElementById("completedBookings").textContent = stats.completed_bookings_today ?? 0;

    }

    catch (error) {

        console.error("Dashboard statistics:", error);

    }

}


/* ==========================================================
   TODAY BOOKINGS
========================================================== */

window.loadTodayBookings = async function () {

    try {

        const bookings = await apiRequest("/bookings/admin/today/");

        renderTodayBookings(bookings);

    }

    catch (error) {

        console.error("Today's bookings:", error);

    }

}


function renderTodayBookings(bookings) {

    const table = document.getElementById("bookingTable");

    table.innerHTML = "";

    if (!bookings || bookings.length === 0) {

        table.innerHTML = `
            <tr>
                <td colspan="5">
                    No bookings today.
                </td>
            </tr>
        `;

        return;

    }

    bookings.forEach(booking => {

        table.innerHTML += `
            <tr>

                <td>${booking.start_time}</td>

                <td>${booking.customer_name}</td>

                <td>${booking.service_name}</td>

                <td>${booking.staff_name || "-"}</td>

                <td>${booking.status}</td>

            </tr>
        `;

    });

}


/* ==========================================================
   STAFF WORKING TODAY
========================================================== */

window.loadDashboardStaff = async function (){

    try {

        const staff = await apiRequest("/staffs/working/today");

        renderDashboardStaff(staff);

    }

    catch (error) {

        console.error("Dashboard staff:", error);

    }

}


function renderDashboardStaff(staff) {

    const container = document.getElementById("staffContainer");

    container.innerHTML = "";

    if (!staff || staff.length === 0) {

        container.innerHTML = "<p>No staff available.</p>";

        return;

    }

    staff.forEach(member => {

        container.innerHTML += `
            <div class="staff-item">

                <div class="staff-info">

                    <div class="staff-avatar">

                        ${(member.user.username || "?").charAt(0)}

                    </div>

                    <div>

                        <h4>@${member.user.username}</h4>

                    </div>

                </div>

            </div>
        `;

    });

}


/* ==========================================================
   ACTIVE BREAKS DETAILS TODAY
========================================================== */

window.loadDashboardActiveBreakMiniDetails = async function (){

    try {

        const breaks = await apiRequest("/break-periods/active-breaks/");

        renderDashboardActiveBreakMiniDetails(breaks);

    }

    catch (error) {

        console.error("Dashboard staff:", error);

    }

}


function renderDashboardActiveBreakMiniDetails(breaks) {

    const container = document.getElementById("breakContainer");

    container.innerHTML = "";

    if (!breaks || breaks.length === 0) {

        container.innerHTML = "<p>No staff current on break.</p>";

        return;

    }

    breaks.forEach(active_break => {

        container.innerHTML += `
            <div class="break-item">

                <div class="break-info">

                    <div class="break-avatar">

                        ${(active_break.staff_username || "?").charAt(0)}

                    </div>

                    <div>

                        <h4>@${active_break.staff_username}</h4>

                        <p>${active_break.start_time}</p>

                        <p>${active_break.end_time}</p>

                    </div>


                </div>

            </div>
        `;

    });

}

