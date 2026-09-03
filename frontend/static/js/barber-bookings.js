
/* ==========================================================
   barber-bookings.js

   Levelz Cuts - Barber Today's Bookings
========================================================== */


/* ==========================================================
   STATE
========================================================== */

let barberBookingsInitialized = false;


/* ==========================================================
   INITIALIZE
========================================================== */

window.initBarberBookings = function () {

    if (barberBookingsInitialized) {

        return;

    }


    barberBookingsInitialized = true;

    const form = document.getElementById( "completeBookingForm" );

    if (form) {

        form.addEventListener( "submit", handleCompleteBooking );

    }


    initCreateBookingButtons();

};


/* ==========================================================
   CREATE BOOKING BUTTONS
========================================================== */

function initCreateBookingButtons() {

    const dashboardButton = document.getElementById( "createBookingBtn" );


    if (dashboardButton) {

        dashboardButton.addEventListener( "click", navigateToCreateBooking );

    }


    const bookingsButton = document.getElementById( "todayCreateBookingBtn" );


    if (bookingsButton) {

        bookingsButton.addEventListener( "click", navigateToCreateBooking );

    }

}


/* ==========================================================
   NAVIGATE TO BOOKING CREATION
========================================================== */

function navigateToCreateBooking() {

    window.location.href = "/bookings/";

}


/* ==========================================================
   LOAD TODAY'S BOOKINGS
========================================================== */

window.loadBarberBookings = async function () {

    try {

        const data = await apiRequest( "/bookings/barber/today/" );

        const bookings = normalizeBookings(data);

        renderBarberBookings( bookings );

        populateCompleteBookingSelect( bookings );

    }

    catch (error) {

        console.error( "Unable to load today's bookings:", error );

        renderBookingError();

    }

};


/* ==========================================================
   NORMALIZE API RESPONSE
========================================================== */

function normalizeBookings(data) {

    if (Array.isArray(data)) {

        return data;

    }


    if ( Array.isArray( data?.results ) ) {

        return data.results;

    }

    const bookings = [];

    if (data?.current) {

        bookings.push( data.current );

    }

    if (data?.next) {

        bookings.push( data.next );

    }

    return bookings;

}


/* ==========================================================
   RENDER BOOKINGS
========================================================== */

function renderBarberBookings( bookings ) {

    const table =
        document.getElementById( "todayBookingTable" );


    if (!table) {

        return;

    }


    table.innerHTML = "";


    if (!bookings.length) {

        table.innerHTML = `

            <tr>

                <td colspan="6"> No bookings found for today. </td>

            </tr>

        `;

        return;

    }


    bookings.forEach(

        booking => {

            const row = document.createElement( "tr" );

            row.innerHTML = `

                <td> ${escapeBookingHtml( booking.start_time || "-" )} </td>

                <td> ${escapeBookingHtml( booking.customer_name || "-" )} </td>

                <td> ${escapeBookingHtml( booking.service || "-" )} </td>

                <td> ${escapeBookingHtml( booking.hairstyle || "-" )} </td>

                <td> ${escapeBookingHtml( booking.color || "-" )} </td>

                <td> ${escapeBookingHtml( booking.status || "-" )} </td>

            `;

            table.appendChild(row);

        }
    );

}


/* ==========================================================
   POPULATE COMPLETE BOOKING SELECT
========================================================== */

function populateCompleteBookingSelect( bookings ) {

    const select = document.getElementById( "completeBookingSelect" );


    if (!select) {

        return;

    }


    select.innerHTML = `

        <option value=""> Select booking </option>

    `;


    bookings.forEach(
        booking => {

            /*
                Do not offer bookings that have
                already been completed.
            */

            const status = String( booking.status || "" ).toUpperCase();

            if ( status === "COMPLETED" ) {

                return;

            }

            const option = document.createElement( "option" );

            option.value = booking.id;

            const time = booking.start_time || "-";

            const customer = booking.customer_name || "Customer";

            const service = booking.service || "Service";

            option.textContent = `${time} - ${customer} - ${service}`;

            select.appendChild( option );

        }
    );

}


/* ==========================================================
   MARK BOOKING COMPLETED
========================================================== */

async function handleCompleteBooking( event ) {

    event.preventDefault();

    const select = document.getElementById( "completeBookingSelect" );

    const button = document.getElementById( "completeBookingBtn" );

    const bookingId = select?.value;

    if (!bookingId) {

        alert( "Please select a booking." );

        return;

    }

    if ( !confirm( "Are you sure you want to mark this booking as completed?" ) ) {

        return;

    }

    if (button) {

        button.disabled = true;

        button.innerHTML = `

            <i class="fa-solid fa-spinner fa-spin"></i>

            Completing...

        `;

    }

    try {

        /*
            This uses the same endpoint pattern
            already present in your original
            barber dashboard:

                PATCH /bookings/{id}/finish/

        */

        await apiRequest( `/bookings/${bookingId}/finish/`, "PATCH" );

        alert( "Booking marked as completed." );

        document.getElementById( "completeBookingForm") ?.reset();

        await window.loadBarberBookings?.();

        /*
            Refresh dashboard information too,
            so returning to Dashboard shows the
            latest booking state.
        */

        await window.loadBarberDashboard?.();

    }

    catch (error) {

        console.error( "Unable to complete booking:", error );


        alert( "Unable to mark booking as completed." );

    }

    finally {

        if (button) {

            button.disabled = false;

            button.innerHTML = `

                <i class="fa-solid fa-circle-check"></i>

                Mark Completed

            `;

        }

    }

}


/* ==========================================================
   ERROR
========================================================== */

function renderBookingError() {

    const table = document.getElementById( "todayBookingTable" );


    if (!table) {

        return;

    }


    table.innerHTML = `

        <tr>

            <td colspan="6"> Unable to load today's bookings. </td>

        </tr>

    `;

}


/* ==========================================================
   HTML ESCAPE
========================================================== */

function escapeBookingHtml( value ) {

    if ( value === null || value === undefined ) {

        return "";

    }


    return String(value)

        .replaceAll( "&", "&amp;" )

        .replaceAll( "<", "&lt;" )

        .replaceAll( ">", "&gt;" )

        .replaceAll( '"',  "&quot;" )

        .replaceAll(  "'", "&#039;" );

}