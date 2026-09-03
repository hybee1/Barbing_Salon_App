
// const API_BASE = "http://localhost:8000/api";
// const BASE_URL = "http://localhost:8000";

//const API_BASE = "https://untyped-hippopotamic-rosa.ngrok-free.dev/api";
//const BASE_URL = "https://untyped-hippopotamic-rosa.ngrok-free.dev";


/* ==========================================
BOOKING STATE
========================================== */

let currentStep = 1;

let bookingData = {
    service: null,
    hairstyle: null,
    color: null,
    barber: null,
    date: null,
    time: null,
    customer: {}
};

// Only stores the currently selected service details
let selectedServiceCache = null;

function saveBookingData() {
    localStorage.setItem("bookingData", JSON.stringify(bookingData));
}



/* ==========================================
STEP CONTROL
========================================== */

function showStep(step) {

    document.querySelectorAll(".step-box")
    .forEach(box => {

        box.classList.remove("active");

    });

    document.querySelectorAll(".steps-progress .step")
    .forEach((s,index)=>{

        s.classList.toggle(
            "active",
            index < step
        );

    });

    document
    .getElementById(`step-${step}`)
    .classList.add("active");


    currentStep = step;

    // Load cached data when entering steps

    if(step === 2){

        loadStylesForSelectedServiceFromCache();

    }

    if(step === 3){

        loadColorsForSelectedServiceFromCache();

    }

}

function canProceed(step){

    switch(step){

        case 1:
            return bookingData.service;

        case 2:
            return true; // Hairstyle optional

        case 3:
            return true; // Color optional

        case 4:
            return bookingData.barber;

        case 5:
            return bookingData.date;

        case 6:
            return bookingData.time;

        default:
            return true;
    }

}

async function nextStep() {

    if (!canProceed(currentStep)) {

        alert("Please make a selection first.");
        return;

    }

    /*  When leaving Service step, load hairstyles and colors */

    if(currentStep === 1){

        await loadServiceHairStylesAndColors();
    }

    if(currentStep < 7){

        showStep(currentStep + 1);

    }

}

function prevStep() {
    if (currentStep > 1) {
        showStep(currentStep - 1);
    }
}


/* ==========================================
LOAD SERVICES
========================================== */

async function loadServices() {
    const box = document.getElementById("servicesBox");

    const services_result = await publicApiFetch("/services/");

    if (!services_result) return;

    const services = services_result.results;

    box.innerHTML = services.map(s => `
        <div class="card"
        onclick="selectService(this, ${s.id}, '${s.name}', ${s.duration_minutes}, ${s.price})">
            <h3>${s.name}</h3>
            <p>${s.duration_minutes} mins</p>
            <strong>₦${s.price}</strong>
        </div>
    `).join("");
}

/* ==========================================
 SELECT SERVICE
========================================== */
function selectService(card, id, name, duration, price) {
    bookingData.service = { id, name, duration, price };
    highlightSelected(card, "servicesBox");
    // Save to localStorage
    saveBookingData();
    console.log(bookingData.service)
    document.getElementById("serviceNextBtn").disabled = false;
    // loadStylesForSelectedService(); // load hairstyles here
}

async function loadServiceHairStylesAndColors(){

    const serviceId = bookingData.service.id;

    // If same service is already cached
    if( selectedServiceCache && selectedServiceCache.id === serviceId ) {

        console.log("Using service cache");

        return;

    }

    console.log("Loading service details");

    const data_result = await publicApiFetch( `/services/${serviceId}/hairstylesandcolors/` );

    if (!data_result) return;

    selectedServiceCache = data_result;

    console.log( "Service cache updated", selectedServiceCache );

}

function loadStylesForSelectedServiceFromCache(){

    const box = document.getElementById("stylesBox");

    if( !selectedServiceCache || !selectedServiceCache.hairstyles ) {

        box.innerHTML = "<p>No hairstyles available.</p>";

        return;

    }

    const styles = selectedServiceCache.hairstyles;

    box.innerHTML = styles.map(style => `

        <div class="card" onclick=" selectStyle( this,  ${style.id}, '${style.name}',
            ${style.price || 0}, ${style.duration_minutes || 0} )">

            <img src="${IMAGE_BASE_URL}${style.image}" alt="${style.name}">

            <h3>${style.name}</h3>

        </div>

    `).join("");

}

/* ==========================================
 SELECT HAIRSTYLE
========================================== */
function selectStyle(card, id, name, price, duration) {
    bookingData.hairstyle = { id, name, price, duration};
    highlightSelected(card, "stylesBox");
    saveBookingData();
    console.log(bookingData.hairstyle)
}

/* ==========================================
LOAD COLORS
========================================== */

function loadColorsForSelectedServiceFromCache(){


    const box = document.getElementById("colorsBox");

    if( !selectedServiceCache || !selectedServiceCache.colors ) {

        box.innerHTML = "<p>No colors available.</p>";

        return;

    }

    const colors = selectedServiceCache.colors;

    box.innerHTML = colors.map(color => `

        <div class="card" onclick=" selectColor( this, ${color.id}, '${color.name}', ${color.duration || 0})">

            <h3>${color.name}</h3>

        </div>


    `).join("");

}

/* ==========================================
SELECT COLOR
========================================== */

function selectColor(card, id, name, duration){

    bookingData.color = { id, name, duration };

    highlightSelected(card,"colorsBox");

    saveBookingData();

}

/* ==========================================
LOAD BARBERS
========================================== */

async function loadBarbers() {
    const box = document.getElementById("barbersBox");

    const barbers = await publicApiFetch("/staffs/barbers/");

    if (!barbers) return;

    box.innerHTML = barbers.map(barber => `
    <div class= "card barber-card"
     onclick="selectBarber(this, ${barber.id}, '${barber.user.username}')">

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

function selectBarber(card, id, name) {
    bookingData.barber = { id, name };
    highlightSelected(card, "barbersBox");
    saveBookingData();
    console.log(bookingData.barber)
    document.getElementById("barberNextBtn").disabled = false;
}

/* ==========================================
DATE HANDLING
========================================== */

document.getElementById("dateInput")?.addEventListener("change", (e) => {
    bookingData.date = e.target.value;
    document.getElementById("dateNextBtn").disabled = false;
    saveBookingData();
    console.log(bookingData.date)
    loadTimeSlots();
});

/* ==========================================
TIME SLOTS (FROM BACKEND LOGIC)
========================================== */

async function loadTimeSlots() {
    const box = document.getElementById("timeBox");

    if (!bookingData.service || !bookingData.barber || !bookingData.date) {
        box.innerHTML = "<p>Select service, barber and date first</p>";
        return;
    }

    const totalDuration =
    (bookingData.service?.duration || 0) +
    (bookingData.hairstyle?.duration || 0) +
    (bookingData.color?.duration || 0);

    const params = new URLSearchParams({
                barber_id: bookingData.barber.id,
                date: bookingData.date,
                total_service_duration: totalDuration,
        });

    // const url = `/barbers/barber/availability/?${params.toString()}`;
    const url = `/bookings/barber/availability/?${params.toString()}`;

    const slots = await publicApiFetch(url);

    if (!slots) return;

    slots.sort(); // sort in increasing order

    box.innerHTML = slots.map(time => `
            <div class="time-slot"
                 onclick="selectTime(this, '${time}')">
                ${time.substring(0,5)}
            </div>
        `).join("");
}

function selectTime(card, time) {
    bookingData.time = time;
    document.getElementById("timeNextBtn").disabled = false;
    highlightSelectedTime(card);
    saveBookingData();
}

/* ==========================================
HIGHLIGHT HELPERS
========================================== */

function highlightSelected(selectedCard, containerId) {

    const container = document.getElementById(containerId);

    container.querySelectorAll(".card").forEach(card => {
        card.classList.remove("selected");
    });

    selectedCard.classList.add("selected");
}

function highlightSelectedTime(selectedSlot) {

    document.querySelectorAll(".time-slot").forEach(slot => {
        slot.classList.remove("selected");
    });

//    event.currentTarget.classList.add("selected");
        selectedSlot.classList.add("selected");
}

/* ==========================================
SUBMIT BOOKING
========================================== */

async function submitBooking() {

    bookingData.customer = {
        /*full_name: document.getElementById("fullName").value,*/
        customer_name: document.getElementById("CustomerName").value,
        /*email: document.getElementById("email").value,*/
        phone: document.getElementById("phone").value
    };

    const service = bookingData.service;
    const barber = bookingData.barber;
    const bookingDate = bookingData.date;

    const customerName = bookingData.customer.customer_name.trim();
    const phone = bookingData.customer.phone.trim();

    if ( !service || !barber || !bookingDate ||
          !bookingData.time ) {
            alert("Please complete all booking steps");
            return;
    }

    if ( !customerName || !phone ) {
        alert("Please enter your name and phone number.");
        return;
    }

    if (!/^[A-Za-z]+(?: [A-Za-z]+)*$/.test(customerName)) {
        alert("Please enter a valid name using letters and spaces only.");
        return;
    }

    const data = await publicApiFetch("/bookings/create/", "POST", bookingData);

    if (!data) {
    // fetchData() already alerted the backend error
    return;
    }
    // Request succeeded
    document.getElementById("bookingReference").textContent = data.booking_reference;
    document.getElementById("successModal").style.display = "flex";
    localStorage.removeItem("bookingData");

}

/* ==========================================
INIT
========================================== */

document.addEventListener("DOMContentLoaded", async () => {

    const saved = localStorage.getItem("bookingData");

    if (saved) {
        /*Object.assign(bookingData, JSON.parse(saved));*/
        bookingData = {
                    ...bookingData,
                    ...JSON.parse(saved)
};
    }

    await loadServices();
    await loadBarbers();

    if (bookingData.service) {

    await loadServiceHairStylesAndColors();

    loadStylesForSelectedServiceFromCache();

    loadColorsForSelectedServiceFromCache();

    }
});

function copyBookingReference() {

    const btn = event.currentTarget;

    navigator.clipboard.writeText(
        document.getElementById("bookingReference").textContent
    );

    btn.innerHTML =
        '<i class="fa-solid fa-check"></i> Copied';

    setTimeout(() => {

        btn.innerHTML =
            '<i class="fa-regular fa-copy"></i> Copy';

    }, 2000);

}


function goHome() {

    window.location.href = "/";

}