
// public-api-calls.js


const BASE_URL = "http://127.0.0.1:8000/web";
const IMAGE_BASE_URL = "http://127.0.0.1:8000/";

// const BASE_URL = "https://untyped-hippopotamic-rosa.ngrok-free.dev/web";
// const IMAGE_BASE_URL = "https://untyped-hippopotamic-rosa.ngrok-free.dev/";


async function publicApiFetch(endpoint, method = "GET", body = null) {

    try {
        const options = {
            method: method,
            headers: {
                "Content-Type": "application/json"
            }
        };

        // Only add body when one was provided
        if (body !== null && body !== undefined) {
            options.body = JSON.stringify(body);
        }

        const res = await fetch(`${BASE_URL}${endpoint}`, options);

        // --------------------------------
        // Try to parse JSON response
        // --------------------------------

        let data = null;

        try {
            data = await res.json();
        } catch (e) {
            // Response wasn't JSON
        }


        // --------------------------------
        // SUCCESS
        // --------------------------------

        if (res.ok) {
            return data;
        }


        // --------------------------------
        // ERROR
        // --------------------------------

        let message = `HTTP ${res.status} ${res.statusText}`;

        if (data) {

            const error = data.error;


            // --------------------------------
            // APIException
            //
            // {
            //     "success": false,
            //     "error": {
            //         "detail": "booking conflict"
            //     }
            // }
            // --------------------------------

            if (
                error &&
                typeof error === "object" &&
                typeof error.detail === "string"
            ) {
                message = error.detail;
            }


            // --------------------------------
            // DRF validation errors
            //
            // {
            //     "success": false,
            //     "error": {
            //         "customer_name": [
            //             "Full name should contain only letters and spaces."
            //         ]
            //     }
            // }
            // --------------------------------

            else if (
                error &&
                typeof error === "object"
            ) {

                const messages = Object.entries(error)
                    .map(([field, errors]) => {

                        if (Array.isArray(errors)) {
                            return `${field}: ${errors.join(", ")}`;
                        }

                        return `${field}: ${errors}`;
                    })
                    .filter(Boolean);

                if (messages.length > 0) {
                    message = messages.join("\n");
                }
            }


            // --------------------------------
            // Fallbacks
            // --------------------------------

            else if (typeof error === "string") {
                message = error;
            }

            else if (data.detail) {
                message = data.detail;
            }

            else if (data.message) {
                message = data.message;
            }

            else if (typeof data === "string") {
                message = data;
            }
        }


        console.error("API Error:", {
            status: res.status,
            message: message,
            response: data
        });

        alert(message);

        return null;


    } catch (err) {

        console.error("Fetch failed:", err);

        alert(
            "Unable to connect to the server. " +
            "Please check your internet connection."
        );

        return null;
    }
}

