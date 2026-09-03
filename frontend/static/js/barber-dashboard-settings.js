
/* ==========================================================
   barber-dashboard-settings.js

   Levelz Cuts - Barber Dashboard Settings
========================================================== */

let settingsPageInitialized = false;

let userDetailsSnapshot = {
    username: "",
    phone_number: "",
    email: "",
    profile_image: ""
};


/* ==========================================================
   INITIALIZE SETTINGS PAGE
========================================================== */

window.initBarberSettingsPage = async function () {

    const container = document.getElementById("settingsContainer");

    if (!container) {
        return;
    }

    /*
     * If the settings page already exists,
     * don't rebuild it.
     */
    if ( settingsPageInitialized && container.querySelector("#username") ) {
        /*
         * Still refresh the user information whenever
         * Settings is opened.
         */
        await loadBarberSettings();
        return;
    }

    settingsPageInitialized = true;

    container.innerHTML = `

        <!-- ==================================================
             ACCOUNT SETTINGS
        =================================================== -->

        <div class="settings-card account-settings-card">

            <div class="settings-card-header">

                <div>

                    <h3>Account Settings</h3>

                    <p class="settings-description">
                        Manage your account information and security.
                    </p>

                </div>

            </div>


            <!-- ==================================================
                 USER DETAILS
            =================================================== -->

            <div class="account-subsection">

                <div class="account-subsection-header">

                    <div>

                        <h4>User Details</h4>

                        <p>
                            Update your username, phone number,
                            email and profile image.
                        </p>

                    </div>

                    <button type="button" class="gold-btn settings-edit-btn"
                        id="editUserDetailsBtn">

                        <i class="fas fa-pen"></i>
                        Edit

                    </button>

                </div>


                <div class="user-profile-layout">

                    <!-- Profile Image -->

                    <div class="profile-image-section">

                        <div class="profile-avatar" id="profileAvatar">

                            <i class="fas fa-user"></i>

                        </div>


                        <label for="profileImage" class="profile-image-label">

                            <i class="fas fa-camera"></i>
                            Change Photo

                        </label>

                        <input id="profileImage" type="file" accept="image/*" disabled hidden>

                    </div>


                    <!-- User Details -->

                    <div class="user-details-form">

                        <div class="settings-form">

                            <div class="settings-field-row">

                                <div class="settings-field">

                                    <label for="username"> Username </label>

                                    <input id="username" type="text" placeholder="Username"
                                        disabled>

                                </div>


                                <div class="settings-field">

                                    <label for="phoneNumber"> Phone Number </label>

                                    <input id="phoneNumber" type="text" placeholder="Phone number"
                                        disabled>

                                </div>

                            </div>


                            <div class="settings-field email-field">

                                <label for="email"> Email Address </label>

                                <input id="email" type="email" placeholder="Email address"
                                    disabled>

                            </div>

                        </div>

                    </div>

                </div>


                <div class="settings-actions">

                    <button type="button" class="gold-btn hidden" id="saveUserDetailsBtn">

                        <i class="fas fa-save"></i>
                        Save Changes

                    </button>


                    <button type="button" class="settings-cancel-btn hidden"
                        id="cancelUserDetailsBtn">

                        Cancel

                    </button>

                </div>

            </div>


            <!-- ==================================================
                 PASSWORD MANAGEMENT
            =================================================== -->

            <div class="account-subsection password-subsection">

                <div class="account-subsection-header">

                    <div>

                        <h4>Password & Security</h4>

                        <p> Keep your account secure by changing
                            your password regularly.
                        </p>

                    </div>

                    <button type="button" class="gold-btn" id="changePasswordBtn">

                        <i class="fas fa-lock"></i>
                        Change Password

                    </button>

                </div>

            </div>

        </div>


        <!-- ==================================================
             CHANGE PASSWORD MODAL
        =================================================== -->

        <div id="changePasswordModal" class="password-modal" style="display:none;">

            <div class="password-modal-content">

                <h3>Change Password</h3>


                <label for="currentPassword"> Current Password </label>

                <input id="currentPassword" type="password" autocomplete="current-password"
                    placeholder="Enter current password">


                <label for="newPassword"> New Password </label>

                <input id="newPassword" type="password" autocomplete="new-password"
                    placeholder="Enter new password">


                <label for="confirmNewPassword"> Confirm New Password </label>

                <input id="confirmNewPassword" type="password" autocomplete="new-password"
                    placeholder="Confirm new password">


                <div class="password-modal-actions">

                    <button type="button" class="gold-btn" id="savePasswordBtn">

                        Change Password

                    </button>


                    <button type="button" class="gold-btn" id="cancelPasswordBtn">

                        Cancel

                    </button>

                </div>

            </div>

        </div>

    `;


    /*
     * Initial state:
     *
     * Fields contain user information but remain
     * completely uneditable.
     */

    setFieldsDisabled(
        [ "username", "phoneNumber", "email", "profileImage" ],
        true
    );


    toggleHidden( "saveUserDetailsBtn", true );

    toggleHidden( "cancelUserDetailsBtn", true );

    toggleHidden( "editUserDetailsBtn", false );


    /* ======================================================
       EVENT HANDLERS
    ====================================================== */

    const editUserButton = document.getElementById("editUserDetailsBtn");

    const saveUserButton = document.getElementById("saveUserDetailsBtn");

    const cancelUserButton = document.getElementById("cancelUserDetailsBtn");


    if (editUserButton) {
        editUserButton.onclick = enableUserDetailsEditing;
    }


    if (saveUserButton) {
        saveUserButton.onclick = saveUserDetails;
    }


    if (cancelUserButton) {
        cancelUserButton.onclick = cancelUserDetailsEditing;
    }


    /* ======================================================
       PROFILE IMAGE
    ====================================================== */

    const profileAvatar = document.getElementById("profileAvatar");

    const profileImage = document.getElementById("profileImage");

    if (profileAvatar && profileImage) {

        profileAvatar.onclick = function () {

            if (!profileImage.disabled) {
                profileImage.click();
            }

        };

        profileImage.onchange = handleProfileImagePreview;

    }


    /* ======================================================
       PASSWORD
    ====================================================== */

    const passwordButton =
        document.getElementById("changePasswordBtn");

    if (passwordButton) {
        passwordButton.onclick = openPasswordModal;
    }

    const savePasswordButton = document.getElementById("savePasswordBtn");

    if (savePasswordButton) {
        savePasswordButton.onclick = changePassword;
    }

    const cancelPasswordButton = document.getElementById("cancelPasswordBtn");

    if (cancelPasswordButton) {
        cancelPasswordButton.onclick = closePasswordModal;
    }


    /*
     * IMPORTANT:
     *
     * Load the barber's actual user information
     * after the settings UI has been created.
     */
    await loadBarberSettings();

};


/* ==========================================================
   LOAD BARBER SETTINGS
========================================================== */

window.loadBarberSettings = async function () {

    try {

        /*
         * loadBarberUser() is now the source of the
         * barber's user details.
         */
        const data = await apiRequest("/staffs/staff/me/");


        if (!data) {
            return;
        }

        const username = document.getElementById("username");

        const phoneNumber = document.getElementById("phoneNumber");

        const email = document.getElementById("email");


        /*
         * USERNAME
         *
         * Support the different names your backend
         * may currently return.
         */
        const usernameValue = data.username || data.name || data.full_name || "";


        /*
         * PHONE
         */
        const phoneValue = data.phone_number || data.phoneNumber || data.phone || "";


        /*
         * EMAIL
         */
        const emailValue = data.email || "";


        if (username) {
            username.value = usernameValue;
        }


        if (phoneNumber) {
            phoneNumber.value = phoneValue;
        }


        if (email) {
            email.value = emailValue;
        }


        /*
         * PROFILE IMAGE
         */
        const profileImageUrl = data.image || data.profile_image ||
                                data.profileImage || data.avatar || "";


        if (profileImageUrl) {

            setProfileAvatar( profileImageUrl );

        } else {

            resetProfileAvatar();

        }


        /*
         * Save the current values so Cancel
         * can restore them.
         */
        userDetailsSnapshot = {

            username: usernameValue,

            phone_number: phoneValue,

            email: emailValue,

            profile_image: profileImageUrl

        };

    }

    catch (error) {

        console.error( "Unable to load barber settings:", error );

    }

};


/* ==========================================================
   USER DETAILS EDITING
========================================================== */

function enableUserDetailsEditing() {

    setFieldsDisabled(
        [ "username", "phoneNumber", "email", "profileImage" ],
        false
    );

    toggleHidden( "saveUserDetailsBtn", false );

    toggleHidden( "cancelUserDetailsBtn", false  );

    toggleHidden( "editUserDetailsBtn", true );

}


/* ==========================================================
   CANCEL USER DETAILS EDITING
========================================================== */

function cancelUserDetailsEditing() {

    if (userDetailsSnapshot) {

        const username = document.getElementById("username");

        const phoneNumber = document.getElementById("phoneNumber");

        const email = document.getElementById("email");


        if (username) {
            username.value = userDetailsSnapshot.username;
        }

        if (phoneNumber) {
            phoneNumber.value = userDetailsSnapshot.phone_number;
        }


        if (email) {
            email.value = userDetailsSnapshot.email;
        }


        if (userDetailsSnapshot.profile_image) {

            setProfileAvatar( userDetailsSnapshot.profile_image );

        } else {

            resetProfileAvatar();

        }

    }

    const profileImage = document.getElementById("profileImage");

    if (profileImage) {
        profileImage.value = "";
    }


    setFieldsDisabled(
        [ "username", "phoneNumber", "email", "profileImage" ],
        true
    );


    toggleHidden( "saveUserDetailsBtn", true  );


    toggleHidden(  "cancelUserDetailsBtn", true );


    toggleHidden( "editUserDetailsBtn", false );

}


/* ==========================================================
   PROFILE IMAGE PREVIEW
========================================================== */

function handleProfileImagePreview(event) {

    const file = event.target.files?.[0];


    if (!file) {
        return;
    }


    if (!file.type.startsWith("image/")) {

        alert( "Please select a valid image." );

        event.target.value = "";

        return;

    }

    const MAX_PROFILE_IMAGE_SIZE = 5 * 1024 * 1024;


    if (file.size > MAX_PROFILE_IMAGE_SIZE) {

        alert(  "Profile image must be smaller than 5 MB." );

        event.target.value = "";

        return;

    }

    const reader = new FileReader();

    reader.onload = function (event) {

        if (event.target?.result) {

            setProfileAvatar( event.target.result );

        }

    };


    reader.onerror = function () {

        alert( "Unable to preview the selected image." );

        event.target.value = "";

    };

    reader.readAsDataURL(file);

}


/* ==========================================================
   SET PROFILE AVATAR
========================================================== */

function setProfileAvatar(source) {

    const avatar = document.getElementById("profileAvatar");

    if (!avatar || !source) {
        return;
    }

    avatar.innerHTML = "";

    const image = document.createElement("img");

    image.src = source;

    image.alt = "Profile image";

    image.onerror = function () {

        avatar.innerHTML = '<i class="fas fa-user"></i>';

    };

    avatar.appendChild(image);

}


/* ==========================================================
   RESET PROFILE AVATAR
========================================================== */

function resetProfileAvatar() {

    const avatar = document.getElementById("profileAvatar");

    if (!avatar) {
        return;
    }

    avatar.innerHTML = '<i class="fas fa-user"></i>';

}


/* ==========================================================
   SAVE USER DETAILS
========================================================== */

async function saveUserDetails() {

    const usernameElement = document.getElementById("username");

    const phoneElement = document.getElementById("phoneNumber");

    const emailElement = document.getElementById("email");

    const profileImage = document.getElementById("profileImage");


    if (!usernameElement || !emailElement) {
        return;
    }


    const username = usernameElement.value.trim();

    const phoneNumber = phoneElement?.value.trim() || "";

    const email = emailElement.value.trim();

    if (!username) {

        alert( "Username is required." );

        usernameElement.focus();

        return;

    }

    if (!email) {

        alert( "Email address is required." );

        emailElement.focus();

        return;

    }


    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {

        alert( "Please enter a valid email address." );

        emailElement.focus();

        return;

    }

    const formData = new FormData();

    formData.append( "username", username );

    formData.append( "phone_number", phoneNumber );

    formData.append(  "email", email );

    if ( profileImage && profileImage.files && profileImage.files.length > 0 ) {

        formData.append( "profile_image", profileImage.files[0] );

    }

    try {

        await apiRequest( "/staffs/self/details-update/",  "PATCH", formData );

        /*
         * Reload the user information from the backend.
         */
        await loadBarberSettings();

        cancelUserDetailsEditing();

        alert( "User details saved successfully." );

    }

    catch (error) {

        console.error(
            "Unable to save user details:",
            error
        );

        alert(
            getApiErrorMessage( error, "Unable to save user details." )
        );

    }

}


/* ==========================================================
   PASSWORD MODAL
========================================================== */

function openPasswordModal() {

    const modal = document.getElementById( "changePasswordModal" );

    if (!modal) {
        return;
    }

    modal.style.display = "flex";

    const currentPassword = document.getElementById( "currentPassword" );

    if (currentPassword) {
        currentPassword.focus();
    }

}


function closePasswordModal() {

    const modal = document.getElementById( "changePasswordModal"  );

    if (!modal) {
        return;
    }

    modal.style.display = "none";

    clearPasswordFields();

}


/* ==========================================================
   CLEAR PASSWORD FIELDS
========================================================== */

function clearPasswordFields() {

    const currentPassword = document.getElementById( "currentPassword" );

    const newPassword = document.getElementById( "newPassword" );

    const confirmNewPassword = document.getElementById( "confirmNewPassword" );


    if (currentPassword) {
        currentPassword.value = "";
    }


    if (newPassword) {
        newPassword.value = "";
    }


    if (confirmNewPassword) {
        confirmNewPassword.value = "";
    }

}


/* ==========================================================
   CHANGE PASSWORD
========================================================== */

async function changePassword() {

    const currentPasswordElement = document.getElementById( "currentPassword" );

    const newPasswordElement = document.getElementById( "newPassword" );

    const confirmNewPasswordElement = document.getElementById( "confirmNewPassword" );


    if ( !currentPasswordElement || !newPasswordElement || !confirmNewPasswordElement ) {
        return;
    }


    const currentPassword =  currentPasswordElement.value;

    const newPassword = newPasswordElement.value;

    const confirmNewPassword = confirmNewPasswordElement.value;


    if (!currentPassword) {

        alert( "Current password is required." );

        currentPasswordElement.focus();

        return;

    }


    if (!newPassword) {

        alert( "New password is required." );

        newPasswordElement.focus();

        return;

    }


    if (!confirmNewPassword) {

        alert( "Please confirm your new password." );

        confirmNewPasswordElement.focus();

        return;

    }


    if ( newPassword !== confirmNewPassword ) {

        alert( "New passwords don't match." );

        confirmNewPasswordElement.focus();

        return;

    }


    if ( currentPassword === newPassword  ) {

        alert(  "Your new password must be different from your current password." );

        newPasswordElement.focus();

        return;

    }

    if (newPassword.length < 8) {

        alert( "New password must be at least 8 characters long." );

        newPasswordElement.focus();

        return;

    }

    try {

        await apiRequest( "/staffs/self/password-update/", "PATCH",
            {
                current_password: currentPassword,

                password: newPassword,

                password2: confirmNewPassword
            }
        );


        alert( "Password changed successfully." );

        closePasswordModal();

    }

    catch (error) {

        console.error(  "Unable to change password:", error );


        alert(
            getApiErrorMessage(
                error,
                "Unable to change password. Please check your current password and try again."
            )
        );

    }

}


/* ==========================================================
   API ERROR MESSAGE
========================================================== */

function getApiErrorMessage(error, fallback) {

    if (!error) {
        return fallback;
    }


    if (typeof error === "string") {
        return error;
    }


    if (error.message) {
        return error.message;
    }


    if (error.response?.data) {

        const data = error.response.data;


        if (typeof data === "string") {
            return data;
        }


        if (data.detail) {
            return String(data.detail);
        }


        if (data.message) {
            return String(data.message);
        }


        if (typeof data === "object") {

            const messages = [];

            Object.keys(data).forEach( function (key) {

                    const value = data[key];

                    if (Array.isArray(value)) {

                        messages.push( `${key}: ${value.join(", ")}` );

                    }

                    else if ( value !== undefined && value !== null  ) {

                        messages.push( `${key}: ${String(value)}`  );

                    }

                }
            );

            if (messages.length) {
                return messages.join("\n");
            }

        }

    }


    return fallback;

}


/* ==========================================================
   GENERIC HELPERS
========================================================== */

function setFieldsDisabled(ids, disabled) {

    ids.forEach(function (id) {

        const element = document.getElementById(id);

        if (element) {
            element.disabled = disabled;
        }

    });

}


function toggleHidden(id, hidden) {

    const element = document.getElementById(id);


    if (!element) {
        return;
    }


    element.classList.toggle( "hidden", hidden );

}


/* ==========================================================
   MODAL OUTSIDE CLICK
========================================================== */

document.addEventListener(
    "click", function (event) {

        const modal = document.getElementById( "changePasswordModal" );


        if (!modal) {
            return;
        }


        if ( event.target === modal &&  modal.style.display === "flex" ) {

            closePasswordModal();

        }

    }
);


/* ==========================================================
   ESCAPE KEY
========================================================== */

document.addEventListener( "keydown",
    function (event) {

        if (event.key !== "Escape") {
            return;
        }


        const modal = document.getElementById( "changePasswordModal" );


        if ( modal && modal.style.display === "flex" ) {

            closePasswordModal();

        }

    }
);
