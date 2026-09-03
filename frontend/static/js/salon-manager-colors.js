/* ==========================================================
   salon-manager-colors.js
========================================================== */

/* ==========================================================
   COLOR MANAGEMENT
========================================================== */

let colorPageInitialized = false;

let colorCurrentPage = 1;
let colorTotalPages = 1;
let colorTotalCount = 0;


/* ==========================================================
   INITIALIZE COLOR PAGE
========================================================== */

window.initColorPage = function () {

    if (colorPageInitialized) {
        return;
    }

    colorPageInitialized = true;

    const searchButton = document.getElementById("searchColorsBtn");

    if (searchButton) {
        searchButton.addEventListener("click", function () {
            colorCurrentPage = 1;
            loadColors();
        });
    }


    const clearButton = document.getElementById("clearColorFiltersBtn");

    if (clearButton) {
        clearButton.addEventListener("click", clearColorFilters);
    }


    const createButton = document.getElementById("createColorBtn");

    if (createButton) {
        createButton.addEventListener("click", function () {
            showColorForm();
        });
    }


    const editButton = document.getElementById("editColorBtn");

    if (editButton) {
        editButton.addEventListener("click", function () {
            editSelectedColor();
        });
    }


    const deleteButton = document.getElementById("deleteColorBtn");

    if (deleteButton) {
        deleteButton.addEventListener("click", function () {
            deleteSelectedColors();
        });
    }


    const previousButton = document.getElementById("prevColorPage");

    if (previousButton) {
        previousButton.addEventListener("click", function () {

            if (colorCurrentPage > 1) {

                colorCurrentPage--;

                loadColors();
            }
        });
    }


    const nextButton = document.getElementById("nextColorPage");

    if (nextButton) {
        nextButton.addEventListener("click", function () {

            if (colorCurrentPage < colorTotalPages) {

                colorCurrentPage++;

                loadColors();
            }
        });
    }


    loadServicesForColorFilter();

    loadColors();

};


/* ==========================================================
   CLEAR FILTERS
========================================================== */

window.clearColorFilters = function () {

    const search = document.getElementById("colorNameFilter");
    const service = document.getElementById("colorServiceFilter");
    const price = document.getElementById("colorPriceFilter");
    const duration = document.getElementById("colorDurationFilter");
    const status = document.getElementById("colorStatusFilter");


    if (search) {
        search.value = "";
    }

    if (service) {
        service.value = "";
    }

    if (price) {
        price.value = "";
    }

    if (duration) {
        duration.value = "";
    }

    if (status) {
        status.value = "";
    }


    colorCurrentPage = 1;

    loadColors();

};


/* ==========================================================
   LOAD SERVICES INTO DROPDOWN
========================================================== */

async function loadServicesForColorFilter() {

    try {

        const response = await apiRequest(
            "/services/colors/only-service/"
        );

        const services = response.results || response;

        const select = document.getElementById(
            "colorServiceFilter"
        );

        if (!select) {
            return;
        }


        select.innerHTML = `
            <option value="">All Services</option>
        `;


        services.forEach(service => {

            select.innerHTML += `
                <option value="${service.id}">
                    ${service.name}
                </option>
            `;

        });

    }

    catch (error) {

        console.error(
            "Unable to load services for color filter:",
            error
        );

    }

}


/* ==========================================================
   SHOW COLOR FORM
========================================================== */

async function showColorForm(color = null) {

    const container = document.getElementById(
        "colorFormContainer"
    );

    if (!container) {
        return;
    }


    try {

        const serviceResponse = await apiRequest(
            "/services/colors/only-service/"
        );

        const services =
            serviceResponse.results || serviceResponse;


        container.classList.remove("hidden");


        container.innerHTML = `

            <div class="section-divider">

                <span>Color Form</span>

            </div>


            <div class="card-header">

                <h2>
                    ${color ? "Edit Color" : "New Color"}
                </h2>

            </div>


            <form id="colorForm">

                <div class="form-group">

                    <label>Service</label>

                    <select id="colorService" required>

                        <option value="">
                            Select Service
                        </option>

                        ${services.map(service => `

                            <option
                                value="${service.id}"
                                ${
                                    color &&
                                    String(color.service) ===
                                    String(service.id)
                                        ? "selected"
                                        : ""
                                }
                            >
                                ${service.name}
                            </option>

                        `).join("")}

                    </select>

                </div>


                <div class="form-row">

                    <div class="form-group service-name-group">

                        <label>Color Name</label>

                        <input
                            id="colorName"
                            type="text"
                            value="${color?.name || ""}"
                            required
                        >

                    </div>


                    <div class="form-group service-price-group">

                        <label>Price (₦)</label>

                        <input
                            id="colorPrice"
                            type="number"
                            min="0"
                            step="0.01"
                            value="${
                                color?.price !== undefined &&
                                color?.price !== null
                                    ? color.price
                                    : ""
                            }"
                            required
                        >

                    </div>


                    <div class="form-group service-duration-group">

                        <label>Duration</label>

                        <input
                            id="colorDuration"
                            type="number"
                            min="1"
                            value="${
                                color?.duration_minutes !== undefined &&
                                color?.duration_minutes !== null
                                    ? color.duration_minutes
                                    : ""
                            }"
                            required
                        >

                    </div>

                </div>


                <div class="form-group">

                    <label>Description</label>

                    <textarea
                        id="colorDescription"
                        rows="5"
                    >${color?.description || ""}</textarea>

                </div>


                <div class="form-group">

                    <label>

                        <input
                            id="colorActive"
                            type="checkbox"
                            ${
                                color
                                    ? (color.is_active ? "checked" : "")
                                    : "checked"
                            }
                        >

                        Active

                    </label>

                </div>


                <div class="toolbar">

                    <button
                        class="gold-btn"
                        type="submit"
                    >
                        ${
                            color
                                ? "Update Color"
                                : "Create Color"
                        }
                    </button>


                    <button
                        type="button"
                        class="danger-btn"
                        onclick="
                            document
                                .getElementById('colorForm')
                                .reset()
                        "
                    >
                        Clear Form
                    </button>

                </div>

            </form>

        `;


        const form = document.getElementById("colorForm");


        form.addEventListener(
            "submit",
            async function (event) {

                event.preventDefault();


                const data = {

                    service:
                        document.getElementById(
                            "colorService"
                        ).value,

                    name:
                        document.getElementById(
                            "colorName"
                        ).value.trim(),

                    price:
                        document.getElementById(
                            "colorPrice"
                        ).value,

                    duration_minutes:
                        document.getElementById(
                            "colorDuration"
                        ).value,

                    description:
                        document.getElementById(
                            "colorDescription"
                        ).value.trim(),

                    is_active:
                        document.getElementById(
                            "colorActive"
                        ).checked

                };


                try {

                    if (color) {

                        await apiRequest(
                            `/colors/${color.id}/`,
                            "PATCH",
                            data
                        );

                        alert("Color updated.");

                    }

                    else {

                        await apiRequest(
                            "/colors/",
                            "POST",
                            data
                        );

                        alert("Color created.");

                    }


                    container.classList.add("hidden");

                    colorCurrentPage = 1;

                    loadColors();

                }

                catch (error) {

                    console.error(error);

                    alert(
                        "Unable to save color."
                    );

                }

            }
        );


        container.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    }

    catch (error) {

        console.error(error);

        alert(
            "Unable to load color form."
        );

    }

}


/* ==========================================================
   EDIT COLOR
========================================================== */

window.editColor = async function (id) {

    try {

        const color = await apiRequest(
            `/colors/${id}/`
        );

        showColorForm(color);

    }

    catch (error) {

        console.error(error);

        alert(
            "Unable to load color."
        );

    }

};


/* ==========================================================
   EDIT SELECTED COLOR
========================================================== */

window.editSelectedColor = function () {

    const selected = [
        ...document.querySelectorAll(
            ".color-checkbox:checked"
        )
    ];


    if (selected.length === 0) {

        alert(
            "Select one color."
        );

        return;

    }


    if (selected.length > 1) {

        alert(
            "Select only one color to edit."
        );

        return;

    }


    editColor(
        selected[0].value
    );

};


/* ==========================================================
   DELETE SELECTED COLORS
========================================================== */

window.deleteSelectedColors = async function () {

    const selected = [
        ...document.querySelectorAll(
            ".color-checkbox:checked"
        )
    ];


    if (selected.length === 0) {

        alert(
            "Select at least one color."
        );

        return;

    }


    if (
        !confirm(
            "Are you sure you want to delete the selected color(s)?"
        )
    ) {

        return;

    }


    const ids = selected.map(
        color => Number(color.value)
    );


    try {

        await apiRequest(
            "/colors/delete/",
            "DELETE",
            {
                ids: ids
            }
        );


        alert(
            "Selected color(s) deleted successfully."
        );


        /*
         * If the last item on the current page was deleted,
         * move back one page when necessary.
         */
        if (
            selected.length ===
            document.querySelectorAll(
                ".color-checkbox"
            ).length &&
            colorCurrentPage > 1
        ) {

            colorCurrentPage--;

        }


        loadColors();

    }

    catch (error) {

        console.error(error);

        alert(
            "Unable to delete selected color(s)."
        );

    }

};


/* ==========================================================
   LOAD COLORS
========================================================== */

window.loadColors = async function () {

    try {

        const colorName =
            document.getElementById(
                "colorNameFilter"
            )?.value.trim() || "";


        const serviceId =
            document.getElementById(
                "colorServiceFilter"
            )?.value || "";


        const colorPrice =
            document.getElementById(
                "colorPriceFilter"
            )?.value || "";


        const colorDuration =
            document.getElementById(
                "colorDurationFilter"
            )?.value || "";


        const colorStatus =
            document.getElementById(
                "colorStatusFilter"
            )?.value || "";


        const params = new URLSearchParams();


        if (colorName) {

            params.append(
                "color_name",
                colorName
            );

        }


        if (serviceId) {

            params.append(
                "service_id",
                serviceId
            );

        }


        if (colorPrice) {

            params.append(
                "color_price",
                colorPrice
            );

        }


        if (colorDuration) {

            params.append(
                "color_duration_minutes",
                colorDuration
            );

        }


        if (colorStatus) {

            params.append(
                "color_is_active",
                colorStatus
            );

        }


        /*
         * Server-side pagination.
         */
        params.append(
            "page",
            colorCurrentPage
        );


        const queryString =
            params.toString();


        const response = await apiRequest(
            `/colors/?${queryString}`
        );


        /*
         * Django REST Framework pagination.
         *
         * Expected response:
         *
         * {
         *     count: 25,
         *     next: "...",
         *     previous: "...",
         *     results: [...]
         * }
         */


        const colors =
            response.results || response;


        colorTotalCount =
            response.count !== undefined
                ? response.count
                : colors.length;


        /*
         * If the backend gives next/previous URLs,
         * use those to determine whether another page exists.
         */
        if (
            response.results &&
            response.next !== undefined
        ) {

            const hasNextPage =
                Boolean(response.next);

            const hasPreviousPage =
                Boolean(response.previous);


            /*
             * We don't need the exact backend page count
             * to operate the buttons. However, calculate
             * the current total pages when count is available.
             */
            const pageSize =
                colors.length > 0
                    ? colors.length
                    : 1;


            colorTotalPages =
                Math.max(
                    1,
                    Math.ceil(
                        colorTotalCount /
                        pageSize
                    )
                );


            /*
             * Keep current page within valid bounds.
             */
            if (
                !hasPreviousPage &&
                colorCurrentPage > 1
            ) {

                colorCurrentPage = 1;

            }


            if (
                !hasNextPage &&
                colorCurrentPage > colorTotalPages
            ) {

                colorCurrentPage =
                    colorTotalPages;

            }

        }

        else {

            /*
             * Non-paginated fallback.
             */
            colorTotalPages = 1;

        }


        renderColors(colors);

        updateColorPagination(
            response,
            colors
        );

    }

    catch (error) {

        console.error(error);

        alert(
            "Unable to load colors."
        );

    }

};


/* ==========================================================
   RENDER COLORS
========================================================== */

window.renderColors = function (colors) {

    const table =
        document.getElementById(
            "colorTable"
        );


    if (!table) {

        return;

    }


    table.innerHTML = "";


    if (
        !colors ||
        colors.length === 0
    ) {

        table.innerHTML = `
            <tr>
                <td colspan="6">
                    No colors found.
                </td>
            </tr>
        `;

        initColorSelectAll();

        return;

    }


    colors.forEach(color => {

        table.innerHTML += `

            <tr>

                <td>
                    <input
                        type="checkbox"
                        class="color-checkbox"
                        value="${color.id}"
                    >
                </td>


                <td>
                    ${color.name || "-"}
                </td>


                <td>
                    ${
                        color.service_name ||
                        color.service?.name ||
                        "-"
                    }
                </td>


                <td>
                    ₦${color.price || 0}
                </td>


                <td>
                    ${color.duration_minutes || 0} mins
                </td>


                <td>
                    ${
                        color.is_active
                            ? "Active"
                            : "Inactive"
                    }
                </td>

            </tr>

        `;

    });


    initColorSelectAll();

};


/* ==========================================================
   UPDATE COLOR PAGINATION
========================================================== */

function updateColorPagination(
    response,
    colors
) {

    const info =
        document.getElementById(
            "colorPaginationInfo"
        );


    const pageNumber =
        document.getElementById(
            "colorPageNumber"
        );


    const previousButton =
        document.getElementById(
            "prevColorPage"
        );


    const nextButton =
        document.getElementById(
            "nextColorPage"
        );


    if (!info || !pageNumber) {

        return;

    }


    /*
     * Django REST Framework pagination.
     */
    if (
        response &&
        response.count !== undefined &&
        response.results
    ) {

        const pageSize =
            colors.length;


        if (pageSize > 0) {

            colorTotalPages =
                Math.ceil(
                    response.count /
                    pageSize
                );

        }
        else {

            colorTotalPages = 1;

        }


        const start =
            response.count === 0
                ? 0
                : (
                    (colorCurrentPage - 1) *
                    pageSize
                ) + 1;


        const end =
            Math.min(
                colorCurrentPage * pageSize,
                response.count
            );


        info.textContent =
            `Showing ${start}–${end} of ${response.count}`;


        pageNumber.textContent =
            `Page ${colorCurrentPage} of ${colorTotalPages}`;


        if (previousButton) {

            previousButton.disabled =
                !response.previous;

        }


        if (nextButton) {

            nextButton.disabled =
                !response.next;

        }


        return;

    }


    /*
     * Fallback when the API returns a plain array.
     */
    colorTotalCount =
        colors.length;


    colorTotalPages = 1;


    info.textContent =
        `Showing ${
            colors.length ? 1 : 0
        }–${colors.length} of ${colors.length}`;


    pageNumber.textContent =
        "Page 1";


    if (previousButton) {

        previousButton.disabled = true;

    }


    if (nextButton) {

        nextButton.disabled = true;

    }

}


/* ==========================================================
   SELECT ALL COLORS
========================================================== */

function initColorSelectAll() {

    const selectAll =
        document.getElementById(
            "selectAllColors"
        );


    if (!selectAll) {

        return;

    }


    /*
     * Reset select-all whenever a new page is rendered.
     */
    selectAll.checked = false;


    selectAll.onchange = function () {

        document
            .querySelectorAll(
                ".color-checkbox"
            )
            .forEach(box => {

                box.checked =
                    selectAll.checked;

            });

    };

}