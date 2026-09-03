
/* ==========================================================
   salon-manager-services.js
========================================================== */

/* ==========================================================
   SERVICE PAGINATION
========================================================== */

let serviceCurrentPage = 1;

const servicePageSize = 10;

let serviceTotalPages = 1;

let serviceTotalRecords = 0;

/* ==========================================================
   SERVICE MANAGEMENT
========================================================== */


let servicePageInitialized = false;


window.initServicePage = function () {

    if (servicePageInitialized) {

        return;

    }

    servicePageInitialized = true;

    /*===================================
        CREATE SEARCH BUTTON
    =====================================*/
    const searchButton = document.getElementById("searchServicesBtn");

    if(searchButton){

        searchButton.addEventListener("click", () => {

            serviceCurrentPage = 1;

            loadServices();

        });

    }

    const clearButton = document.getElementById("clearServiceFilters");

    if(clearButton){

        clearButton.addEventListener( "click", clearServiceFilters  );

    }

    /*===================================
        CREATE SERVICE BUTTON
    =====================================*/
    const createButton = document.getElementById("createServiceBtn");

    if (createButton) {

        createButton.addEventListener("click", () => {

            showServiceForm();

        });

    }

    /*===================================
        EDIT SELECTED BUTTON
    ====================================*/
    const editButton = document.getElementById("editServiceBtn");

    if (editButton) {

        editButton.addEventListener("click", () => {

            editSelectedService();

        });

    }

    /*===================================
        CREATE DELETE BUTTON
    =====================================*/
    const deleteButton = document.getElementById("deleteServiceBtn");

    if (deleteButton) {

        deleteButton.addEventListener("click", () => {

        deleteSelectedColors();

        });

    }

    const prevServiceButton = document.getElementById("prevServicePage");

    if (prevServiceButton) {

        prevServiceButton.addEventListener("click", () => {

            if (serviceCurrentPage > 1) {

                serviceCurrentPage--;

                loadServices();

            }

        });

    }


    const nextServiceButton = document.getElementById("nextServicePage");

    if (nextServiceButton) {

        nextServiceButton.addEventListener("click", () => {

            if (serviceCurrentPage < serviceTotalPages) {

                serviceCurrentPage++;

                loadServices();

            }

        });

    }

};


/*===================================
   clearServiceFilters
=====================================*/
window.clearServiceFilters = function(){

    document.getElementById(
        "serviceNameFilter"
    ).value = "";

    document.getElementById(
        "servicePriceFilter"
    ).value = "";

    document.getElementById(
        "serviceDurationFilter"
    ).value = "";

    document.getElementById(
        "serviceStatusFilter"
    ).value = "";


    serviceCurrentPage = 1;

    loadServices();

};


/*===================================
   showServiceForm
=====================================*/
function showServiceForm(service = null) {

    const container = document.getElementById("serviceFormContainer");

    if (!container) {

        console.error("serviceFormContainer not found.");

        return;

    }

    container.classList.remove("hidden");

    container.innerHTML = `

        <div class="section-divider">

            <span>Service Form</span>

        </div>

        <div class="card-header">

            <h2>${service ? "Edit Service" : "New Service"}</h2>

        </div>

        <form id="serviceForm" enctype="multipart/form-data">

            <div class="form-row">

                <div class="form-group service-name-group">
                    <label for="serviceName">Name</label>

                    <input type="text" id="serviceName" name="name"
                    value="${service?.name || ""}" required >
                </div>

                <div class="form-group service-price-group">
                    <label for="servicePrice">Price (₦)</label>

                    <input type="number" id="servicePrice" name="price"
                        min="0" step="0.01" value="${service?.price || ""}" required >
                </div>

                <div class="form-group service-duration-group">
                    <label for="serviceDuration">Duration (Minutes)</label>

                    <input type="number" id="serviceDuration" name="duration_minutes"
                        min="1" value="${service?.duration_minutes || ""}" required >
                </div>

            </div>

                <div class="form-group">

                    <label for="serviceImage"> Image </label>

                    <input type="file" id="serviceImage" name="image" accept="image/*">

                    ${
                        service?.image
                        ? `
                            <div class="preview">

                                <img src="${service.image}" width="120" alt="Service Image">

                            </div>
                        `
                        : ""
                    }

                </div>



                <div class="form-group">

                    <label for="serviceDescription"> Description </label>

                    <textarea id="serviceDescription" name="description"
                        rows="5">${service?.description || ""}
                    </textarea>

                </div>

                <div class="form-group">

                    <label>

                        <input type="checkbox" id="serviceActive" name="is_active"
                            ${service ? (service.is_active ? "checked" : "") : "checked"}>

                        Active

                    </label>

                </div>

                <div class="toolbar">

                    <button type="submit" class="gold-btn">

                        ${service ? "Update Service" : "Create Service"}

                    </button>

                    <button type="button" class="danger-btn"
                        onclick="document.getElementById('serviceForm').reset()">
                        Clear Form
                    </button>

                </div>

            </form>

    `;

    const form = document.getElementById("serviceForm");

    form.addEventListener("submit", async (event) => {

        event.preventDefault();

        const formData = new FormData();

        formData.append(
            "name",
            document.getElementById("serviceName").value
        );

        formData.append(
            "price",
            document.getElementById("servicePrice").value
        );

        formData.append(
            "duration_minutes",
            document.getElementById("serviceDuration").value
        );

        formData.append(
            "description",
            document.getElementById("serviceDescription").value
        );

        formData.append(
            "is_active",
            document.getElementById("serviceActive").checked
        );

        const image =
            document.getElementById("serviceImage").files[0];

        if (image) {

            formData.append("image", image);

        }

        try {

            if (service) {

                await apiRequest( `/services/${service.id}/`, "PATCH", formData );

                alert("Service updated.");

            }

            else {

                await apiRequest( "/services/", "POST", formData );

                alert("Service created.");

            }

            container.classList.add("hidden");

            loadServices();

        }

        catch (error) {

            console.error(error);

            alert("Unable to save service.");

        }

    });

    container.scrollIntoView({

        behavior: "smooth",

        block: "start"

    });

}

/*===================================
   editService
=====================================*/
window.editService = async function (id) {

    try {

        const service =
            await apiRequest(`/services/${id}/`);

        showServiceForm(service);

    }

    catch (error) {

        console.error(error);

        alert("Unable to load service.");

    }

}

/*===================================
   editSelectedService
=====================================*/
window.editSelectedService = function(){

    const selected=[
        ...document.querySelectorAll(
            ".service-checkbox:checked"
        )
    ];

    if(selected.length===0){

        alert("Select one service.");

        return;

    }

    if(selected.length>1){

        alert("Select only one service to edit.");

        return;

    }

    editService(selected[0].value);

};


/* ==========================================================
DELETE SELECTED SERVICES
========================================================== */

window.deleteSelectedServices = async function () {

    const selected = [ ...document.querySelectorAll( ".service-checkbox:checked" ) ];

    if (selected.length === 0) {

        alert("Select at least one service.");

        return;

    }

    if (!confirm( "Are you sure you want to delete the selected service(s)?" )) {
        return;
    }

    const ids = selected.map( service => Number(service.value) );

    try {

        await apiRequest( "/services/delete/", "DELETE", { ids: ids } );

        alert("Selected service(s) deleted successfully.");

        loadServices();

    }

    catch (error) {

        console.error(error);

        alert("Unable to delete service(s).");

    }

};


/*===================================
   loadServices
=====================================*/
window.loadServices = async function(){

    try {

        const serviceName =
            document.getElementById("serviceNameFilter")?.value || "";

        const servicePrice =
            document.getElementById("servicePriceFilter")?.value || "";

        const serviceDuration =
            document.getElementById("serviceDurationFilter")?.value || "";

        const serviceStatus =
            document.getElementById("serviceStatusFilter")?.value || "";


        const params = new URLSearchParams();


        /* ============================
           FILTERS
        ============================ */

        if(serviceName){

            params.append(
                "service_name",
                serviceName
            );

        }


        if(servicePrice){

            params.append(
                "service_price",
                servicePrice
            );

        }


        if(serviceDuration){

            params.append(
                "service_duration_minutes",
                serviceDuration
            );

        }


        if(serviceStatus){

            params.append(
                "service_is_active",
                serviceStatus
            );

        }


        /* ============================
           PAGINATION
        ============================ */

        params.append(
            "page",
            serviceCurrentPage
        );

        params.append(
            "page_size",
            servicePageSize
        );


        /* ============================
           API REQUEST
        ============================ */

        const response =
            await apiRequest(
                `/services/?${params.toString()}`
            );


        /* ============================
           DRF PAGINATION
        ============================ */

        const services =
            response.results || response;


        if(response.count !== undefined){

            serviceTotalRecords =
                response.count;

            serviceTotalPages =
                Math.ceil(
                    response.count /
                    servicePageSize
                );

        }

        else{

            serviceTotalRecords =
                services.length;

            serviceTotalPages =
                Math.max(
                    1,
                    Math.ceil(
                        services.length /
                        servicePageSize
                    )
                );

        }


        renderServices(services);

        updateServicePagination();


    }

    catch(error){

        console.error(error);

        alert("Unable to load services.");

    }

};


/* ==========================================================
   UPDATE SERVICE PAGINATION
========================================================== */

function updateServicePagination(){

    const pageNumber =
        document.getElementById(
            "servicePageNumber"
        );

    const paginationInfo =
        document.getElementById(
            "servicePaginationInfo"
        );

    const previousButton =
        document.getElementById(
            "prevServicePage"
        );

    const nextButton =
        document.getElementById(
            "nextServicePage"
        );


    /* ============================
       PAGE NUMBER
    ============================ */

    if(pageNumber){

        pageNumber.textContent =
            `Page ${serviceCurrentPage} of ${serviceTotalPages}`;

    }


    /* ============================
       SHOWING X–Y OF Z
    ============================ */

    if(paginationInfo){

        if(serviceTotalRecords === 0){

            paginationInfo.textContent =
                "Showing 0–0 of 0";

        }

        else{

            const start =
                ((serviceCurrentPage - 1) *
                servicePageSize) + 1;

            const end =
                Math.min(
                    serviceCurrentPage *
                    servicePageSize,
                    serviceTotalRecords
                );

            paginationInfo.textContent =
                `Showing ${start}–${end} of ${serviceTotalRecords}`;

        }

    }


    /* ============================
       PREVIOUS
    ============================ */

    if(previousButton){

        previousButton.disabled =
            serviceCurrentPage <= 1;

    }


    /* ============================
       NEXT
    ============================ */

    if(nextButton){

        nextButton.disabled =
            serviceCurrentPage >= serviceTotalPages;

    }

}


/* ==========================================================
   RENDER SERVICES
========================================================== */

window.renderServices = function (services) {

    const table = document.getElementById("serviceTable");

    if (!table) {

        return;
    }

    table.innerHTML = "";

    if (!services || services.length === 0) {

        table.innerHTML = `

            <tr> <td colspan="7"> No services found. </td> </tr>

        `;

        return;

    }

    services.forEach(service => {

        table.innerHTML += `

            <tr>

                <td> <input type="checkbox" class="service-checkbox" value="${service.id}"> </td>

                <td> ${ service.image ? `<img src="${service.image}" width="50">` : "-" } </td>

                <td>${service.name}</td>

                <td>₦${service.price}</td>

                <td>${service.duration_minutes} mins</td>

                <td> ${service.is_active ? "Active" : "Inactive"} </td>

            </tr>

        `;

    });

    initSelectAll( "selectAllServices", "service-checkbox" );

};


/*===================================
   initSelectAll
=====================================*/
function initSelectAll(selectAllId, checkboxClass) {

    const selectAll = document.getElementById(selectAllId);

    if (!selectAll) {

        return;

    }

    selectAll.onchange = () => {

        document
            .querySelectorAll(`.${checkboxClass}`)
            .forEach(box => {

                box.checked = selectAll.checked;

            });

    };

}