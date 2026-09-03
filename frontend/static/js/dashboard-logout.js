

/* ==========================================================
LOGOUT MANAGEMENT
========================================================== */

let logoutInitialized = false;


/* ==========================================================
INITIALIZE LOGOUT
========================================================== */

window.initLogout = function () {

    if (logoutInitialized) {

        return;

    }

    logoutInitialized = true;

    const logoutButton = document.getElementById("logoutBtn");

    if (!logoutButton) {

        return;

    }

    logoutButton.addEventListener( "click", handleLogout );

};


/* ==========================================================
HANDLE LOGOUT
========================================================== */

async function handleLogout() {

    try {

        await apiRequest( "/staff/logout/", "POST" );

        localStorage.removeItem("userData");

        window.location.href = "/web/staff/login/";

    }

    catch (error) {

        console.error(error);

        alert("Unable to logout.");

    }

}