
/* ==========================================================
    salon-manager-bookings.js
========================================================== */



/* ==========================================================
   BOOKING PAGINATION STATE
========================================================== */

let managerBookings = [];

let currentBookingPage = 1;

const BOOKINGS_PER_PAGE = 10;


/* ==========================================================
   BOOKING MANAGEMENT
========================================================== */

window.initBookingPage = function () {

    const searchButton = document.getElementById("searchBookings");

    if(searchButton){

        searchButton.addEventListener( "click", loadBookings );

    }


    const clearButton = document.getElementById("clearBookingFilters");

    if(clearButton){

        clearButton.addEventListener( "click", clearBookingFilters );

    }

    const newBookingBtn = document.getElementById("newBookingBtn");

    if(newBookingBtn){

        newBookingBtn.addEventListener( "click", () => {
                window.location.href="/bookings/";
            }
        );

    }


    document .querySelectorAll( "#bookingStartDate, #bookingEndDate" )
        .forEach(input => {

            input.addEventListener( "keydown",
                function(e){

                    if(e.key === "Enter"){

                        loadBookings();

                    }

                }
            );

        });


    /* ======================================================
       PAGINATION BUTTONS
    ====================================================== */

    const previousButton = document.getElementById("prevBookingPage");

    const nextButton = document.getElementById("nextBookingPage");

    if(previousButton){

        previousButton.addEventListener("click", previousBookingPage);

    }

    if(nextButton){

        nextButton.addEventListener("click", nextBookingPage );

    }

};


/* ==========================================================
   LOAD BOOKINGS
========================================================== */

/* ==========================================================
   LOAD BOOKINGS
========================================================== */

window.loadBookings = async function () {

    try {

        let filter = false;

        const startDate = document.getElementById( "bookingStartDate" )?.value || "";


        const endDate = document.getElementById( "bookingEndDate"  )?.value || "";


        const status = document.getElementById( "bookingStatusFilter" )?.value || "";


        const params = new URLSearchParams();


        /* ==================================================
           DATE VALIDATION
        ================================================== */

        if(startDate && endDate){

            if(endDate < startDate){

                alert( "The end date cannot be earlier than the start date." );

                return;

            }

            filter = true;

        }

        if(startDate || endDate){

            if( (startDate && !endDate) || (!startDate && endDate) ){

                alert(
                    "Please enter start and end date to search for bookings in that date range."
                );

                return;

            }

        }

        /* ==================================================
           DATE PARAMETERS
        ================================================== */

        if(startDate){

            params.append( "start_date", startDate );

        }

        if(endDate){

            params.append( "end_date", endDate );

        }

        /* ==================================================
           STATUS
        ================================================== */

        if(status){

            params.append( "status", status );

            filter = true;

        }


        /* ==================================================
           LOAD DATA
        ================================================== */

        let bookings = null;

        if(filter){

            bookings = await apiRequest( `/bookings/?${params.toString()}`  );

        }

        else{

            bookings = await apiRequest( `/bookings/last7days/`  );

        }

        /* ==================================================
           STORE BOOKINGS
        ================================================== */

        managerBookings = Array.isArray(bookings) ? bookings : [];

        /* ==================================================
           RESET PAGINATION
        ================================================== */

        currentBookingPage = 1;

        /* ==================================================
           RENDER FIRST PAGE
        ================================================== */

        renderManagerBookings();


    }

    catch(error){

        console.error(error);

        alert("Unable to load bookings.");

    }

};


/* ==========================================================
   RENDER BOOKINGS
========================================================== */

function renderManagerBookings(){

    const body = document.getElementById( "managerBookingTable" );


    if(!body){
        return;
    }

    body.innerHTML = "";


    /* ======================================================
       NO BOOKINGS
    ====================================================== */

    if(
        !managerBookings ||
        managerBookings.length === 0
    ){

        body.innerHTML = `
            <tr>
                <td colspan="7"> No bookings found. </td>
            </tr>
        `;


        updateBookingPagination();

        return;

    }


    /* ======================================================
       PAGINATION CALCULATIONS
    ====================================================== */

    const startIndex = (currentBookingPage - 1) * BOOKINGS_PER_PAGE;

    const endIndex = startIndex + BOOKINGS_PER_PAGE;


    const bookingsForCurrentPage = managerBookings.slice( startIndex, endIndex );

    /* ======================================================
       RENDER CURRENT PAGE
    ====================================================== */

    bookingsForCurrentPage.forEach(
        booking => {

            body.innerHTML += `

                <tr>

                    <td> ${booking.booking_reference} </td>

                    <td> ${booking.customer_name} </td>

                    <td> ${booking.service_name} </td>

                    <td> ${booking.booking_date} </td>

                    <td> ${booking.start_time} </td>

                    <td> ${booking.status} </td>

                    <td>

                        <button class="gold-btn" onclick="viewBooking(${booking.id})" >
                            View
                        </button>

                    </td>

                </tr>

            `;

        }
    );


    /* ======================================================
       UPDATE PAGINATION UI
    ====================================================== */

    updateBookingPagination();

}


/* ==========================================================
   UPDATE BOOKING PAGINATION UI
========================================================== */

function updateBookingPagination(){

    const info = document.getElementById( "bookingPaginationInfo" );


    const pageNumber = document.getElementById( "bookingPageNumber" );


    const previousButton = document.getElementById( "prevBookingPage" );

    const nextButton = document.getElementById( "nextBookingPage" );


    const totalBookings = managerBookings.length;


    const totalPages = Math.ceil( totalBookings / BOOKINGS_PER_PAGE );


    /* ======================================================
       NO BOOKINGS
    ====================================================== */

    if(totalBookings === 0){

        if(info){

            info.textContent = "Showing 0–0 of 0";

        }

        if(pageNumber){

            pageNumber.textContent = "Page 1";

        }

        if(previousButton){

            previousButton.disabled = true;

        }

        if(nextButton){

            nextButton.disabled = true;

        }

        return;

    }


    /* ======================================================
       CURRENT RANGE
    ====================================================== */

    const startIndex = (currentBookingPage - 1) * BOOKINGS_PER_PAGE;


    const start = startIndex + 1;


    const end = Math.min( startIndex + BOOKINGS_PER_PAGE, totalBookings );


    /* ======================================================
       PAGINATION TEXT
    ====================================================== */

    if(info){

        info.textContent = `Showing ${start}–${end} of ${totalBookings}`;

    }


    if(pageNumber){

        pageNumber.textContent = `Page ${currentBookingPage} of ${totalPages}`;

    }


    /* ======================================================
       BUTTON STATES
    ====================================================== */

    if(previousButton){

        previousButton.disabled = currentBookingPage <= 1;

    }


    if(nextButton){

        nextButton.disabled = currentBookingPage >= totalPages;

    }

}


/* ==========================================================
   PREVIOUS BOOKING PAGE
========================================================== */

function previousBookingPage(){

    if(currentBookingPage <= 1){

        return;

    }


    currentBookingPage--;


    renderManagerBookings();


    scrollToBookingTable();

}


/* ==========================================================
   NEXT BOOKING PAGE
========================================================== */

function nextBookingPage(){

    const totalPages =
        Math.ceil(
            managerBookings.length /
            BOOKINGS_PER_PAGE
        );


    if(currentBookingPage >= totalPages){

        return;

    }


    currentBookingPage++;


    renderManagerBookings();


    scrollToBookingTable();

}


/* ==========================================================
   SCROLL BACK TO TABLE
========================================================== */

function scrollToBookingTable(){

    const table =
        document.querySelector(
            ".booking-table-card"
        );


    if(!table){

        return;

    }


    table.scrollIntoView({

        behavior:"smooth",

        block:"start"

    });

}


/* ==========================================================
   CLEAR FILTERS
========================================================== */

window.clearBookingFilters = function(){

    document.getElementById(
        "bookingStartDate"
    ).value = "";


    document.getElementById(
        "bookingEndDate"
    ).value = "";


    document.getElementById(
        "bookingStatusFilter"
    ).value = "";


    currentBookingPage = 1;


    loadBookings();

};

/* ==========================================================
   Render the details
========================================================== */

function renderBookingModal(bookings) {

    if (!bookings || bookings.length === 0) {

        document.getElementById("bookingDetails").innerHTML =
            "<p>No booking found.</p>";

        return;
    }


    const booking = bookings[0];

    const details = document.getElementById("bookingDetails");


    let statusClass = "";

    switch (booking.status?.toUpperCase()) {

        case "CONFIRMED":
            statusClass = "status-confirmed";
            break;

        case "COMPLETED":
            statusClass = "status-completed";
            break;

        case "CANCELLED":
            statusClass = "status-cancelled";
            break;

        case "PENDING":
            statusClass = "status-pending";
            break;

        case "NO_SHOW":
            statusClass = "status-no-show";
            break;

    }



    details.innerHTML = `

    <div class="booking-section booking-header-section">

        <div class="booking-header-left">

            <h2>
                ${booking.booking_reference}
            </h2>

            <small>
                ${booking.booking_date}
            </small>

        </div>


        <span class="booking-status ${statusClass}">
            ${booking.status}
        </span>


    </div>



    <div class="booking-section">


        <div class="booking-row">

            <div class="booking-field">

                <label>
                    <i class="fa-solid fa-user"></i>
                    Customer
                </label>

                <span>
                    ${booking.customer_name}
                </span>

            </div>


            <div class="booking-field">

                <label>
                    <i class="fa-solid fa-phone"></i>
                    Phone
                </label>

                <span>
                    ${booking.phone_number}
                </span>

            </div>

        </div>


        <div class="booking-row">

            <div class="booking-field">

                <label> <i class="fa-solid fa-envelope"></i> Email </label>

                <span> ${booking.email || "-"} </span>

            </div>

        </div>




        <div class="booking-row">


            <div class="booking-field">

                <label>
                    <i class="fa-solid fa-money-bill"></i>
                    Price
                </label>

                <span class="booking-price">
                    ₦${booking.price}
                </span>

            </div>



            <div class="booking-field">

                <label>
                    <i class="fa-solid fa-globe"></i>
                    Source
                </label>

                <span>
                    ${booking.booking_source}
                </span>

            </div>


        </div>


    </div>





    <div class="booking-section">


        <div class="booking-row">


            <div class="booking-field">

                <label>
                    <i class="fa-solid fa-scissors"></i>
                    Service
                </label>

                <span>
                    ${booking.service_name}
                </span>

            </div>



            <div class="booking-field">

                <label>
                    <i class="fa-solid fa-user-tie"></i>
                    Staff
                </label>

                <span>
                    ${booking.staff_name || "-"}
                </span>

            </div>


        </div>



        <div class="booking-row">


            <div class="booking-field">

                <label>
                    Hairstyle
                </label>

                <span>
                    ${booking.hairstyle_name || "-"}
                </span>

            </div>



            <div class="booking-field">

                <label>
                    Colour
                </label>

                <span>
                    ${booking.color_name || "-"}
                </span>

            </div>


        </div>


    </div>





    ${
        booking.status?.toUpperCase() === "CANCELLED"

        ?

        `

        <div class="cancel-card">

            <h4>
                <i class="fa-solid fa-circle-xmark"></i>
                Booking Cancelled
            </h4>


            <p>
                ${booking.reason_for_cancellation || "No reason provided."}
            </p>


        </div>

        `

        :

        ""

    }






    <div class="booking-section">


        <div class="booking-time">

            <h4> Appointment Time </h4>

            <div class="time-line">

                <div>

                    <small> Arrival </small>

                    <span> ${booking.arrival_time || "-"} </span>

                </div>

                <i class="fa-solid fa-arrow-right"></i>

                <div>

                    <small> Start </small>

                    <span> ${booking.start_time} </span>

                </div>

                <i class="fa-solid fa-arrow-right"></i>

                <div>

                    <small> Finish </small>

                    <span> ${booking.end_time} </span>

                </div>

            </div>

        </div>

    </div>


    `;

}

/* ============================================================
   viewBooking (show more details about a particular booking
=============================================================== */

window.viewBooking = async function(id){

    try{

        const params = new URLSearchParams();

        if (id) {

            params.append("booking_id", id);
        }

        const booking = await apiRequest(`/bookings/?${params.toString()}`);

        renderBookingModal(booking);

        document.getElementById("bookingModal").classList.remove("hidden");

    }

    catch(error){

        console.error(error);

        alert("Unable to load and show booking details.");

    }

}

/* ==========================================================
   Modal Close button
========================================================== */
document.getElementById("closeBookingModal").addEventListener("click",()=>{

    document.getElementById("bookingModal").classList.add("hidden");

});
