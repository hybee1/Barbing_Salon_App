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

    // *********************===============

    const breakDetailsModal = document.getElementById( "breakDetailsModal" );


    if (breakDetailsModal) {

        breakDetailsModal.hidden = true;

        breakDetailsModal.classList.remove( "is-open" );

        breakDetailsModal.setAttribute( "aria-hidden", "true" );

    }


    const form = document.getElementById("myBreakForm");


    if (form) {

        form.addEventListener("submit", createBarberBreak);

    }


    /*
        Load break types from API.
    */

    loadBarberBreakTypes();


    /*
        Close break details modal.
    */

    const closeButton = document.getElementById("closeBreakDetailsModal");

    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeBreakDetailsModal
        );

    }


    /*
        Close modal when clicking outside the modal content.
    */

    const modal = document.getElementById("breakDetailsModal");

    if (modal) {

        modal.addEventListener(
            "click",
            function (event) {

                if (event.target === modal) {

                    closeBreakDetailsModal();

                }

            }
        );

    }


    /*
        Close modal with Escape.
    */

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                closeBreakDetailsModal();

            }

        }
    );

};


/* ==========================================================
   LOAD BREAK TYPES
========================================================== */

async function loadBarberBreakTypes() {

    const select =
        document.getElementById(
            "myBreakStatusSelect"
        );


    if (!select) {

        return;

    }


    /*
        Reset select and keep default option.
    */

    select.innerHTML = `
        <option value="">
            Select type
        </option>
    `;


    try {

        const data = await apiRequest("/break-periods/break/statuses/");


        /*
            API response:

            {
                "breaktype": [
                    "BREAK",
                    "OFF",
                    "PERSONAL"
                ]
            }
        */

        const types = Array.isArray(data?.breaktype) ? data.breaktype : [];


        if (!types.length) {

            return;

        }


        /*
            Populate select options.
        */

        types.forEach(
            breakType => {

                /*
                    The API returns strings:

                    "BREAK"
                    "OFF"
                    "PERSONAL"
                */

                if ( breakType === null || breakType === undefined || breakType === "" ) {

                    return;

                }


                const value = String(breakType);

                const label = formatBreakTypeLabel( breakType  );

                const option = document.createElement( "option" );

                option.value = value;

                option.textContent = label;

                select.appendChild( option );

            }
        );

    }

    catch (error) {

        console.error( "Unable to load break types:", error );

    }

}

/* ==========================================================
   FORMAT BREAK TYPE LABEL
========================================================== */

function formatBreakTypeLabel(value) {

    if (!value) {

        return "";

    }


    return String(value)
        .toLowerCase()
        .replace(
            /_/g,
            " "
        )
        .replace(
            /\b\w/g,
            char => char.toUpperCase()
        );

}


/* ==========================================================
   LOAD BREAKS
========================================================== */

window.loadBarberBreaks = async function () {

    try {

        const data = await apiRequest( "/break-periods/break/barber/"  );

        const breaks = Array.isArray(data) ? data : data?.results || [];

        renderBarberBreaks(breaks);


        /*
            Also keep the existing dashboard
            break history populated.
        */

        const dashboardTable =  document.getElementById("breakTable");


        if (dashboardTable) {

            renderDashboardBreaks( breaks, dashboardTable );

        }

    }

    catch (error) {

        console.error(
            "Unable to load barber breaks:",
            error
        );


        renderBreakError();

    }

};


/* ==========================================================
   RENDER BREAK RECORDS
========================================================== */

function renderBarberBreaks(breaks) {

    const table = document.getElementById("myBreakTable");

    if (!table) {

        return;

    }

    table.innerHTML = "";

    if (!breaks.length) {

        table.innerHTML = `

            <tr>

                <td colspan="5" class="break-empty-state">

                    No break records found.

                </td>

            </tr>

        `;

        return;

    }


    breaks.forEach(
        breakRecord => {

            const row = document.createElement("tr");


            /*
                Make the entire row selectable.
            */

            row.classList.add( "break-record-row" );

            row.tabIndex = 0;

            row.setAttribute( "role", "button"  );

            row.setAttribute( "aria-label", "View break record details"  );

            row.innerHTML = `

                <td> ${escapeBreakHtml( breakRecord.start_date || "-" )} </td>

                <td> ${escapeBreakHtml( breakRecord.end_date || "-" )} </td>

                <td> ${escapeBreakHtml( breakRecord.start_time || "-" )} </td>

                <td> ${escapeBreakHtml( breakRecord.end_time || "-" )} </td>

                <td>

                    <span class="break-status-badge">

                        ${escapeBreakHtml( breakRecord.status || breakRecord.type || "-" )}

                    </span>

                </td>

            `;


            /*
                Open details modal.
            */

            row.addEventListener(
                "click",
                function () {

                    openBreakDetailsModal( breakRecord );

                }
            );


            /*
                Keyboard accessibility.
            */

            row.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key === "Enter" ||
                        event.key === " "
                    ) {

                        event.preventDefault();

                        openBreakDetailsModal( breakRecord );

                    }

                }
            );


            table.appendChild(row);

        }
    );

}


/* ==========================================================
   CREATE / SCHEDULE BREAK
========================================================== */

async function createBarberBreak(event) {

    event.preventDefault();

    const startDate = document.getElementById( "myBreakStartDate" )?.value;

    const endDate =  document.getElementById( "myBreakEndDate" )?.value;

    const startTime = document.getElementById( "myBreakStartTime" )?.value;

    const endTime = document.getElementById( "myBreakEndTime"  )?.value;

    const type =  document.getElementById( "myBreakStatusSelect" )?.value;


    const reason = document.getElementById( "myBreakReason" )?.value;


    /*
        Validate required fields.
    */

    if ( !startDate || !endDate || !startTime || !endTime || !type ) {

        alert( "Please complete all required fields." );

        return;

    }


    /*
        Validate date range.
    */

    if (endDate < startDate) {

        alert( "End date must be the same as or later than start date." );

        return;

    }


    /*
        If the break starts and ends on the same day,
        make sure the end time is later.
    */

    if ( startDate === endDate && endTime <= startTime ) {

        alert( "End time must be later than start time." );

        return;

    }


    const button = document.getElementById( "saveMyBreakBtn" );


    if (button) {

        button.disabled = true;

        button.innerHTML = `

            <i class="fa-solid fa-spinner fa-spin"></i>

            Saving...

        `;

    }


    try {

        /*
            IMPORTANT:

            This now correctly sends:

            start_date
            end_date
            start_time
            end_time
            type
            reason
        */

        await apiRequest( "/break-periods/break/create/",
                            "POST",
                        {

                            start_date: startDate,

                            end_date: endDate,

                            start_time: startTime,

                            end_time: endTime,

                            status: type,

                            reason: reason

                        }
                    );


        alert( "Break scheduled successfully."  );

        document .getElementById("myBreakForm") ?.reset();


        /*
            Refresh break records.
        */

        await window.loadBarberBreaks?.();


        /*
            Refresh dashboard.
        */

        await window.loadBarberDashboard?.();

    }

    catch (error) {

        console.error( "Break creation error:", error );

        alert(
                error?.message ||
                error?.details ||
                error?.error?.details ||
                error?.error?.details?.[0] ||
                error?.detail ||
                error?.error?.detail ||
                error?.error?.detail?.[0] ||"Unable to schedule break." );

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
   BREAK DETAILS MODAL
========================================================== */

function openBreakDetailsModal(breakRecord) {

    const modal =
        document.getElementById(
            "breakDetailsModal"
        );


    if (!modal) {

        return;

    }


    /*
        Populate modal.
    */

    setBreakModalValue(
        "breakDetailStartDate",
        breakRecord.start_date || "-"
    );


    setBreakModalValue(
        "breakDetailEndDate",
        breakRecord.end_date || "-"
    );


    setBreakModalValue(
        "breakDetailStartTime",
        breakRecord.start_time || "-"
    );


    setBreakModalValue(
        "breakDetailEndTime",
        breakRecord.end_time || "-"
    );


    setBreakModalValue(
        "breakDetailType",
        breakRecord.type || "-"
    );


    setBreakModalValue(
        "breakDetailStatus",
        breakRecord.status ||
        breakRecord.type ||
        "-"
    );


    setBreakModalValue(
        "breakDetailReason",
        breakRecord.reason ||
        "No reason provided."
    );


    setBreakModalValue(
        "breakDetailCreatedAt",
        formatBreakDateTime(
            breakRecord.created_at
        )
    );


    setBreakModalValue(
        "breakDetailUpdatedAt",
        formatBreakDateTime(
            breakRecord.updated_at
        )
    );


    /*
        IMPORTANT:
        Remove the hidden attribute BEFORE
        showing the modal.
    */

    modal.hidden = false;


    modal.setAttribute(
        "aria-hidden",
        "false"
    );


    modal.classList.add(
        "is-open"
    );


    document.body.classList.add(
        "break-modal-open"
    );

}


/* ==========================================================
   SET MODAL VALUE
========================================================== */

function setBreakModalValue(
    elementId,
    value
) {

    const element =
        document.getElementById(elementId);


    if (!element) {

        return;

    }


    element.textContent =
        value === null ||
        value === undefined ||
        value === ""
            ? "-"
            : value;

}


/* ==========================================================
   CLOSE BREAK DETAILS MODAL
========================================================== */

function closeBreakDetailsModal() {

    const modal =
        document.getElementById(
            "breakDetailsModal"
        );


    if (!modal) {

        return;

    }


    /*
        Remove open state first.
    */

    modal.classList.remove(
        "is-open"
    );


    modal.setAttribute(
        "aria-hidden",
        "true"
    );


    document.body.classList.remove(
        "break-modal-open"
    );


    /*
        Completely hide the modal.
    */

    modal.hidden = true;

}


/* ==========================================================
   FORMAT DATETIME
========================================================== */

function formatBreakDateTime(value) {

    if (!value) {

        return "-";

    }


    const date =
        new Date(value);


    if (Number.isNaN(date.getTime())) {

        return value;

    }


    return date.toLocaleString();

}


/* ==========================================================
   DASHBOARD BREAK HISTORY
========================================================== */

function renderDashboardBreaks(
    breaks,
    table
) {

    if (!table) {

        return;

    }


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
        breakRecord => {

            const row =
                document.createElement("tr");


            const time =
                `${breakRecord.start_time || "-"} - ` +
                `${breakRecord.end_time || "-"}`;


            row.innerHTML = `

                <td>
                    ${escapeBreakHtml(
                        breakRecord.start_date ||
                        breakRecord.date ||
                        "-"
                    )}
                </td>

                <td>
                    ${escapeBreakHtml(
                        time
                    )}
                </td>

                <td>
                    ${escapeBreakHtml(
                        breakRecord.status ||
                        breakRecord.type ||
                        "-"
                    )}
                </td>

                <td>
                    ${escapeBreakHtml(
                        breakRecord.reason ||
                        "-"
                    )}
                </td>

            `;


            table.appendChild(row);

        }
    );

}


/* ==========================================================
   ERROR
========================================================== */

function renderBreakError() {

    const table =
        document.getElementById(
            "myBreakTable"
        );


    if (!table) {

        return;

    }


    table.innerHTML = `

        <tr>

            <td colspan="5">

                Unable to load break records.

            </td>

        </tr>

    `;

}


/* ==========================================================
   HTML ESCAPE
========================================================== */

function escapeBreakHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

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
