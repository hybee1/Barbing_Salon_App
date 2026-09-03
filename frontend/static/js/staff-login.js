const loginForm = document.getElementById("staffLoginForm");


loginForm.addEventListener("submit", async function(event){

    event.preventDefault();

    const username_or_phone_number = document.getElementById("username_or_phone_number").value;

    const password = document.getElementById("password").value;


    const message = document.getElementById("loginMessage");

    try {

        const data = await publicRequest( "/staff/login/", "POST",
            {
                username: username_or_phone_number,
                password: password
            }
        );


        /*
          Cookies have already been set by Django.
         Just redirect to the dashboard.

        */

        window.location.href = data.redirect_url

    }

    catch(error){

        console.error(error);

        message.textContent = error.message || "Invalid login";

    }


});