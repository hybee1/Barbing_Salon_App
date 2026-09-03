

/* ==========================================
PRIMECUTS BARBERSHOP
MAIN JS
========================================== */


/* ==========================================
API BASE
========================================== */

// const API_BASE = "http://localhost:8000/web";
// const BASE_URL = "http://localhost:8000";

 const API_BASE = "http://127.0.0.1:8000/web";
 const BASE_URL = "http://127.0.0.1:8000";

// const API_BASE = "https://untyped-hippopotamic-rosa.ngrok-free.dev/web";
// const BASE_URL = "https://untyped-hippopotamic-rosa.ngrok-free.dev";

/* ==========================================
MOBILE MENU
========================================== */

const menuBtn = document.querySelector(".menu-btn");
const navLinks = document.querySelector(".nav-links");

if(menuBtn && navLinks){

    menuBtn.addEventListener("click",()=>{

        navLinks.classList.toggle("active");

    });

}

/* ======================================
CLOSE MENU
====================================== */

document.querySelectorAll(".nav-links a")
.forEach(link=>{

    link.addEventListener("click",()=>{

        navLinks.classList.remove("active");

    });

});

/* ==========================================
SMOOTH SCROLL
========================================== */

document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener("click", (e) => {
        e.preventDefault();

        const targetId = link.getAttribute("href");
        const target = document.querySelector(targetId);

        if (target) {
            target.scrollIntoView({
                behavior: "smooth"
            });
        }

        navLinks.classList.remove("active");
    });
});


/* ==========================================
FETCH HELPERS
========================================== */

async function fetchData(endpoint) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`);
        if (!res.ok) throw new Error("Network error");
        return await res.json();
    } catch (err) {
        console.error(err);
        return [];
    }
}


/* ==========================================
LOAD SERVICES (DRF)
========================================== */

async function loadServices() {

    const container = document.querySelector(".services-grid");

    if (!container) return;

    const services_result = await fetchData("/services/");

    const services = services_result.results;

    // Homepage preview only

    container.innerHTML = services.map(service => `
            <div class="service-card">

                <img class="service-bg" src="${service.image}" alt="${service.name}"
                loading="lazy" >

                <div class="service-overlay"></div>

                <div class="service-content">
                    <h3>${service.name}</h3>

                    <p>${service.duration_minutes} mins</p>

                    <span>₦${service.price}</span>

                    <a href="#booking">Book Now</a>
                </div>

            </div>
        `).join("");

    enableGalleryModal();

}

/* ==========================================
LOAD BARBERS (DRF)
========================================== */

async function loadBarbers() {
    const container = document.querySelector(".barbers-grid");
    if (!container) return;

    const barbers = await fetchData("/staffs/barbers/");

    const featuredBarbers = barbers.slice(0,4);

    container.innerHTML = featuredBarbers.map(barber => `
    <div class="barber-card">

        ${barber.user.image
        ? `<img class="barber-bg" src="${barber.user.image}" alt="${barber.user.username}">`
        : `<div class="barber-bg barber-placeholder">${barber.user.username}</div>`
        }

        <div class="barber-overlay"></div>

        <div class="barber-content">
            <h3>${barber.user.username}</h3>
            <p>${barber.user.role || "Barber"}</p>
            <span>★★★★★</span>
        </div>

    </div>
    `).join("");

}

/* ==========================================
LOAD GALLERY (DRF)
========================================== */

/* ==========================================
LOAD GALLERY (DRF)
========================================== */

async function loadGallery() {

    const container = document.querySelector(".gallery-grid");

    if (!container) return;

    const hairstyles_result = await fetchData("/hairstyles/");

    const hairstyles = hairstyles_result.results || [];

    container.innerHTML = hairstyles.map(hairstyle => `

        <div class="gallery-item">

            <img
                src="${hairstyle.image}"
                alt="${hairstyle.name}"
                loading="lazy"
            >

            <div class="gallery-item-overlay">

                <h3 class="gallery-item-title">
                    ${hairstyle.name}
                </h3>

                <div class="gallery-item-actions">

                    <button
                        type="button"
                        class="gallery-view-style"
                        data-image="${hairstyle.image}"
                        data-name="${hairstyle.name}"
                    >
                        <i class="fa-solid fa-expand"></i>
                        View Style
                    </button>

                    <a
                        href="/bookings/?hairstyle_id=${hairstyle.id}"
                        class="gallery-book-style"
                    >
                        <i class="fa-solid fa-calendar-check"></i>
                        Book
                    </a>

                </div>

            </div>

        </div>

    `).join("");

    enableGalleryModal();

}


/* ==========================================
   GALLERY MODAL
   SAME MODAL AS FULL GALLERY PAGE
========================================== */

function enableGalleryModal() {

    const items = document.querySelectorAll(".gallery-item");

    items.forEach(item => {

        const image = item.querySelector("img");

        const viewButton = item.querySelector(".gallery-view-style");

        const bookLink = item.querySelector(".gallery-book-style");


        /* ======================================
           VIEW STYLE BUTTON
        ====================================== */

        if (viewButton) {

            viewButton.addEventListener("click", event => {

                event.stopPropagation();

                /* Prevent duplicate modals */

                const existingModal =
                    document.querySelector(".gallery-modal");

                if (existingModal) {
                    existingModal.remove();
                }


                /* Create modal */

                const modal = document.createElement("div");

                modal.classList.add("gallery-modal", "active");


                modal.innerHTML = `

                    <div class="gallery-modal-backdrop"></div>


                    <div class="gallery-modal-content">

                        <button
                            type="button"
                            class="gallery-modal-close"
                            aria-label="Close"
                        >

                            <i class="fa-solid fa-xmark"></i>

                        </button>


                        <div class="gallery-modal-image-wrapper">

                            <img
                                src="${image.src}"
                                alt="${image.alt}"
                            >

                        </div>


                        <div class="gallery-modal-info">

                            <h3>
                                ${image.alt}
                            </h3>

                            <a
                                href="${bookLink ? bookLink.href : '#'}"
                                class="btn btn-primary"
                            >

                                <i class="fa-solid fa-calendar-check"></i>

                                Book This Style

                            </a>

                        </div>

                    </div>

                `;


                document.body.appendChild(modal);


                /* ======================================
                   CLOSE MODAL
                ====================================== */

                const closeModal = () => {

                    modal.remove();

                    document.removeEventListener(
                        "keydown",
                        closeWithEscape
                    );

                };


                /* Click backdrop */

                const backdrop =
                    modal.querySelector(".gallery-modal-backdrop");

                backdrop.addEventListener(
                    "click",
                    closeModal
                );


                /* Click close button */

                const closeButton =
                    modal.querySelector(".gallery-modal-close");

                closeButton.addEventListener(
                    "click",
                    closeModal
                );


                /* ======================================
                   ESCAPE KEY
                ====================================== */

                const closeWithEscape = event => {

                    if (event.key === "Escape") {

                        closeModal();

                    }

                };


                document.addEventListener(
                    "keydown",
                    closeWithEscape
                );


                /* ======================================
                   PREVENT BODY SCROLL
                ====================================== */

                document.body.style.overflow = "hidden";


                /* Restore body scroll when modal closes */

                const originalRemove = modal.remove.bind(modal);

                modal.remove = () => {

                    document.body.style.overflow = "";

                    originalRemove();

                };

            });

        }


        /* ======================================
           BOOK BUTTON
        ====================================== */

        if (bookLink) {

            bookLink.addEventListener("click", event => {

                event.stopPropagation();

            });

        }


        /* ======================================
           CLICK IMAGE
        ====================================== */

        if (image) {

            image.addEventListener("click", () => {

                if (viewButton) {

                    viewButton.click();

                }

            });

        }

    });

}


/* ==========================================
STICKY NAV ON SCROLL
========================================== */

window.addEventListener("scroll", () => {
    const header = document.querySelector("header");

    if (window.scrollY > 50) {
        header.classList.add("sticky");
    } else {
        header.classList.remove("sticky");
    }
});


/* ==========================================
    LOAD CONTACT DETAILS
========================================== */

async function loadSalonContactDetails() {

     try {

        const salonContactDetails = await fetchData("/settings/salon-info-web/");

        console.log("1");
        console.log(salonContactDetails);

        if (!salonContactDetails) {
            return;
        }

        console.log("2");

        const salonPhoneNumber = document.getElementById("salonPhoneNumber");
        console.log(salonPhoneNumber);

        const salonEmail = document.getElementById("salonEmail");
        console.log(salonEmail);

        const salonOpenAndCloseTime = document.getElementById("salonOpenAndCloseTime");
        console.log(salonOpenAndCloseTime);

        console.log("3");

        if (salonPhoneNumber) {
            salonPhoneNumber.textContent = "Phone: " + (salonContactDetails.phone_number || "");
        }

        if (salonEmail) {
            salonEmail.textContent = "Email: " + (salonContactDetails.email || "");
        }

        if (salonOpenAndCloseTime) {
            salonOpenAndCloseTime.textContent =
                String(salonContactDetails.open_time || "").slice(0, 5) +
                " - " +
                String(salonContactDetails.close_time || "").slice(0, 5);
        }


        console.log("4");

     }

    catch (error) {

        console.error( "Unable to load salon contact details:", error );

    }

}


/* ==========================================
INIT
========================================== */

document.addEventListener("DOMContentLoaded", () => {
    loadServices();
    loadBarbers();
    loadGallery();
    loadSalonContactDetails();
});