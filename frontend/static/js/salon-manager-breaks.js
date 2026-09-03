/* ==========================================================
   salon-manager-breaks.js
========================================================== */


/* ==========================================================
   BREAK MANAGEMENT
   Levelz Cuts
========================================================== */


/* ==========================================================
   BREAK PAGE STATE
========================================================== */

let breakPageInitialized = false;

let breakCurrentPage = 1;

const breakPageSize = 10;

let breakTotalPages = 1;

let breakAllData = [];


/* ==========================================================
   INITIALIZE BREAK PAGE
========================================================== */

window.initBreakPage = function(){

    /*
       Do not mark the page as initialized until
       the required DOM elements actually exist.
    */

    if(breakPageInitialized){
        return;
    }


    const table = document.getElementById("breakTable");

    if(!table){
        return;
    }


    breakPageInitialized = true;


    const previousButton =
        document.getElementById("prevBreakPage");

    const nextButton =
        document.getElementById("nextBreakPage");


    if(previousButton){

        previousButton.addEventListener(
            "click",
            previousBreakPage
        );

    }


    if(nextButton){

        nextButton.addEventListener(
            "click",
            nextBreakPage
        );

    }

};


/* ==========================================================
   LOAD BREAKS
========================================================== */

window.loadBreakManagement = async function(){

    const table =
        document.getElementById("breakTable");


    if(!table){
        return;
    }


    try{

        const breaks = await apiRequest( "/break-periods/" );


        /*
           Support both normal arrays and
           DRF paginated responses.
        */

        breakAllData =
            Array.isArray(breaks)
                ? breaks
                : (breaks.results || []);


        breakCurrentPage = 1;


        renderBreakManagement(
            breakAllData
        );

    }

    catch(error){

        console.error(
            "Unable to load breaks:",
            error
        );


        table.innerHTML = `
            <tr>
                <td colspan="5">
                    Unable to load breaks.
                </td>
            </tr>
        `;


        updateBreakPagination(0);

    }

};


/* ==========================================================
   RENDER BREAKS
========================================================== */

function renderBreakManagement(breaks){

    const table =
        document.getElementById("breakTable");


    if(!table){
        return;
    }


    table.innerHTML = "";


    if(!breaks || breaks.length === 0){

        table.innerHTML = `

            <tr>

                <td colspan="5">
                    No breaks found.
                </td>

            </tr>

        `;


        updateBreakPagination(0);

        return;

    }


    breakTotalPages =
        Math.ceil(
            breaks.length / breakPageSize
        );


    if(
        breakCurrentPage >
        breakTotalPages
    ){

        breakCurrentPage =
            breakTotalPages;

    }


    const startIndex =
        (breakCurrentPage - 1)
        * breakPageSize;


    const endIndex =
        startIndex + breakPageSize;


    const pageItems =
        breaks.slice(
            startIndex,
            endIndex
        );


    pageItems.forEach(item => {

        table.innerHTML += `

            <tr>

                <td>
                    ${item.staff_name || "-"}
                </td>

                <td>
                    ${item.status || "On Break"}
                </td>

                <td>
                    ${item.start_time || "-"}
                </td>

                <td>
                    ${item.end_time || "-"}
                </td>

                <td>

                    ${
                        item.end_time

                        ?

                        "-"

                        :

                        `
                        <button
                            type="button"
                            class="gold-btn end-break-btn"
                            onclick="endBreak(${item.id})"
                        >
                            End Break
                        </button>
                        `
                    }

                </td>

            </tr>

        `;

    });


    updateBreakPagination(
        breaks.length
    );

}


/* ==========================================================
   UPDATE PAGINATION UI
========================================================== */

function updateBreakPagination(totalItems){

    const paginationInfo =
        document.getElementById(
            "breakPaginationInfo"
        );


    const pageNumber =
        document.getElementById(
            "breakPageNumber"
        );


    const previousButton =
        document.getElementById(
            "prevBreakPage"
        );


    const nextButton =
        document.getElementById(
            "nextBreakPage"
        );


    if(totalItems === 0){

        breakTotalPages = 1;

        breakCurrentPage = 1;


        if(paginationInfo){

            paginationInfo.textContent =
                "Showing 0–0 of 0";

        }


        if(pageNumber){

            pageNumber.textContent =
                "Page 1";

        }


        if(previousButton){

            previousButton.disabled = true;

        }


        if(nextButton){

            nextButton.disabled = true;

        }


        return;

    }


    breakTotalPages =
        Math.ceil(
            totalItems / breakPageSize
        );


    const startItem =
        (breakCurrentPage - 1)
        * breakPageSize + 1;


    const endItem =
        Math.min(
            breakCurrentPage * breakPageSize,
            totalItems
        );


    if(paginationInfo){

        paginationInfo.textContent =
            `Showing ${startItem}–${endItem} of ${totalItems}`;

    }


    if(pageNumber){

        pageNumber.textContent =
            `Page ${breakCurrentPage} of ${breakTotalPages}`;

    }


    if(previousButton){

        previousButton.disabled =
            breakCurrentPage <= 1;

    }


    if(nextButton){

        nextButton.disabled =
            breakCurrentPage >= breakTotalPages;

    }

}


/* ==========================================================
   PREVIOUS PAGE
========================================================== */

function previousBreakPage(){

    if(breakCurrentPage <= 1){
        return;
    }


    breakCurrentPage--;


    renderBreakManagement(
        breakAllData
    );

}


/* ==========================================================
   NEXT PAGE
========================================================== */

function nextBreakPage(){

    if(
        breakCurrentPage >=
        breakTotalPages
    ){

        return;

    }


    breakCurrentPage++;


    renderBreakManagement(
        breakAllData
    );

}


/* ==========================================================
   END BREAK
========================================================== */

window.endBreak = async function(id){

    if(!id){
        return;
    }


    try{

        await apiRequest( `/break-periods/breaks/${id}/end/`,
            {
                method: "POST"
            }
        );

        await loadBreakManagement();

    }

    catch(error){

        console.error(
            "Unable to end break:",
            error
        );

    }

};