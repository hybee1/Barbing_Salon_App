/* ==========================================================
   barber-breaks.js

   Levelz Cuts - Barber Breaks
========================================================== */


/* ==========================================================
   STATE
========================================================== */

let barberBreaksInitialized = false;


/* ==========================================================
   INITIALIZE
========================================================== */

window.initBarberBreaks = function () {

    if (barberBreaksInitialized) {

        return;

    }


    barberBreaksInitialized = true;


    const form =
        document.getElementById(
            "myBreakForm"
        );


    if (form) {

        form.addEventListener(
            "submit",
            createBarberBreak
        );

    }

};


/* ==========================================================
   LOAD BREAKS
========================================================== */

window.loadBarberBreaks = async function () {

    try {

        const data = await apiRequest( "/break-periods/break/barber/" );

        const breaks = Array.isArray(data) ? data : data?.results || [];

        renderBarberBreaks( breaks );


        /*
            Also keep the existing dashboard
            break history populated.
        */

        const dashboardTable = document.getElementById( "breakTable" );

        if (dashboardTable) {

            renderDashboardBreaks( breaks, dashboardTable );

        }

    }

    catch (error) {

        console.error( "Unable to load barber breaks:", error );

        renderBreakError();

    }

};


/* ==========================================================
   RENDER BREAK RECORDS
========================================================== */

function renderBarberBreaks( breaks ) {

    const table = document.getElementById( "myBreakTable" );


    if (!table) {

        return;

    }


    table.innerHTML = "";


    if (!breaks.length) {

        table.innerHTML = `

            <tr>

                <td colspan="5"> No break records found. </td>

            </tr>

        `;

        return;

    }


    breaks.forEach(
        breakRecord => {

            const row = document.createElement( "tr" );

            row.innerHTML = `

                <td> ${escapeBreakHtml( breakRecord.date || "-" )} </td>

                <td> ${escapeBreakHtml( breakRecord.start_time || "-" )} </td>

                <td> ${escapeBreakHtml( breakRecord.end_time || "-" )} </td>

                <td> ${escapeBreakHtml( breakRecord.status || breakRecord.type || "-" )} </td>

                <td> ${escapeBreakHtml( breakRecord.reason || "-" )} </td>

            `;


            table.appendChild( row );

        }
    );

}


/* ==========================================================
   CREATE / SCHEDULE BREAK
========================================================== */

async function createBarberBreak(
    event
) {

    event.preventDefault();


    const date =
        document.getElementById(
            "myBreakDate"
        )?.value;


    const startTime =
        document.getElementById(
            "myBreakStartTime"
        )?.value;


    const endTime =
        document.getElementById(
            "myBreakEndTime"
        )?.value;


    const type =
        document.getElementById(
            "myBreakStatusSelect"
        )?.value;


    const reason =
        document.getElementById(
            "myBreakReason"
        )?.value;


    if (
        !date ||
        !startTime ||
        !endTime ||
        !type
    ) {

        alert(
            "Please complete all required fields."
        );

        return;

    }


    if (
        endTime <= startTime
    ) {

        alert(
            "End time must be later than start time."
        );

        return;

    }


    const button =
        document.getElementById(
            "saveMyBreakBtn"
        );


    if (button) {

        button.disabled = true;

        button.innerHTML = `

            <i class="fa-solid fa-spinner fa-spin"></i>

            Saving...

        `;

    }


    try {

        await apiRequest( "/breaks-periods/break/create/", "POST",
            {
                date: date,

                start_time: startTime,

                end_time: endTime,

                type: type,

                reason: reason
            }
        );

        alert( "Break scheduled successfully." );

        document .getElementById( "myBreakForm" ) ?.reset();

        await window.loadBarberBreaks?.();


        /*
            Refresh the dashboard's break status
            and break history as well.
        */

        await window.loadBarberDashboard?.();

    }

    catch (error) {

        console.error( "Break creation error:", error );

        alert( "Unable to schedule break." );

    }

    finally {

        if (button) {

            button.disabled = false;

            button.innerHTML = `

                <i class="fa-solid fa-mug-hot"></i>

                Schedule Break

            `;

        }

    }

}


/* ==========================================================
   DASHBOARD BREAK HISTORY
========================================================== */

function renderDashboardBreaks( breaks, table ) {

    if (!table) {

        return;

    }


    table.innerHTML = "";


    if (!breaks.length) {

        table.innerHTML = `

            <tr>

                <td colspan="4"> No break records found. </td>

            </tr>

        `;

        return;

    }


    breaks.forEach(
        breakRecord => {

            const row = document.createElement( "tr" );


            const time = `${breakRecord.start_time || "-"} - ` + `${breakRecord.end_time || "-"}`;

            row.innerHTML = `

                <td> ${escapeBreakHtml( breakRecord.date || "-" )} </td>

                <td> ${escapeBreakHtml( time )} </td>

                <td> ${escapeBreakHtml( breakRecord.status || breakRecord.type || "-" )} </td>

                <td> ${escapeBreakHtml( breakRecord.reason || "-" )} </td>

            `;

            table.appendChild( row );

        }
    );

}


/* ==========================================================
   ERROR
========================================================== */

function renderBreakError() {

    const table = document.getElementById( "myBreakTable" );

    if (!table) {

        return;

    }


    table.innerHTML = `

        <tr>

            <td colspan="5"> Unable to load break records. </td>

        </tr>

    `;

}


/* ==========================================================
   HTML ESCAPE
========================================================== */

function escapeBreakHtml( value ) {

    if ( value === null || value === undefined ) {

        return "";

    }

    return String(value)

        .replaceAll( "&", "&amp;" )

        .replaceAll( "<", "&lt;" )

        .replaceAll( ">", "&gt;" )

        .replaceAll( '"', "&quot;" )

        .replaceAll( "'", "&#039;" );

}