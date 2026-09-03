// const API_URL = "http://localhost:8000/api";
// const BASE_URL = "http://localhost:8000";

 const API_URL = "http://127.0.0.1:8000/api";
 const BASE_URL = "http://127.0.0.1:8000";

// const API_URL = "https://untyped-hippopotamic-rosa.ngrok-free.dev/api";
// const BASE_URL = "https://untyped-hippopotamic-rosa.ngrok-free.dev";


/* ==========================================================
   Refresh Access Token
========================================================== */

async function refreshAccessToken() {

    try {

        const response = await fetch( `${API_URL}/auth/token/refresh/`,
            {
                method: "POST",
                credentials: "include"
            }
        );

        if (response.ok) {
           return true;
        }

        console.warn("Refresh token expired or invalid.");

        try {
            // whether you auth no logout must work
            await fetch( `${API_URL}/staff/logout/`,
                    {
                        method: "POST",
                        credentials: "include",
                        headers: {
                            "Content-Type": "application/json"
                        }
                    }
                );

            } catch (logoutError) {

                console.error(
                    "Logout request failed:",
                    logoutError
                );

            }

        // Redirect to login regardless of whether logout succeeded
        window.location.href = "/web/staff/login";

        return false;

        } catch (error) {

        console.error( "Unable to refresh access token:", error );

        window.location.href = "/web/staff/login";

        return false;
    }

}


/* ==========================================================
   Public Requests
   (Login, Register, Forgot Password, etc.)
========================================================== */

async function publicRequest(endpoint, method = "GET", body = null) {

    const options = {

        method,

        credentials: "include",

        headers: { "Content-Type": "application/json" }

    };

    if (body) {

        options.body = JSON.stringify(body);

    }

    const response = await fetch( `${API_URL}${endpoint}`, options  );

    const data = await response.json();

    if (!response.ok) {

        throw data;

    }

    return data;

}


/* ==========================================================
   Authenticated Requests
========================================================== */

async function apiRequest(endpoint, method = "GET", body = null) {

    const options = { method, credentials: "include", headers: {} };

    if (body) {
        if (body instanceof FormData) {
            options.body = body;
        } else {
            options.headers["Content-Type"] = "application/json";
            options.body = JSON.stringify(body);
        }
    }

    let response = await fetch(`${API_URL}${endpoint}`, options);

    if (response.status === 401) {
        const refreshed = await refreshAccessToken();

        if (!refreshed) {

            throw new Error("Authentication expired.");
//            return;
        }

        // Access token was refreshed successfully.
        // Retry the original request.
        response = await fetch(`${API_URL}${endpoint}`, options);
    }

    if (response.status === 204) {
        return null;
    }

    const data = await response.json();

    if (!response.ok) {
        throw data;
    }

    return data;
}