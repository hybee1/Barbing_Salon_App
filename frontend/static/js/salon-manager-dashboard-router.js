/* ==========================================================
   salon-manager-dashboard-router.js
   Levelz Cuts - Salon Manager
========================================================== */

/* ==========================================================
   PAGE MAP
========================================================== */

const managerPages = {

    dashboard: "dashboardPage",
    bookings: "bookingsPage",
    services: "servicesPage",
    hairstyles: "hairstylesPage",
    colors: "colorsPage",
    staff: "staffPage",
    breaks: "breaksPage",
    reports: "reportsPage",
    inventory: "inventoryPage",
    settings: "settingsPage"

};



/* ==========================================================
   PAGE TITLE MAP
========================================================== */

const pageTitles = {

    dashboard: "Dashboard",
    bookings: "Bookings",
    services: "Services",
    hairstyles: "Hairstyles",
    colors: "Colors",
    staff: "Staff",
    breaks: "Breaks",
    reports: "Reports",
    inventory: "Inventory",
    settings: "Settings"

};



/* ==========================================================
   PAGE INITIALIZERS
========================================================== */

const pageActions = {

    dashboard() {

        window.initDashboardPage?.();
        window.loadDashboard?.();

    },

    bookings() {

        window.initBookingPage?.();
        window.loadBookings?.();

    },

    services() {

        window.initServicePage?.();
        window.loadServices?.();

    },

    hairstyles() {

        console.log("Initializing Hairstyles");

        window.initHairstylePage?.();
        window.loadHairstyles?.();

    },

    colors() {

        window.initColorPage?.();
        window.loadColors?.();

    },

    staff() {

        window.initStaffPage?.();
        window.loadStaffs?.();

    },

    breaks() {

        window.initBreakPage?.();
        window.loadBreakManagement?.();

    },

    reports() {

        window.initReportsPage?.();

    },

    inventory() {

        window.initInventoryPage?.();

    },

    settings() {

        window.initSettingsPage?.();
        window.loadSettings?.();

    }

};



/* ==========================================================
   STARTUP
========================================================== */

document.addEventListener("DOMContentLoaded", () => {

    initNavigation();

    initServiceMenu();

    initDashboardButtons();

    window.initLogout?.();

    openPage("dashboard");

});


/* ==========================================================
   NAVIGATION
========================================================== */

function initNavigation() {

    document.querySelectorAll(".nav-link").forEach(link => {

        link.addEventListener("click", e => {

            e.preventDefault();

            openPage(link.dataset.page);

        });

    });

}


/* ==========================================================
   OPEN PAGE
========================================================== */

function openPage(page) {

    /* Hide every page */

    document.querySelectorAll(".page-section").forEach(section => {

        section.hidden = true;

    });

    /* Show requested page */

    const target = document.getElementById(managerPages[page]);

    if (target) {

        target.hidden = false;

    }

    updateActiveLink(page);

    updateTitle(page);

    updateServiceMenu(page);

    /* Run page initializer */

    pageActions[page]?.();

}


/* ==========================================================
   ACTIVE SIDEBAR
========================================================== */

function updateActiveLink(page) {

    document.querySelectorAll(".nav-link").forEach(link => {

        link.classList.toggle(

            "active",

            link.dataset.page === page

        );

    });

}


/* ==========================================================
   TITLE
========================================================== */

function updateTitle(page) {

    const title = document.getElementById("pageTitle");

    if (title) {

        title.textContent = pageTitles[page] || "Dashboard";

    }

}


/* ==========================================================
   SERVICES MENU
========================================================== */

function initServiceMenu() {

    const button = document.querySelector(".nav-group-toggle");
    const submenu = document.querySelector(".nav-submenu");
    const arrow = button?.querySelector(".fa-angle-down");

    if (!button || !submenu) return;

    button.addEventListener("click", () => {

        submenu.classList.toggle("collapsed");

        arrow?.classList.toggle("fa-rotate-180");

    });

}


/* ==========================================================
   KEEP SERVICES MENU OPEN
========================================================== */

function updateServiceMenu(page) {

    const submenu = document.querySelector(".nav-submenu");
    const arrow = document.querySelector(".nav-group-toggle .fa-angle-down");

    if (!submenu) return;

    const openPages = [

        "services",

        "hairstyles",

        "colors"

    ];

    const shouldOpen = openPages.includes(page);

    submenu.classList.toggle("collapsed", !shouldOpen);

    arrow?.classList.toggle("fa-rotate-180", shouldOpen);

}


/* ==========================================================
   DASHBOARD BUTTONS
========================================================== */

function initDashboardButtons() {

    const buttons = {

        dashboardNewBookingBtn: "bookings",

        dashboardNewStaffBtn: "staff",

        dashboardReportsBtn: "reports",

        viewAllBookingsBtn: "bookings"

    };

    Object.entries(buttons).forEach(([id, page]) => {

        const button = document.getElementById(id);

        if (!button) return;

        button.addEventListener("click", () => {

            openPage(page);

        });

    });

}