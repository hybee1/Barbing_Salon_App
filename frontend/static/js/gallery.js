/* ==========================================================
   LEVELZ CUTS
   FULL HAIRSTYLE GALLERY
========================================================== */


/* ==========================================================
   DOM ELEMENTS
========================================================== */

const galleryGrid = document.getElementById("galleryCatalogGrid");

const gallerySearch = document.getElementById("hairstyleSearch");

const galleryFilters = document.getElementById("galleryFilters");

const galleryResults = document.getElementById("galleryResults");

const galleryEmpty = document.getElementById("galleryEmpty");

const galleryLoading = document.getElementById("galleryLoading");

const clearGallerySearch = document.getElementById("clearGallerySearch");



/* ==========================================================
   PAGINATION / STATE
========================================================== */

let allHairstyles = [];

let activeFilter = "all";

let searchTerm = "";

let nextHairstylesUrl = null;

let isLoadingHairstyles = false;



/* ==========================================================
   LOAD MORE BUTTON
========================================================== */

let loadMoreButton = null;



/* ==========================================================
   CREATE LOAD MORE BUTTON
========================================================== */

function createLoadMoreButton(){

    if(loadMoreButton){

        return;

    }

    loadMoreButton = document.createElement("button");

    loadMoreButton.type = "button";

    loadMoreButton.className = "btn btn-primary gallery-load-more";

    loadMoreButton.innerHTML = `
        <i class="fa-solid fa-plus"></i>
        Load More Styles
    `;


    loadMoreButton.addEventListener( "click", loadNextHairstylePage );

    const catalog = document.querySelector( ".gallery-catalog .container" );

    if(catalog){

        catalog.appendChild( loadMoreButton );

    }

}


/* ==========================================================
   LOAD INITIAL HAIRSTYLES
========================================================== */

async function loadAllHairstyles(){

    if(!galleryGrid || isLoadingHairstyles){

        return;

    }


    isLoadingHairstyles = true;

    showGalleryLoading(true);

    try{

        /*
         * IMPORTANT:
         *
         * publicApiFetch() handles the API
         * configuration for the application.
         *
         * Do NOT define another API base URL here.
         */

        const data = await publicApiFetch( "/hairstyles/" );


        /*
         * DRF paginated response:
         *
         * {
         *     count: 50,
         *     next: "...",
         *     previous: null,
         *     results: [...]
         * }
         */

        const results = Array.isArray(data) ? data : (data.results || []);

        /*
         * Store the first page.
         */

        allHairstyles = results;

        /*
         * Store the URL for the next page.
         *
         * If pagination is disabled,
         * this will remain null.
         */

        nextHairstylesUrl = Array.isArray(data) ? null : (data.next || null);

        createLoadMoreButton();

        renderGallery();

        updateLoadMoreButton();


    }
    catch(error){

        console.error( "Failed to load hairstyles:", error );

        allHairstyles = [];

        nextHairstylesUrl = null;

        galleryGrid.innerHTML = "";

        galleryResults.textContent = "Unable to load hairstyles.";

        galleryEmpty.hidden = false;

        updateLoadMoreButton();

    }
    finally{

        isLoadingHairstyles = false;

        showGalleryLoading(false);

    }

}


/* ==========================================================
   LOAD NEXT API PAGE
========================================================== */

async function loadNextHairstylePage(){

    if( !nextHairstylesUrl || isLoadingHairstyles ){

        return;

    }


    isLoadingHairstyles = true;

    setLoadMoreLoading(true);


    try {

    /*
     * DRF's "next" value may be an absolute URL, for example:
     *
     * http://127.0.0.1:8000/api/hairstyles/?page=2
     *
     * publicApiFetch() already has the API base URL configured,
     * so it should NOT receive:
     *
     * /api/hairstyles/?page=2
     *
     * Instead, it should receive only the endpoint and query string:
     *
     * /hairstyles/?page=2
     *
     * This allows publicApiFetch() to prepend its own base URL:
     *
     * http://127.0.0.1:8000/api
     */

    let nextUrl = nextHairstylesUrl;

    try {

        const parsedUrl = new URL(
            nextHairstylesUrl,
            window.location.origin
        );

        /*
         * Get only the endpoint + query string.
         *
         * Example:
         *
         * /api/hairstyles/?page=2
         *
         * becomes:
         *
         * /hairstyles/?page=2
         */

        nextUrl = parsedUrl.pathname + parsedUrl.search;

        /*
         * Remove the API base path because
         * publicApiFetch() already adds /api.
         */

        if (nextUrl.startsWith("/api/")) {

            nextUrl = nextUrl.substring(4);

        }

	if (nextUrl.startsWith("/web/")) {

            nextUrl = nextUrl.substring(4);

        }

    } catch (error) {

        /*
         * If DRF returned a value that cannot be parsed
         * as a URL, use it as-is.
         */

        nextUrl = nextHairstylesUrl;

    }

    const data = await publicApiFetch(nextUrl);


        const results = Array.isArray(data) ? data : (data.results || []);

        /*
         * APPEND the next page.
         *
         * Do not replace allHairstyles.
         */

        allHairstyles.push(...results );


        /*
         * Save the following page.
         */

        nextHairstylesUrl = Array.isArray(data) ? null : (data.next || null);

        renderGallery();

        updateLoadMoreButton();


    }
    catch(error){

        console.error( "Failed to load more hairstyles:",  error );

    }
    finally{

        isLoadingHairstyles = false;

        setLoadMoreLoading(false);

    }

}


/* ==========================================================
   RENDER GALLERY
========================================================== */

function renderGallery(){

    const filteredHairstyles = getFilteredHairstyles();

    galleryGrid.innerHTML = "";


    /*
     * Nothing matches the current search/filter.
     */

    if(filteredHairstyles.length === 0){

        galleryEmpty.hidden = false;

        galleryResults.textContent = "No styles found.";

        return;

    }


    galleryEmpty.hidden = true;

    galleryResults.textContent =
        `Showing ${filteredHairstyles.length} `
        + `${filteredHairstyles.length === 1 ? "style" : "styles"}`;


    filteredHairstyles.forEach(
        hairstyle => {

            galleryGrid.appendChild(
                createHairstyleCard(
                    hairstyle
                )
            );

        }
    );

}



/* ==========================================================
   FILTER HAIRSTYLES
========================================================== */

function getFilteredHairstyles(){

    return allHairstyles.filter(
        hairstyle => {

            const name = ( hairstyle.name ||  "" ) .toLowerCase();

            /*
             * SEARCH
             */

            const matchesSearch = !searchTerm || name.includes( searchTerm );

            /*
             * CATEGORY
             */

            const matchesFilter = matchesCategory( name, activeFilter );

            return ( matchesSearch && matchesFilter );

        }
    );

}



/* ==========================================================
   CATEGORY MATCHING
========================================================== */

function matchesCategory( name, filter ){

    if(filter === "all"){

        return true;

    }


    if(filter === "fade"){

        return name.includes( "fade" );

    }


    if(filter === "afro"){

        return name.includes( "afro" );

    }

    if(filter === "dread"){

        return name.includes( "dread"  );

    }


    if(filter === "mohawk"){

        return name.includes(  "mohawk" );

    }

    if(filter === "other"){

        return !(
            name.includes("fade") ||
            name.includes("afro") ||
            name.includes("dread") ||
            name.includes("mohawk")
        );

    }

    return true;

}



/* ==========================================================
   CREATE HAIRSTYLE CARD
========================================================== */

function createHairstyleCard( hairstyle ){

    const card = document.createElement( "article" );

    card.className = "gallery-catalog-card";

    const image = document.createElement( "img" );

    image.src = hairstyle.image;

    image.alt = hairstyle.name || "Hairstyle";

    image.loading = "lazy";

    const overlay = document.createElement( "div" );

    overlay.className = "gallery-card-overlay";

    const title = document.createElement( "h3" );

    title.className = "gallery-card-title";

    title.textContent = hairstyle.name || "Hairstyle";

    const actions = document.createElement( "div" );

    actions.className = "gallery-card-actions";


    /* ======================================================
       VIEW STYLE
    ======================================================= */

    const viewButton = document.createElement( "button" );

    viewButton.type = "button";

    viewButton.className = "gallery-card-view";

    viewButton.innerHTML = `
        <i class="fa-solid fa-expand"></i>
        View Style
    `;


    viewButton.addEventListener(
        "click", event => {

            event.stopPropagation();

            openGalleryModal( hairstyle );

        }
    );



    /* ======================================================
       BOOK STYLE
    ======================================================= */

    const bookLink = document.createElement( "a" );

    bookLink.className = "gallery-card-book";

    bookLink.href = `/bookings/?hairstyle_id=${hairstyle.id}`;

    bookLink.innerHTML = `
        <i class="fa-solid fa-calendar-check"></i>
        Book
    `;

    bookLink.addEventListener( "click", event => { event.stopPropagation();  }
    );


    /* ======================================================
       BUILD CARD
    ======================================================= */

    actions.appendChild( viewButton  );

    actions.appendChild( bookLink );

    overlay.appendChild( title );

    overlay.appendChild( actions );

    card.appendChild( image );

    card.appendChild( overlay );

    /*
     * Clicking the card opens
     * the image preview.
     */

    card.addEventListener( "click",  () => {

            openGalleryModal(hairstyle);

        }
    );


    return card;

}



/* ==========================================================
   MODAL ELEMENTS
========================================================== */

const galleryModal = document.getElementById( "galleryModal" );

const galleryModalImage = document.getElementById("galleryModalImage");

const galleryModalTitle = document.getElementById( "galleryModalTitle" );

const galleryModalClose = document.getElementById( "galleryModalClose");



/* ==========================================================
   OPEN MODAL
========================================================== */

function openGalleryModal( hairstyle){

    if(!galleryModal){

        return;

    }

    galleryModalImage.src =  hairstyle.image;

    galleryModalImage.alt = hairstyle.name || "Hairstyle";

    galleryModalTitle.textContent = hairstyle.name || "Hairstyle";

    const modalBook = document.getElementById( "galleryModalBook" );

    if(modalBook){

        modalBook.href = `/bookings/?hairstyle_id=${hairstyle.id}`;

    }

    galleryModal.classList.add( "active" );

    galleryModal.setAttribute( "aria-hidden", "false" );

    document.body.style.overflow = "hidden";

}



/* ==========================================================
   CLOSE MODAL
========================================================== */

function closeGalleryModal(){

    if(!galleryModal){

        return;

    }

    galleryModal.classList.remove( "active" );

    galleryModal.setAttribute("aria-hidden", "true" );


    galleryModalImage.src = "";


    document.body.style.overflow = "";

}



/* ==========================================================
   SEARCH
========================================================== */

if(gallerySearch){

    gallerySearch.addEventListener( "input", event => {

            searchTerm = event.target.value.trim().toLowerCase();

            renderGallery();

        }
    );

}



/* ==========================================================
   FILTER BUTTONS
========================================================== */

if(galleryFilters){

    galleryFilters.querySelectorAll(".gallery-filter" )
        .forEach( button => {

                button.addEventListener( "click", () => {

                        galleryFilters.querySelectorAll(".gallery-filter" )
                            .forEach( item => {

                                    item.classList.remove( "active" );

                                }
                            );


                        button.classList.add( "active" );

                        activeFilter =  button.dataset.filter;

                        renderGallery();

                    }
                );

            }
        );

}



/* ==========================================================
   CLEAR SEARCH / FILTER
========================================================== */

if(clearGallerySearch){

    clearGallerySearch.addEventListener( "click", () => {

            searchTerm = "";

            activeFilter = "all";

            if(gallerySearch){

                gallerySearch.value = "";

            }

            galleryFilters.querySelectorAll(".gallery-filter" )
                .forEach(
                    button => {

                        button.classList.remove( "active" );


                        if( button.dataset.filter === "all" ){

                            button.classList.add( "active" );

                        }

                    }
                );


            renderGallery();

        }
    );

}



/* ==========================================================
   MODAL EVENTS
========================================================== */

if(galleryModalClose){

    galleryModalClose.addEventListener( "click", closeGalleryModal );

}

if(galleryModal){

    const backdrop = galleryModal.querySelector(".gallery-modal-backdrop");


    if(backdrop){

        backdrop.addEventListener( "click", closeGalleryModal );

    }

}



/* ==========================================================
   ESCAPE KEY
========================================================== */

document.addEventListener("keydown", event => {

        if( event.key === "Escape" && galleryModal &&
              galleryModal.classList.contains( "active" ) ){

            closeGalleryModal();

        }

    }
);



/* ==========================================================
   MOBILE NAVIGATION
========================================================== */

const menuBtn = document.querySelector( ".menu-btn" );


const navLinks = document.querySelector( ".nav-links" );


if(menuBtn && navLinks){

    menuBtn.addEventListener( "click",  () => {

            navLinks.classList.toggle( "active" );

        }
    );

}


document
    .querySelectorAll( ".nav-links a" )
    .forEach(
        link => {

            link.addEventListener("click",  () => {

                    if(navLinks){

                        navLinks.classList.remove( "active" );

                    }

                }
            );

        }
    );



/* ==========================================================
   LOADING STATE
========================================================== */

function showGalleryLoading(show){

    if(!galleryLoading){

        return;

    }

    galleryLoading.style.display = show ? "flex" : "none";

}



/* ==========================================================
   LOAD MORE BUTTON STATE
========================================================== */

function updateLoadMoreButton(){

    if(!loadMoreButton){

        return;

    }


    /*
     * No next page means all hairstyles
     * have already been loaded.
     */

    if(!nextHairstylesUrl){

        loadMoreButton.style.display = "none";

        return;

    }

    loadMoreButton.style.display = "inline-flex";

    loadMoreButton.disabled = false;

    loadMoreButton.innerHTML = `
        <i class="fa-solid fa-plus"></i>
        Load More Styles
    `;

}



/* ==========================================================
   LOAD MORE BUTTON LOADING
========================================================== */

function setLoadMoreLoading(
    loading
){

    if(!loadMoreButton){

        return;

    }


    if(loading){

        loadMoreButton.disabled =
            true;


        loadMoreButton.innerHTML = `
            <i class="fa-solid fa-spinner fa-spin"></i>
            Loading Styles...
        `;


        return;

    }


    updateLoadMoreButton();

}



/* ==========================================================
   INITIALIZE
========================================================== */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadAllHairstyles();

    }
);