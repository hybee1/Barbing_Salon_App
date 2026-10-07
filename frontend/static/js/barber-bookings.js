/* ==========================================================
   barber-bookings.js

   Levelz Cuts - Barber Today's Bookings
========================================================== */


/* ==========================================================
   STATE
========================================================== */

let barberBookingsInitialized = false;

let selectedBarberBooking = null;


/* ==========================================================
   INITIALIZE
========================================================== */

window.initBarberBookings = function () {

    console.log("[BARBER BOOKINGS] initBarberBookings() called");


    if (barberBookingsInitialized) {

        console.log(
            "[BARBER BOOKINGS] Already initialized"
        );

        return;

    }


    barberBookingsInitialized = true;


    initBookingStatusControls();

    initCreateBookingButtons();

};


/* ==========================================================
   CREATE BOOKING BUTTONS
========================================================== */

function initCreateBookingButtons() {

    const dashboardButton =
        document.getElementById(
            "createBookingBtn"
        );


    if (dashboardButton) {

        dashboardButton.addEventListener(
            "click",
            navigateToCreateBooking
        );

    }


    const bookingsButton =
        document.getElementById(
            "todayCreateBookingBtn"
        );


    if (bookingsButton) {

        bookingsButton.addEventListener(
            "click",
            navigateToCreateBooking
        );

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

    console.log(
        "[BARBER BOOKINGS] loadBarberBookings() CALLED"
    );


    try {

        console.log(
            "[BARBER BOOKINGS] Calling API:"
        );

        console.log( "/bookings/barber/today/" );


        const data = await apiRequest( "/bookings/barber/today/" );


        console.log(  "[BARBER BOOKINGS] API RESPONSE:", data );


        const bookings = normalizeBookings(data);


        console.log( "[BARBER BOOKINGS] NORMALIZED BOOKINGS:", bookings  );


        selectedBarberBooking = null;


        hideBookingStatusCard();


        renderBarberBookings(
            bookings
        );

    }

    catch (error) {

        console.error("[BARBER BOOKINGS] Unable to load today's bookings:", error );


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


    if (Array.isArray(data?.results)) {

        return data.results;

    }


    const bookings = [];


    if (data?.current) {

        bookings.push(
            data.current
        );

    }


    if (data?.next) {

        bookings.push(
            data.next
        );

    }


    return bookings;

}


/* ==========================================================
   RENDER TODAY'S BOOKINGS
========================================================== */

function renderBarberBookings(bookings) {

    console.log(
        "[BARBER BOOKINGS] renderBarberBookings():",
        bookings
    );


    const table =
        document.getElementById(
            "todayBookingTable"
        );


    if (!table) {

        console.error(
            "[BARBER BOOKINGS] #todayBookingTable NOT FOUND"
        );

        return;

    }


    table.innerHTML = "";


    if (!bookings.length) {

        table.innerHTML = `

            <tr>

                <td colspan="8">

                    No bookings found for today.

                </td>

            </tr>

        `;

        return;

    }


    bookings.forEach(
        booking => {

            const row =
                document.createElement("tr");


            /*
                STATUS
            */

            const bookingStatus =
                String(
                    booking?.status || "-"
                ).toUpperCase();


            /*
                BOOKING REFERENCE

                Use the real value returned by
                the backend.

                Do NOT use customer name,
                service name, etc. as reference.
            */

            const bookingReference =
                booking?.booking_reference ??
                booking?.reference ??
                booking?.booking_ref ??
                booking?.reference_code ??
                "-";


            /*
                ROW ID
            */

            row.dataset.bookingId =
                booking?.id ?? "";


            row.classList.add(
                "booking-selectable-row"
            );


            /*
                IMPORTANT:

                EXACTLY 8 TDs.

                1. Select
                2. Booking Reference
                3. Time
                4. Customer
                5. Service
                6. Hairstyle
                7. Color
                8. Status
            */

            row.innerHTML = `

                <!-- 1. SELECT -->

                <td class="booking-select-cell">

                    <label
                        class="booking-row-checkbox"
                        aria-label="Select booking"
                    >

                        <input type="checkbox" class="booking-checkbox" value="${escapeBookingHtml(
                                booking?.id ?? ""
                            )}"
                        >

                        <span class="custom-booking-checkbox" ></span>

                    </label>

                </td>


                <!-- 2. BOOKING REFERENCE -->

                <td>

                    <span class="booking-reference">

                        ${escapeBookingHtml( bookingReference )}

                    </span>

                </td>


                <!-- 3. TIME -->

                <td> ${escapeBookingHtml( booking?.start_time ?? "-" )} </td>

                <!-- 4. CUSTOMER -->

                <td> ${escapeBookingHtml( booking?.customer_name ?? "-" )} </td>


                <!-- 5. SERVICE -->

                <td> ${escapeBookingHtml( booking?.service ?? "-" )} </td>


                <!-- 6. HAIRSTYLE -->

                <td> ${escapeBookingHtml( booking?.hairstyle ?? "-" )} </td>

                <!-- 7. COLOR -->

                <td> ${escapeBookingHtml( booking?.color ?? "-" )} </td>


                <!-- 8. STATUS -->

                <td>

                    <span class="booking-status-badge ${getBookingStatusClass( bookingStatus)}">

                        <span class="booking-status-dot"></span>

                        ${escapeBookingHtml(bookingStatus)}

                    </span>

                </td>

            `;

            /* ==========================================================
               ROW CLICK
            ========================================================== */

            row.addEventListener("click", function (event) {

                    /*
                        Ignore checkbox clicks because the checkbox
                        has its own selection handler.
                    */

                    if ( event.target.closest( ".booking-row-checkbox" ) ) {

                        return;

                    }


                    console.log( "[BARBER BOOKINGS] Row clicked:", booking );

//                    selectBarberBooking( booking, row );
                    selectBarberBooking(booking, row).catch(error => {
                        console.error(
                            "[BARBER BOOKINGS] Failed to select booking:",
                            error
                        );
                    });

                }
            );


            /* ==========================================================
               CHECKBOX
            ========================================================== */

            const checkbox = row.querySelector( ".booking-checkbox" );


            if (checkbox) {

                checkbox.addEventListener( "click", function (event) {

                        event.stopPropagation();

                    }
                );


                checkbox.addEventListener(  "change", function (event) {

                        event.stopPropagation();


                        if (checkbox.checked) {

                            console.log(
                                "[BARBER BOOKINGS] Checkbox selected:",
                                booking
                            );


                            selectBarberBooking( booking, row );

                        }

                        else {

                            console.log(
                                "[BARBER BOOKINGS] Checkbox deselected:",
                                booking
                            );


                            if ( selectedBarberBooking?.id === booking?.id ) {

                                selectedBarberBooking = null;

                                hideBookingStatusCard();

                            }

                        }

                    }
                );

            }

table.appendChild(row);

            table.appendChild(row);

        }
    );

}


/* ==========================================================
   BOOKING STATUS CONTROLS
========================================================== */

function initBookingStatusControls() {

    const statusSelect =
        document.getElementById("bookingStatusSelect");


    const updateButton =
        document.getElementById("updateBookingStatusBtn");


    if (statusSelect) {

        statusSelect.addEventListener("change", function () {

            const selectedStatus =
                String(statusSelect.value || "").toUpperCase();


            /*
             * Show cancellation reason only when
             * CANCELLED is selected.
             */

            toggleCancellationReason(
                selectedStatus === "CANCELLED"
            );


            if (updateButton) {

                updateButton.disabled =
                    !selectedBarberBooking ||
                    !selectedStatus;

            }

        });

    }


    if (updateButton) {

        updateButton.addEventListener(
            "click",
            handleBookingStatusUpdate
        );

    }

}


/* =========================================================
    TOGGLE CANCELLATION REASON
=========================================================== */
function toggleCancellationReason(show) {

    const group = document.getElementById("cancellationReasonGroup");

    const textarea = document.getElementById("reasonCancellation");

    if (!group || !textarea) {

        return;

    }

    group.hidden = !show;

    if (show) {

        textarea.focus();

    }

    else {

        textarea.value = "";

    }

}


/* ==========================================================
   SELECT BOOKING
========================================================== */

async function selectBarberBooking( booking, row) {

    if (!booking?.id) {

        console.warn(
            "[BARBER BOOKINGS] Cannot select booking without ID:",
            booking
        );

        return;

    }


    /*
        Remove selected state from all rows.
    */

    document
        .querySelectorAll(
            "#todayBookingTable .booking-selectable-row"
        )
        .forEach(
            item => {

                item.classList.remove( "selected" );


                /*
                    Uncheck every other checkbox.
                */

                const checkbox = item.querySelector( ".booking-checkbox" );

                if (checkbox) {

                    checkbox.checked = false;

                }

            }
        );


    /*
        Mark selected row.
    */

    if (row) {

        row.classList.add( "selected" );


        /*
            Check this booking's checkbox.
        */

        const checkbox = row.querySelector( ".booking-checkbox" );


        if (checkbox) {

            checkbox.checked = true;

        }

    }


    /*
        Store selected booking.
    */

    selectedBarberBooking = booking;

    console.log("[BARBER BOOKINGS] Selected booking:", selectedBarberBooking );


    /*
        Populate:

        - Customer
        - Booking details
        - Current status
        - Available status changes
    */

    await populateBookingStatusControls( booking );


    /*
        Show the status card.
    */

    const card = document.getElementById("bookingStatusCard" );


    if (card) {

        card.hidden = false;

    }

}



/* ==========================================================
   POPULATE SELECTED BOOKING PANEL
========================================================== */

async function populateBookingStatusControls(booking) {

    const customer = document.getElementById( "selectedBookingCustomer" );

    const details = document.getElementById("selectedBookingDetails" );

    const currentStatus = document.getElementById( "selectedBookingCurrentStatus" );

    const statusSelect = document.getElementById("bookingStatusSelect");

    const updateButton = document.getElementById( "updateBookingStatusBtn" );

    const status = String(booking?.status || "").toUpperCase();

    if (customer) {

        customer.textContent = booking?.customer_name || "Customer";

    }


    if (details) {

        details.textContent = [

            booking?.start_time || "-",

            booking?.service || "-",

            booking?.hairstyle || "-",

            booking?.color || "-"

        ].join("  •  ");

    }


    if (currentStatus) {

        currentStatus.textContent = status || "-";


        currentStatus.className = `booking-status-badge ${ getBookingStatusClass(status) }`;

    }


    if (statusSelect) {

        statusSelect.innerHTML = "";


        statusSelect.appendChild( createStatusOption( "", "Select status" ) );

        const statuses = await getAvailableBookingStatuses();

        statuses.forEach(
            nextStatus => {

                statusSelect.appendChild( createStatusOption( nextStatus, formatBookingStatus( nextStatus ) ) );

            }
        );


        statusSelect.value = "";

    }


    if (updateButton) {

        updateButton.disabled = true;

    }

}


/* ==========================================================
   AVAILABLE STATUS TRANSITIONS
========================================================== */

async function getAvailableBookingStatuses() {

    const data = await apiRequest("/bookings/statuses/");


    console.log(  "[BARBER BOOKINGS] RAW STATUS RESPONSE:", data );


    return Array.isArray(data?.statuses) ? data.statuses : [];

}



/* ==========================================================
   CREATE STATUS OPTION
========================================================== */

function createStatusOption( value, text ) {

    const option = document.createElement( "option" );

    option.value = value;

    option.textContent = text;

    return option;

}


/* ==========================================================
   UPDATE BOOKING STATUS
========================================================== */

async function handleBookingStatusUpdate() {

    if (!selectedBarberBooking?.id) {

        return;

    }


    const statusSelect = document.getElementById("bookingStatusSelect");


    const button = document.getElementById("updateBookingStatusBtn");


    const reasonCancellation = document.getElementById("reasonCancellation");


    const newStatus = String(statusSelect?.value || "").toUpperCase();

    if (!newStatus) {

        return;

    }


    /*
     * Get cancellation reason.
     */

    const cancellationReason = String(reasonCancellation?.value || "").trim();


    /*
     * Cancellation requires a reason.
     */

    if ( newStatus === "CANCELLED" && !cancellationReason ) {

        alert( "Please provide a reason for cancelling this booking." );

        reasonCancellation?.focus();

        return;

    }


    const statusLabel = formatBookingStatus(newStatus);

    if ( !confirm( `Are you sure you want to change this booking to ${statusLabel}?` ) ) {

        return;

    }


    if (button) {

        button.disabled = true;

        button.innerHTML = `
            <i class="fa-solid fa-spinner fa-spin"></i>
            Updating...
        `;

    }


    try {

        const bookingId = selectedBarberBooking.id;

        /*
         * Start with the existing booking data.
         */

        const bookingData = { ...selectedBarberBooking, status: newStatus  };


        /*
         * Add cancellation reason only when
         * the booking is being cancelled.
         */

        if (newStatus === "CANCELLED") {

            bookingData.reason_for_cancellation = cancellationReason;

        }


        console.log( "[BARBER BOOKINGS] Updating booking:", bookingData );

        await apiRequest( `/bookings/${bookingId}/update-status/`, "PATCH", bookingData  );

        alert( `Booking updated to ${statusLabel}.`  );

        await window.loadBarberBookings?.();

        await window.loadBarberDashboard?.();

    }

    catch (error) {

        console.error( "[BARBER BOOKINGS] Unable to update booking status:", error );


        alert( error?.message ||
                error?.details ||
                error?.error?.details ||
                error?.error?.details?.[0] ||
                error?.detail ||
                error?.error?.detail ||
                error?.error?.detail?.[0] ||
                "Unable to update booking status." );


        if (button) {

            button.disabled = false;

            button.innerHTML = `
                <i class="fa-solid fa-check"></i>
                Update Status
            `;

        }

    }

}




/* ==========================================================
   HIDE STATUS CARD
========================================================== */

function hideBookingStatusCard() {

    const card =
        document.getElementById(
            "bookingStatusCard"
        );


    if (card) {

        card.hidden = true;

    }


    const statusSelect = document.getElementById( "bookingStatusSelect" );


    if (statusSelect) {

        statusSelect.innerHTML = `

            <option value=""> Select status </option>

        `;

    }


    const updateButton = document.getElementById( "updateBookingStatusBtn"  );


    if (updateButton) {

        updateButton.disabled = true;


        updateButton.innerHTML = `

            <i class="fa-solid fa-check"></i>

            Update Status

        `;

    }


    document.querySelectorAll( "#todayBookingTable .booking-selectable-row" )
        .forEach(
            row => {

                row.classList.remove( "selected" );

            }
        );

}


/* ==========================================================
   STATUS HELPERS
========================================================== */

function formatBookingStatus(status) {

    return String( status || "" )
        .replaceAll(
            "_", " "  )
        .replace( /\b\w/g, letter => letter.toUpperCase() );

}


function getBookingStatusClass(status) {

    return `status-${String( status || ""  ).toLowerCase()}`;

}


/* ==========================================================
   ERROR
========================================================== */

function renderBookingError() {

    const table = document.getElementById( "todayBookingTable" );

    if (!table) {

        return;

    }

    hideBookingStatusCard();

    table.innerHTML = `

        <tr>

            <td colspan="8"> Unable to load today's bookings. </td>

        </tr>

    `;

}


/* ==========================================================
   HTML ESCAPE
========================================================== */

function escapeBookingHtml(value) {

    if ( value === null || value === undefined ) {

        return "";

    }


    return String(value)

        .replaceAll( "&", "&amp;" )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );

}
