/* ==========================================================
   barber-dashboard.js

   Levelz Cuts - Barber Dashboard
========================================================== */





/* ==========================================================
   CLOCK
========================================================== */

function updateBarberClock() {

    const clock = document.getElementById("clock");

    if (!clock) {
        return;
    }

    clock.textContent = new Date().toLocaleTimeString();

}


setInterval( updateBarberClock, 1000 );

updateBarberClock();


/* ==========================================================
   DASHBOARD INITIALIZATION
========================================================== */

window.loadBarberDashboard = async function () {

    try {

        await loadBarberUser();

        await loadDashboardStats();

        /*
            Keep the existing dashboard booking
            information populated.
        */

        await loadDashboardUpcomingBookings();

        await loadDashboardBreaks();

    }

    catch (error) {

        console.error(
            "Unable to load barber dashboard:",
            error
        );

    }

};


/* ==========================================================
   USER
========================================================== */

/* ==========================================================
   USER
========================================================== */

window.loadBarberUser = async function () {

    try {

        const data =
            await apiRequest("/staffs/staff/me/");


        const userName =
            document.getElementById("userName");


        if (userName) {

            userName.textContent =
                data.name ||
                data.full_name ||
                data.username ||
                "";

        }


        const avatar =
            document.getElementById("avatar");


        if (avatar) {

            const name =
                data.name ||
                data.full_name ||
                data.username ||
                "";


            avatar.textContent =
                name
                    ? name.charAt(0).toUpperCase()
                    : "";

        }


        /*
         * Return the user data so other dashboard
         * components can use the same endpoint.
         */
        return data;

    }

    catch (error) {

        console.error(
            "Unable to load barber profile:",
            error
        );

        return null;

    }

};



/* ==========================================================
   DASHBOARD STATS
========================================================== */

async function loadDashboardStats() {

    try {

        const data = await apiRequest( "/dashboard/barber/stats/" );


        const current = data?.current || null;


        const next = data?.next || null;


        const todayBookings = document.getElementById( "todayBookings" );


        const upcomingBookings = document.getElementById( "upcomingBookings" );


        if (todayBookings) {

            if ( typeof data?.today_count !== "undefined" ) {

                todayBookings.textContent = data.today_count;

            }

        }

        if (upcomingBookings) {

            upcomingBookings.textContent = data.upcoming_count ? "1" : "0";

        }

        const breakStatus = document.getElementById( "breakStatus" );


        if (breakStatus) {

            breakStatus.textContent = data?.break_status || "OFF";

        }

    }

    catch (error) {

        console.error( "Unable to load dashboard stats:", error );

    }

}


/* ==========================================================
   DASHBOARD BOOKINGS
========================================================== */

async function loadDashboardUpcomingBookings() {

    const table = document.getElementById( "upcomingBookingTable" );


    /*
        The dashboard booking table is part
        of the existing dashboard.

        Do not interfere with the new
        Today's Bookings page.
    */

    if (!table) {
        return;
    }


    try {

        const data = await apiRequest( "/bookings/barber/upcoming/today/" );

        let bookings = [];

        if (Array.isArray(data)) {

            bookings = data;

        }

        else if ( Array.isArray(data?.results) ) {

            bookings = data.results;

        }

        else {

            if (data?.current) {

                bookings.push( data.current );

            }

            if (data?.next) {

                bookings.push( data.next );

            }

        }


        renderDashboardBookings( bookings, table );

    }

    catch (error) {

        console.error( "Unable to load dashboard bookings:", error );


        table.innerHTML = `

            <tr>

                <td colspan="6"> Unable to load bookings. </td>

            </tr>

        `;

    }

}


/* ==========================================================
   RENDER DASHBOARD BOOKINGS
========================================================== */

function renderDashboardBookings( bookings, table ) {

    table.innerHTML = "";


    if (!bookings.length) {

        table.innerHTML = `

            <tr>

                <td colspan="6"> No bookings found. </td>

            </tr>

        `;

        return;

    }


    bookings.forEach(
        booking => {

            table.innerHTML += `

                <tr>

                    <td> ${booking.start_time || "-"} </td>

                    <td> ${booking.customer_name || "-"} </td>

                    <td> ${booking.service || "-"} </td>

                    <td> ${booking.hairstyle || "-"} </td>

                    <td> ${booking.color || "-"} </td>

                    <td> ${booking.status || "-"} </td>

                </tr>

            `;

        }
    );

}


/* ==========================================================
   DASHBOARD BREAKS
========================================================== */

async function loadDashboardBreaks() {

    const table =
        document.getElementById(
            "breakTable"
        );


    if (!table) {
        return;
    }


    try {

        const data = await apiRequest( "/break-periods/break/barber/" );


        const breaks =
            Array.isArray(data)
                ? data
                : data?.results || [];


        renderDashboardBreaks(
            breaks,
            table
        );

    }

    catch (error) {

        console.error(
            "Unable to load dashboard breaks:",
            error
        );

    }

}


/* ==========================================================
   RENDER DASHBOARD BREAKS
========================================================== */

function renderDashboardBreaks( breaks, table ) {

    table.innerHTML = "";


    if (!breaks.length) {

        table.innerHTML = `

            <tr>

                <td colspan="4">

                    No break records found.

                </td>

            </tr>

        `;

        return;

    }


    breaks.forEach(
        item => {

            table.innerHTML += `

                <tr>

                    <td>
                        ${item.date || "-"}
                    </td>

                    <td>

                        ${item.start_time || "-"}

                        -

                        ${item.end_time || "-"}

                    </td>

                    <td>
                        ${item.status || item.type || "-"}
                    </td>

                    <td>
                        ${item.reason || "-"}
                    </td>

                </tr>

            `;

        }
    );

}

