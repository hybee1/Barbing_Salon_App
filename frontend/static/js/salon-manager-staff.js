/* ==========================================================
   salon-manager-staff.js
========================================================== */

/* ==========================================================
   STAFF PAGINATION STATE
========================================================== */

let managerStaff = [];

let currentStaffPage = 1;

const STAFF_PER_PAGE = 10;


/* ==========================================================
   STAFF MANAGEMENT
   Levelz Cuts
========================================================== */

let staffPageInitialized = false;


/* ==========================================================
   INITIALIZE STAFF PAGE
========================================================== */

window.initStaffPage = function () {

    console.log("Staff page initialized");


    if (staffPageInitialized) {

        return;

    }

    staffPageInitialized = true;


    /* ======================================================
       LOAD STAFF OPTIONS
    ====================================================== */

    loadStaffOptions();


    /* ======================================================
       SEARCH
    ====================================================== */

    const searchButton = document.getElementById("searchStaffBtn");

    if (searchButton) {

        searchButton.addEventListener( "click", loadStaffs );

    }


    /* ======================================================
       CLEAR FILTERS
    ====================================================== */

    const clearButton = document.getElementById("clearStaffFilterBtn");


    if (clearButton) {

        clearButton.addEventListener( "click", clearStaffFilters );

    }


    /* ======================================================
       CREATE STAFF
    ====================================================== */

    const createButton = document.getElementById("createStaffBtn");

    if (createButton) {

        createButton.addEventListener(
            "click", () => {

                console.log("Create staff clicked");

                showStaffForm();

            }
        );

    }


    /* ======================================================
       EDIT SELECTED
    ====================================================== */

    const editButton = document.getElementById("editStaffBtn");

    if (editButton) {

        editButton.addEventListener( "click", editSelectedStaff );

    }


    /* ======================================================
       DELETE SELECTED
    ====================================================== */

    const deleteButton = document.getElementById("deleteStaffBtn");

    if (deleteButton) {

        deleteButton.addEventListener("click",deleteSelectedStaffs);

    }


    /* ======================================================
       PAGINATION BUTTONS
    ====================================================== */

    const previousButton = document.getElementById("prevStaffPage");

    const nextButton = document.getElementById("nextStaffPage");

    if (previousButton) {

        previousButton.addEventListener(  "click", previousStaffPage );

    }


    if (nextButton) {

        nextButton.addEventListener( "click", nextStaffPage );

    }


    /* ======================================================
       INITIAL LOAD
    ====================================================== */

    loadStaffs();

};


/* ==========================================================
   CLEAR STAFF FILTERS
========================================================== */

window.clearStaffFilters = function () {

    const name = document.getElementById("staffNameFilter");


    const department = document.getElementById("staffDepartmentFilter");


    const phone = document.getElementById("staffPhoneNumberFilter");


    const status = document.getElementById("staffStatusFilter");


    if (name) {

        name.value = "";

    }


    if (department) {

        department.value = "";

    }


    if (phone) {

        phone.value = "";

    }


    if (status) {

        status.value = "";

    }


    /* Reset pagination */

    currentStaffPage = 1;


    loadStaffs();

};


/* ==========================================================
   LOAD STAFF
========================================================== */

window.loadStaffs = async function () {

    const table = document.getElementById("staffTable");

    if (!table) {

        console.warn("staffTable was not found.");

        return;

    }


    try {

        const staffName = document.getElementById("staffNameFilter")?.value.trim() || "";

        const department = document .getElementById("staffDepartmentFilter") ?.value .trim() || "";

        const phoneNumber = document .getElementById("staffPhoneNumberFilter") ?.value .trim() || "";

        const status = document.getElementById("staffStatusFilter") ?.value || "";

        const params = new URLSearchParams();

        if (staffName) {

            params.append( "staff_name", staffName );

        }

        if (department) {

            params.append( "staff_department", department );

        }

        if (phoneNumber) {

            params.append( "staff_phone_number", phoneNumber );

        }

        if (status) {

            params.append( "staff_status", status );

        }

        const queryString = params.toString();

        const url = queryString ? `/staffs/admin/manage-staff/?${queryString}` :
                                                    `/staffs/admin/manage-staff`;

        console.log( "Loading staff:", url );

        const response = await apiRequest(url);

        /*
         * Store ALL staff.
         */

        managerStaff = Array.isArray(response) ? response : (response.results || []);


        console.log( "Staff response:",  managerStaff );

        /*
         * Always return to page 1
         * after a new search/load.
         */

        currentStaffPage = 1;

        /*
         * Render current page.
         */

        renderStaffManagement();

    }


    catch (error) {

        console.error( "Unable to load staff:", error );

    }

};


/* ==========================================================
   RENDER STAFF TABLE
========================================================== */

window.renderStaffManagement = function () {

    const table = document.getElementById("staffTable");


    if (!table) {

        return;

    }

    table.innerHTML = "";

    const totalStaff =  managerStaff.length;


    /* ======================================================
       NO STAFF
    ====================================================== */

    if (totalStaff === 0) {

        table.innerHTML = `

            <tr>

                <td colspan="6"> No staff found. </td>

            </tr>

        `;

        updateStaffPagination();

        return;

    }


    /* ======================================================
       PAGINATION CALCULATIONS
    ====================================================== */

    const startIndex = (currentStaffPage - 1) * STAFF_PER_PAGE;

    const endIndex = startIndex + STAFF_PER_PAGE;

    const staffForCurrentPage = managerStaff.slice( startIndex, endIndex );


    /* ======================================================
       RENDER CURRENT PAGE
    ====================================================== */

    staffForCurrentPage.forEach(
        member => {

            const user = member.user || {};

            const fullName =
                user.full_name || `${user.first_name || ""} ${user.last_name || ""}`.trim() ||
                "-";

            table.innerHTML += `

                <tr>

                    <td>

                        <input type="checkbox" class="staff-checkbox" value="${member.id}" >

                    </td>


                    <td> ${fullName} </td>


                    <td> ${member.department || "-"} </td>


                    <td> ${user.username || "-"} </td>


                    <td> ${ user.phone_number || user.phone_no || "-" } </td>


                    <td> ${member.status || "-"} </td>

                </tr>

            `;

        }
    );


    /* ======================================================
       SELECT ALL
    ====================================================== */

    initStaffSelectAll();


    /* ======================================================
       UPDATE PAGINATION
    ====================================================== */

    updateStaffPagination();

};


/* ==========================================================
   UPDATE STAFF PAGINATION UI
========================================================== */

function updateStaffPagination() {

    const info = document.getElementById(  "staffPaginationInfo" );

    const pageNumber = document.getElementById( "staffPageNumber" );

    const previousButton = document.getElementById( "prevStaffPage" );

    const nextButton = document.getElementById(  "nextStaffPage" );

    const totalStaff = managerStaff.length;

    const totalPages = Math.ceil( totalStaff / STAFF_PER_PAGE );


    /* ======================================================
       NO STAFF
    ====================================================== */

    if (totalStaff === 0) {

        if (info) {

            info.textContent = "Showing 0–0 of 0";

        }


        if (pageNumber) {

            pageNumber.textContent = "Page 1";

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

    const startIndex = (currentStaffPage - 1) * STAFF_PER_PAGE;


    const start = startIndex + 1;


    const end = Math.min( startIndex + STAFF_PER_PAGE, totalStaff );


    /* ======================================================
       PAGINATION TEXT
    ====================================================== */

    if (info) {

        info.textContent = `Showing ${start}–${end} of ${totalStaff}`;

    }

    if (pageNumber) {

        pageNumber.textContent = `Page ${currentStaffPage} of ${totalPages}`;

    }


    /* ======================================================
       BUTTON STATES
    ====================================================== */

    if (previousButton) {

        previousButton.disabled = currentStaffPage <= 1;

    }


    if (nextButton) {

        nextButton.disabled = currentStaffPage >= totalPages;

    }

}


/* ==========================================================
   PREVIOUS STAFF PAGE
========================================================== */

function previousStaffPage() {

    if (currentStaffPage <= 1) {

        return;

    }

    currentStaffPage--;

    renderStaffManagement();

    scrollToStaffTable();

}


/* ==========================================================
   NEXT STAFF PAGE
========================================================== */

function nextStaffPage() {

    const totalPages = Math.ceil( managerStaff.length / STAFF_PER_PAGE  );


    if (currentStaffPage >= totalPages) {

        return;

    }

    currentStaffPage++;

    renderStaffManagement();

    scrollToStaffTable();

}


/* ==========================================================
   SCROLL BACK TO STAFF TABLE
========================================================== */

function scrollToStaffTable() {

    const table = document.querySelector( "#staffPage .table-scroll" );

    if (!table) {

        return;

    }


    table.scrollIntoView({

        behavior: "smooth",

        block: "start"

    });

}


/* ==========================================================
   SELECT ALL STAFF
========================================================== */

function initStaffSelectAll() {

    const selectAll = document.getElementById( "selectAllStaffs" );

    if (!selectAll) {

        return;

    }

    selectAll.checked = false;

    selectAll.onchange = () => {

        document.querySelectorAll( ".staff-checkbox"  )
            .forEach(box => {

                box.checked = selectAll.checked;

            });

    };

}


/* ==========================================================
   GET SELECTED STAFF
========================================================== */

function getSelectedStaffIds() {

    return [ ...document.querySelectorAll( ".staff-checkbox:checked" ) ].map(
                                                        checkbox => Number(checkbox.value) );

}


/* ==========================================================
   SHOW STAFF FORM
========================================================== */

window.showStaffForm = async function (staff = null) {

    const container = document.getElementById( "staffFormContainer"  );


    if (!container) {

        console.error( "staffFormContainer not found." );

        return;

    }


    container.classList.remove("hidden");


    container.innerHTML = `

    <div class="section-divider">

        <span>Staff Form</span>

    </div>


    <div class="card-header">

        <h2> ${staff ? "Edit Staff" : "New Staff"} </h2>

    </div>


    <form id="staffForm" enctype="multipart/form-data">

        <div class="form-row">

            <div class="form-group staff-name-group">

                <label for="staffFirstName">  First Name </label>

                <input id="staffFirstName" type="text" value="${staff?.user?.first_name || ""}"
                    placeholder="John" required >

            </div>


            <div class="form-group staff-name-group">

                <label for="staffLastName"> Last Name </label>

                <input id="staffLastName" type="text" value="${staff?.user?.last_name || ""}"
                    placeholder="Doe" required >

            </div>

        </div>


        <div class="form-row">

            <div class="form-group staff-email-group">

                <label for="staffEmail"> Email </label>

                <input id="staffEmail" type="email" value="${staff?.user?.email || ""}"
                    placeholder="john@email.com" required >

            </div>


            <div class="form-group staff-phone-number-group">

                <label for="staffPhoneNumber"> Phone Number </label>

                <input id="staffPhoneNumber" type="tel"
                    maxlength="11" value="${ staff?.user?.phone_number ||
                    staff?.user?.phone_no || ""  }" placeholder="08012345678" required >

            </div>

        </div>


        <div class="form-row">

            <div class="form-group staff-username-group">

                <label for="staffUsername"> Username </label>

                <input id="staffUsername" type="text" value="${staff?.user?.username || ""}"
                    placeholder="username"
                    required >

            </div>

        </div>


        <div class="form-row">

            <div class="form-group staff-password-group">

                <label for="staffPassword"> Password </label>

                <input id="staffPassword" type="password" placeholder="password"
                    ${staff ? "" : "required"} >

            </div>


            <div class="form-group staff-password-group">

                <label for="staffConfirmPassword"> Confirm Password </label>

                <input id="staffConfirmPassword" type="password" placeholder="confirm password"
                    ${staff ? "" : "required"}  >

            </div>

        </div>


        <div class="form-row">

            <div class="form-group staff-department-group">

                <label for="staffDepartment"> Department </label>

                <select id="staffDepartment" required >

                    <option value=""> Select Department </option>

                </select>

            </div>


            <div class="form-group staff-position-group">

                <label for="staffPosition"> Position </label>

                <select id="staffPosition" required >

                    <option value=""> Select Position </option>

                </select>

            </div>

        </div>


        <div class="form-row">

            <div class="form-group staff-employment-date-group">

                <label> Employment Date </label>

                <input type="date" id="staffEmploymentDate"
                    value="${staff?.employment_date || ""}" >

            </div>

            <div class="form-group staff-status-group">

                <label for="staffStatus"> Status </label>

                <select id="staffStatus" required >

                    <option value=""> Select Status </option>

                </select>

            </div>

        </div>


        <div class="toolbar">

            <button class="gold-btn" type="submit" >

                ${ staff ? "Update Staff" : "Create Staff" }

            </button>


            <button type="button" class="danger-btn" id="cancelStaffFormBtn" >

                Cancel

            </button>

        </div>


    </form>

`;


    /* ======================================================
       LOAD FORM OPTIONS
    ====================================================== */

    await loadStaffOptions();


    /* ======================================================
       SET EDIT VALUES
    ====================================================== */

    if (staff) {

        const departmentSelect = document.getElementById(  "staffDepartment" );

        const positionSelect = document.getElementById( "staffPosition" );

        const statusSelect = document.getElementById( "staffStatus"  );

        if (departmentSelect) {

            departmentSelect.value = staff.department?.value ?? staff.department ?? "";

        }


        if (positionSelect) {

            positionSelect.value = staff.position?.value ?? staff.position ?? "";

        }


        if (statusSelect) {

            statusSelect.value = staff.status?.value ?? staff.status ?? "";

        }

    }


    /* ======================================================
       CANCEL
    ====================================================== */

    document .getElementById("cancelStaffFormBtn") ?.addEventListener( "click", () => {
                container.classList.add(  "hidden" );
            }
        );


    /* ======================================================
       SUBMIT
    ====================================================== */

    const form = document.getElementById( "staffForm" );

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            const formData = new FormData();

            formData.append(
                "first_name", document.getElementById("staffFirstName").value.trim()
            );


            formData.append(
                "last_name", document.getElementById("staffLastName" ).value.trim()
            );


            const password = document.getElementById("staffPassword").value.trim();


            const password2 = document.getElementById( "staffConfirmPassword" ) .value .trim();


            /*
             * Only send password fields when
             * they were actually entered.
             */

            if (password) {

                formData.append( "password", password );

                formData.append( "password2", password2  );

            }


            formData.append(
                "phone_number", document.getElementById("staffPhoneNumber").value.trim() );


            formData.append(
                "email", document.getElementById( "staffEmail").value.trim()
            );


            formData.append(
                "username", document.getElementById("staffUsername").value.trim()
            );


            formData.append( "department", document.getElementById( "staffDepartment" ).value );

            formData.append( "position", document.getElementById("staffPosition" ).value );


            formData.append("status", document .getElementById( "staffStatus" ).value );


            formData.append( "employment_date",
                document.getElementById( "staffEmploymentDate").value
            );


            const image = document.getElementById("staffImage") ?.files?.[0];


            if (image) {

                formData.append( "image", image );

            }


            try {

                if (staff) {

                    await apiRequest( `/staffs/admin/manage-staff/${staff.id}/`, "PATCH", formData );

                    alert( "Staff updated successfully." );

                }

                else {

                    await apiRequest( "/staffs/admin/manage-staff/", "POST", formData );

                    alert( "Staff created successfully." );

                }


                container.classList.add( "hidden" );


                /*
                 * Reload staff.
                 * This resets pagination to page 1.
                 */

                await loadStaffs();

            }

            catch (error) {

                console.error(  "Unable to save staff:", error  );

                alert( "Unable to save staff." );

            }

        }
    );


    container.scrollIntoView({ behavior: "smooth", block: "start" });

};


/* ==========================================================
   EDIT ONE STAFF
========================================================== */

window.editStaff = async function (id) {

    try {

        const staff = await apiRequest( `/staffs/admin/manage-staff/${id}/` );

        console.log( "Editing staff:", staff );


        showStaffForm(staff);

    }


    catch (error) {

        console.error( "Unable to load staff:", error );


        alert( "Unable to load staff." );

    }

};


/* ==========================================================
   EDIT SELECTED STAFF
========================================================== */

window.editSelectedStaff = async function () {

    const selected = getSelectedStaffIds();

    if (selected.length === 0) {

        alert( "Select one staff member." );

        return;

    }


    if (selected.length > 1) {

        alert( "Select only one staff member to edit." );

        return;

    }


    await editStaff( selected[0] );

};


/* ==========================================================
   DELETE SELECTED STAFF
========================================================== */

window.deleteSelectedStaffs = async function () {

    const selected = getSelectedStaffIds();

    if (selected.length === 0) {

        alert( "Select at least one staff member." );

        return;

    }


    const confirmed =
        confirm( `Are you sure you want to delete ${selected.length} staff member(s)?` );


    if (!confirmed) {

        return;

    }


    try {

        await apiRequest( "/staffs/admin/manage-staff/delete/", "DELETE", { ids: selected } );

        alert( "Selected staff member(s) deleted successfully." );

        await loadStaffs();

        const selectAll = document.getElementById( "selectAllStaffs" );


        if (selectAll) {

            selectAll.checked = false;

        }

    }


    catch (error) {

        console.error( "Unable to delete staff:", error );

        alert( "Unable to delete staff member(s)." );

    }

};


/* ==========================================================
   LOAD STAFF OPTIONS
========================================================== */

async function loadStaffOptions() {

    try {

        const response = await apiRequest( "/staffs/options/" );

        const departments = response.staff_departments || [];

        const statuses = response.staff_statuses || [];

        const positions = response.staff_positions || [];

        populateStaffSelect( "staffDepartmentFilter", "All Departments", departments );

        populateStaffSelect( "staffStatusFilter", "All Statuses", statuses );

        populateStaffSelect( "staffDepartment", "Select Department", departments );

        populateStaffSelect( "staffPosition", "Select Position", positions );

        populateStaffSelect( "staffStatus", "Select Status", statuses );

    }


    catch (error) {

        console.error( "Unable to load staff options:", error );

    }

}


/* ==========================================================
   POPULATE STAFF SELECT
========================================================== */

function populateStaffSelect( elementId, placeholder, options ) {

    const select = document.getElementById( elementId );


    if (!select) {

        return;

    }


    select.innerHTML = `

        <option value=""> ${placeholder} </option>

    `;


    options.forEach(option => {

        select.innerHTML += `

            <option value="${option.value}"> ${option.label} </option>

        `;

    });

}
