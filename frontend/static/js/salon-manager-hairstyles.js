/* ==========================================================
   salon-manager-hairstyle.js
========================================================== */

/* ==========================================================
   HAIRSTYLE PAGINATION STATE
========================================================== */

let managerHairstyles = [];

let currentHairstylePage = 1;

const HAIRSTYLES_PER_PAGE = 10;

/* ==========================================================
   HAIRSTYLE MANAGEMENT
========================================================== */

let hairstylePageInitialized = false;

window.initHairstylePage = function () {

    console.log("Hairstyle page initialized");

    if (hairstylePageInitialized) {
        return;
    }

    hairstylePageInitialized = true;


    const searchButton =
        document.getElementById("searchHairstylesBtn");

    if (searchButton) {

        searchButton.addEventListener(
            "click",
            loadHairstyles
        );

    }


    const clearButton =
        document.getElementById("clearHairstyleFiltersBtn");

    if (clearButton) {

        clearButton.addEventListener(
            "click",
            clearHairstyleFilters
        );

    }


    const createButton =
        document.getElementById("createHairstyleBtn");

    if (createButton) {

        createButton.addEventListener(
            "click",
            () => {
                showHairstyleForm();
            }
        );

    }


    const editButton =
        document.getElementById("editHairstyleBtn");

    if (editButton) {

        editButton.addEventListener(
            "click",
            editSelectedHairstyle
        );

    }


    const deleteButton =
        document.getElementById("deleteHairstyleBtn");

    if (deleteButton) {

        deleteButton.addEventListener(
            "click",
            deleteSelectedHairstyles
        );

    }


    /* ======================================================
       PAGINATION BUTTONS
    ====================================================== */

    const previousButton =
        document.getElementById("prevHairstylePage");

    const nextButton =
        document.getElementById("nextHairstylePage");


    if (previousButton) {

        previousButton.addEventListener(
            "click",
            previousHairstylePage
        );

    }


    if (nextButton) {

        nextButton.addEventListener(
            "click",
            nextHairstylePage
        );

    }


    loadServicesForHairstyleFilter();

};



/* ==========================================================
   CLEAR FILTERS
========================================================== */

window.clearHairstyleFilters = function () {

    document.getElementById(
        "hairstyleNameFilter"
    ).value = "";


    document.getElementById(
        "hairstyleServiceFilter"
    ).value = "";


    document.getElementById(
        "hairstylePriceFilter"
    ).value = "";


    document.getElementById(
        "hairstyleDurationFilter"
    ).value = "";


    document.getElementById(
        "hairstyleStatusFilter"
    ).value = "";


    currentHairstylePage = 1;


    loadHairstyles();

};



/* ==========================================================
   LOAD SERVICES INTO FILTER
========================================================== */

async function loadServicesForHairstyleFilter() {

    try {

        const response = await apiRequest("/services/hairstyles/only-service/");

        const services = response.results || response;

        const select = document.getElementById( "hairstyleServiceFilter" );

        if (!select) {
            return;
        }

        select.innerHTML =
            `<option value="">All Services</option>`;

        services.forEach(service => {

            select.innerHTML += `

                <option value="${service.id}">
                    ${service.name}
                </option>

            `;

        });

    }

    catch (error) {

        console.error(error);

    }

}



/* ==========================================================
   SHOW FORM
========================================================== */

async function showHairstyleForm( hairstyle = null ) {

    const container = document.getElementById( "hairstyleFormContainer" );

    console.log(container);

    if (!container) {
        return;
    }

    const serviceResponse = await apiRequest("/services/hairstyles/only-service/");

    const services = serviceResponse.results || serviceResponse;

    container.classList.remove("hidden");

    container.innerHTML = `

        <div class="section-divider">

            <span>Hairstyle Form</span>

        </div>

        <div class="card-header">

            <h2> ${ hairstyle ? "Edit Hairstyle" : "New Hairstyle" }  </h2>

        </div>

        <form id="hairstyleForm" enctype="multipart/form-data" >

            <div class="form-group">

                <label> Service </label>

                <select id="hairstyleService" required >

                    <option value=""> Select Service </option>

                    ${services.map(service => `

                        <option value="${service.id}"
                            ${ hairstyle && hairstyle.service == service.id ? "selected" : "" } >

                            ${service.name}

                        </option>

                    `).join("")}

                </select>

            </div>

            <div class="form-row">

                <div class="form-group service-name-group" >

                    <label> Hairstyle Name </label>

                    <input id="hairstyleName" type="text"
                        value="${ hairstyle?.name || "" }" required >

                </div>

                <div class="form-group service-price-group" >

                    <label> Price (₦) </label>

                    <input id="hairstylePrice" type="number" min="0"
                        step="0.01" value="${ hairstyle?.price || "" }" required >

                </div>

                <div class="form-group service-duration-group"  >

                    <label> Duration </label>

                    <input id="hairstyleDuration" type="number" min="1"
                        value="${ hairstyle?.duration_minutes || "" }"  required >

                </div>

            </div>

            <div class="form-group">

                <label> Image </label>

                <input id="hairstyleImage" type="file" accept="image/*" >

                ${ hairstyle?.image ? `

                        <div class="preview">

                            <img src="${hairstyle.image}" width="120" >

                        </div>
                    `
                    : ""
                }

            </div>

            <div class="form-group">

                <label> Description </label>

                <textarea id="hairstyleDescription" rows="5" >
                ${ hairstyle?.description || "" }
                </textarea>

            </div>

            <div class="form-group">

                <label>

                    <input id="hairstyleActive" type="checkbox"
                        ${ hairstyle ? ( hairstyle.is_active ? "checked" : "" ) : "checked" } >

                    Active

                </label>

            </div>

            <div class="toolbar">

                <button class="gold-btn" type="submit" >

                    ${ hairstyle ? "Update Hairstyle" : "Create Hairstyle" }

                </button>

                <button type="button" class="danger-btn"
                    onclick="document.getElementById('hairstyleForm').reset()" >

                    Clear Form

                </button>

            </div>

        </form>

    `;

        const form = document.getElementById("hairstyleForm");

        form.addEventListener(
            "submit", async (event) => {

                event.preventDefault();

                const formData = new FormData();

                formData.append( "service",  document.getElementById( "hairstyleService" ).value
            );

            formData.append( "name", document.getElementById( "hairstyleName" ).value  );

            formData.append( "price", document.getElementById( "hairstylePrice" ).value );

            formData.append( "duration_minutes",
                document.getElementById( "hairstyleDuration" ).value );

            formData.append( "description", document.getElementById( "hairstyleDescription"
                ).value );

            formData.append( "is_active", document.getElementById( "hairstyleActive" ).checked );

            const image = document.getElementById( "hairstyleImage" ).files[0];

            if (image) {

                formData.append( "image", image );

            }

            try {

                if (hairstyle) {

                    await apiRequest( `/hairstyles/${hairstyle.id}/`, "PATCH", formData );

                    alert( "Hairstyle updated." );

                }

                else {

                    await apiRequest( "/hairstyles/", "POST", formData );

                    alert( "Hairstyle created."  );

                }

                container.classList.add( "hidden" );

                loadHairstyles();

            }

            catch (error) {

                console.error(error);

                alert( "Unable to save hairstyle." );

            }

        }

    );

        container.scrollIntoView({ behavior: "smooth", block: "start"  });

}



/* ==========================================================
   EDIT HAIRSTYLE
========================================================== */

window.editHairstyle = async function (id) {

    try {

        const hairstyle = await apiRequest(  `/hairstyles/${id}/` );

        showHairstyleForm( hairstyle );

    }

    catch (error) {

        console.error(error);

        alert( "Unable to load hairstyle." );

    }

};



/* ==========================================================
   EDIT SELECTED
========================================================== */

window.editSelectedHairstyle = function () {

    const selected = [

        ...document.querySelectorAll( ".hairstyle-checkbox:checked"  )

    ];

    if ( selected.length === 0 ) {

        alert( "Select one hairstyle."  );

        return;

    }

    if ( selected.length > 1 ) {

        alert( "Select only one hairstyle."  );

        return;
    }

    editHairstyle( selected[0].value );

};


/* ==========================================================
DELETE SELECTED HAIRSTYLES
========================================================== */

window.deleteSelectedHairstyles = async function () {

    const selected = [ ...document.querySelectorAll( ".hairstyle-checkbox:checked" ) ];

    if (selected.length === 0) {

        alert("Select at least one hairstyle.");
        return;
    }

    if (!confirm( "Are you sure you want to delete the selected hairstyle(s)?" )) {
        return;
    }

    const ids = selected.map( hairstyle => Number(hairstyle.value) );

    try {

        await apiRequest( "/hairstyles/delete/", "DELETE", { ids: ids }
        );

        alert("Selected hairstyle(s) deleted successfully.");

        loadHairstyles();

    }

    catch (error) {

        console.error(error);

        alert("Unable to delete hairstyle(s).");

    }

};



/* ==========================================================
   LOAD HAIRSTYLES
========================================================== */

window.loadHairstyles = async function () {

    try {

        const hairstyle_name =
            document.getElementById(
                "hairstyleNameFilter"
            )?.value || "";


        const service_id =
            document.getElementById(
                "hairstyleServiceFilter"
            )?.value || "";


        const hairstyle_price =
            document.getElementById(
                "hairstylePriceFilter"
            )?.value || "";


        const hairstyle_duration =
            document.getElementById(
                "hairstyleDurationFilter"
            )?.value || "";


        const hairstyle_status =
            document.getElementById(
                "hairstyleStatusFilter"
            )?.value || "";


        const params = new URLSearchParams();


        if (hairstyle_name) {

            params.append(
                "hairstyle_name",
                hairstyle_name
            );

        }


        if (service_id) {

            params.append(
                "service_id",
                service_id
            );

        }


        if (hairstyle_price) {

            params.append(
                "hairstyle_price",
                hairstyle_price
            );

        }


        if (hairstyle_duration) {

            params.append(
                "hairstyle_duration_minutes",
                hairstyle_duration
            );

        }


        if (hairstyle_status) {

            params.append(
                "hairstyle_is_active",
                hairstyle_status
            );

        }


        const response = await apiRequest(
            `/hairstyles/?${params.toString()}`
        );


        /* ==================================================
           STORE ALL HAIRSTYLES
        ================================================== */

        managerHairstyles =
            Array.isArray(response)
                ? response
                : (response.results || []);


        /* ==================================================
           RESET PAGINATION
        ================================================== */

        currentHairstylePage = 1;


        /* ==================================================
           RENDER FIRST PAGE
        ================================================== */

        renderHairstyles();


    }
    catch (error) {

        console.error(error);

        alert("Unable to load hairstyles.");

    }

};



/* ==========================================================
   RENDER
========================================================== */

window.renderHairstyles = function () {

    const table =
        document.getElementById("hairstyleTable");


    if (!table) {
        return;
    }


    table.innerHTML = "";


    const totalHairstyles =
        managerHairstyles.length;


    /* ======================================================
       NO HAIRSTYLES
    ====================================================== */

    if (totalHairstyles === 0) {

        table.innerHTML = `

            <tr>

                <td colspan="7">
                    No hairstyles found.
                </td>

            </tr>

        `;


        updateHairstylePagination();

        return;

    }


    /* ======================================================
       PAGINATION CALCULATIONS
    ====================================================== */

    const startIndex =
        (currentHairstylePage - 1)
        * HAIRSTYLES_PER_PAGE;


    const endIndex =
        startIndex + HAIRSTYLES_PER_PAGE;


    const hairstylesForCurrentPage =
        managerHairstyles.slice(
            startIndex,
            endIndex
        );


    /* ======================================================
       RENDER CURRENT PAGE
    ====================================================== */

    hairstylesForCurrentPage.forEach(
        hairstyle => {

            table.innerHTML += `

                <tr>

                    <td>

                        <input
                            type="checkbox"
                            class="hairstyle-checkbox"
                            value="${hairstyle.id}"
                        >

                    </td>


                    <td>
                        ${hairstyle.name}
                    </td>


                    <td>

                        ${
                            hairstyle.image

                            ? `
                                <img
                                    src="${hairstyle.image}"
                                    width="50"
                                >
                              `

                            : "-"
                        }

                    </td>


                    <td>
                        ${
                            hairstyle.service_name
                            ||
                            hairstyle.service?.name
                            ||
                            "-"
                        }
                    </td>


                    <td>
                        ₦${hairstyle.price}
                    </td>


                    <td>
                        ${hairstyle.duration_minutes} mins
                    </td>


                    <td>
                        ${
                            hairstyle.is_active
                            ? "Active"
                            : "Inactive"
                        }
                    </td>

                </tr>

            `;

        }
    );


    /* ======================================================
       SELECT ALL
    ====================================================== */

    initSelectAll(
        "selectAllHairstyles",
        "hairstyle-checkbox"
    );


    /* ======================================================
       UPDATE PAGINATION
    ====================================================== */

    updateHairstylePagination();

};



/* ==========================================================
   UPDATE HAIRSTYLE PAGINATION UI
========================================================== */

function updateHairstylePagination() {

    const info =
        document.getElementById(
            "hairstylePaginationInfo"
        );


    const pageNumber =
        document.getElementById(
            "hairstylePageNumber"
        );


    const previousButton =
        document.getElementById(
            "prevHairstylePage"
        );


    const nextButton =
        document.getElementById(
            "nextHairstylePage"
        );


    const totalHairstyles =
        managerHairstyles.length;


    const totalPages =
        Math.ceil(
            totalHairstyles /
            HAIRSTYLES_PER_PAGE
        );


    /* ======================================================
       NO HAIRSTYLES
    ====================================================== */

    if (totalHairstyles === 0) {

        if (info) {

            info.textContent =
                "Showing 0–0 of 0";

        }


        if (pageNumber) {

            pageNumber.textContent =
                "Page 1";

        }


        if (previousButton) {

            previousButton.disabled = true;

        }


        if (nextButton) {

            nextButton.disabled = true;

        }


        return;

    }


    /* ======================================================
       CURRENT RANGE
    ====================================================== */

    const startIndex =
        (currentHairstylePage - 1)
        * HAIRSTYLES_PER_PAGE;


    const start =
        startIndex + 1;


    const end =
        Math.min(
            startIndex + HAIRSTYLES_PER_PAGE,
            totalHairstyles
        );


    /* ======================================================
       PAGINATION TEXT
    ====================================================== */

    if (info) {

        info.textContent =
            `Showing ${start}–${end} of ${totalHairstyles}`;

    }


    if (pageNumber) {

        pageNumber.textContent =
            `Page ${currentHairstylePage} of ${totalPages}`;

    }


    /* ======================================================
       BUTTON STATES
    ====================================================== */

    if (previousButton) {

        previousButton.disabled =
            currentHairstylePage <= 1;

    }


    if (nextButton) {

        nextButton.disabled =
            currentHairstylePage >= totalPages;

    }

}

/* ==========================================================
   PREVIOUS HAIRSTYLE PAGE
========================================================== */

function previousHairstylePage() {

    if (currentHairstylePage <= 1) {
        return;
    }


    currentHairstylePage--;


    renderHairstyles();


    scrollToHairstyleTable();

}


/* ==========================================================
   NEXT HAIRSTYLE PAGE
========================================================== */

function nextHairstylePage() {

    const totalPages =
        Math.ceil(
            managerHairstyles.length /
            HAIRSTYLES_PER_PAGE
        );


    if (currentHairstylePage >= totalPages) {
        return;
    }


    currentHairstylePage++;


    renderHairstyles();


    scrollToHairstyleTable();

}


/* ==========================================================
   SCROLL BACK TO TABLE
========================================================== */

function scrollToHairstyleTable() {

    const table =
        document.querySelector(
            "#hairstylesPage .table-scroll"
        );


    if (!table) {
        return;
    }


    table.scrollIntoView({

        behavior: "smooth",

        block: "start"

    });

}


/* ==========================================================
   SELECT ALL
========================================================== */

function initSelectAll( selectAllId, checkboxClass ) {

    const selectAll = document.getElementById( selectAllId );

    if (!selectAll) {

        return;

    }

    selectAll.onchange = () => {

        document

            .querySelectorAll( `.${checkboxClass}` )

            .forEach(box => {

                box.checked = selectAll.checked;

            });

    };

}

