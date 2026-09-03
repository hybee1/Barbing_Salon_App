/* ==========================================================
   barber-dashboard-router.js

   Levelz Cuts - Barber Dashboard Router
========================================================== */


/* ==========================================================
   PAGE MAP
========================================================== */

const barberPages = {

    dashboard: "dashboardPage",

    bookings: "bookingsPage",

    breaks: "breaksPage",

    settings: "settingsPage"

};


/* ==========================================================
   PAGE TITLES
========================================================== */

const barberPageTitles = {

    dashboard: "Welcome",

    bookings:  "Today's Bookings",

    breaks: "My Breaks",

    settings: "settings"

};


/* ==========================================================
   PAGE ACTIONS
========================================================== */

const barberPageActions = {

    dashboard() {

        window.loadBarberDashboard?.();

    },


    bookings() {

        window.initBarberBookings?.();

        window.loadBarberBookings?.();

    },


    breaks() {

        window.initBarberBreaks?.();

        window.loadBarberBreaks?.();

    },

    settings() {

        window.initBarberSettingsPage?.();

        window.loadBarberSettings?.();

    }

};


/* ==========================================================
   STARTUP
========================================================== */

document.addEventListener( "DOMContentLoaded", () => {

        initBarberNavigation();

        initBarberQuickActions();

        initBarberLogout();

        /*
            If the URL contains a valid hash,
            open that page.

            Otherwise open Dashboard.
        */

        const hash = window.location.hash .replace("#", "") .trim();


        if ( barberPages[hash] ) {

            openBarberPage(hash);

        }

        else {

            openBarberPage( "dashboard" );

        }

    }
);


/* ==========================================================
   NAVIGATION
========================================================== */

function initBarberNavigation() {

    document .querySelectorAll( ".nav-link" )
        .forEach(

            link => {

                link.addEventListener( "click", event => {

                        event.preventDefault();


                        const page = link.dataset.page;


                        if (!page) {

                            return;

                        }


                        openBarberPage( page );


                        /*
                            Keep the URL hash
                            synchronized.
                        */

                        if ( window.location.hash .replace("#", "") !== page ) {

                            history.replaceState( null, "", `#${page}`  );

                        }

                    }
                );

            }
        );

}


/* ==========================================================
   HASH NAVIGATION
========================================================== */

window.addEventListener( "hashchange", () => {

        const page = window.location.hash .replace("#", "") .trim();


        if ( barberPages[page] ) {

            openBarberPage( page );

        }

    }
);


/* ==========================================================
   OPEN PAGE
========================================================== */

function openBarberPage( page ) {

    if ( !barberPages[page] ) {

        page = "dashboard";

    }


    /*
        Hide every SPA page.
    */

    document .querySelectorAll(
            ".page-section" )
        .forEach(
            section => {

                section.hidden = true;

            }
        );


    /*
        Show requested page.
    */

    const target = document.getElementById( barberPages[page] );


    if (target) {

        target.hidden = false;

    }


    updateBarberActiveLink( page );


    updateBarberTitle( page );


    /*
        Run page action.
    */

    barberPageActions[ page ]?.();

}


/* ==========================================================
   ACTIVE SIDEBAR LINK
========================================================== */

function updateBarberActiveLink( page ) {

    document.querySelectorAll( ".nav-link" ) .forEach(
            link => {

                link.classList.toggle( "active", link.dataset.page === page );

            }
        );

}


/* ==========================================================
   PAGE TITLE
========================================================== */

function updateBarberTitle( page ) {

    const title = document.getElementById( "pageTitle" );


    if (!title) {

        return;

    }


    title.textContent = barberPageTitles[ page ] || "Welcome";

}


/* ==========================================================
   QUICK ACTIONS
========================================================== */

function initBarberQuickActions() {


    /*
        Dashboard Create Booking
        → /bookings/
    */

    const createBookingBtn = document.getElementById( "createBookingBtn" );


    if (createBookingBtn) {

        createBookingBtn.addEventListener(
            "click", () => {

                window.location.href = "/bookings/";

            }
        );

    }


    /*
        Dashboard Schedule Break
        → My Breaks page
    */

    const createBreakBtn = document.getElementById( "createBreakBtn" );


    if (createBreakBtn) {

        createBreakBtn.addEventListener(
            "click", () => {

                openBarberPage( "breaks" );


                history.replaceState( null, "", "#breaks" );

            }
        );

    }


    /*
        Today's Bookings Create Booking
        is initialized in barber-bookings.js.
    */

}


/* ==========================================================
   LOGOUT
========================================================== */

function initBarberLogout() {

    /*
        dashboard-logout.js handles
        the actual logout implementation.
    */

    if ( typeof window.initLogout === "function" ) {

        window.initLogout();

    }

}