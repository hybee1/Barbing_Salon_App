/* ==========================================================
   SETTINGS MANAGEMENT
   Levelz Cuts
========================================================== */

let settingsPageInitialized = false;

let salonSettingsSnapshot = null;
let bookingSettingsSnapshot = null;
let userDetailsSnapshot = null;


/* ==========================================================
   INITIALIZE SETTINGS PAGE
========================================================== */

window.initSettingsPage = function () {

    const container = document.getElementById("settingsContainer");

    if (!container) {
        return;
    }

    /*
     * If the page has already been initialized and the
     * container still contains the settings UI, don't rebuild it.
     */
    if ( settingsPageInitialized && container.querySelector("#salonName") ) {
        return;
    }

    settingsPageInitialized = true;

    container.innerHTML = `

        <div class="settings-grid">

            <!-- ==================================================
                 1. SALON INFORMATION
            =================================================== -->

            <div class="settings-card salon-settings-card">

                <div class="settings-card-header">

                    <div>
                        <h3>Salon Information</h3>

                        <p class="settings-description">
                            Manage your salon's basic information.
                        </p>
                    </div>

                    <button type="button" class="gold-btn settings-edit-btn"
                        id="editSalonInfoBtn">

                        <i class="fas fa-pen"></i>
                        Edit

                    </button>

                </div>


                <div class="settings-form">

                    <div class="settings-field">

                        <label for="salonName"> Salon Name </label>

                        <input id="salonName" type="text" placeholder="Levelz Cuts"
                            disabled>

                    </div>


                    <div class="settings-field">

                        <label for="salonPhone"> Phone Number </label>

                        <input id="salonPhone" type="text" placeholder="Phone number"
                            disabled>

                    </div>


                    <div class="settings-field">

                        <label for="salonCountry"> Country </label>

                        <input id="salonCountry" type="text" placeholder="Nigeria"
                            disabled>

                    </div>


                    <div class="settings-field settings-field-full">

                        <label for="salonAddress"> Address </label>

                        <textarea id="salonAddress" placeholder="Salon address"
                            disabled></textarea>

                    </div>

                </div>


                <div class="settings-actions">

                    <button type="button" class="gold-btn hidden" id="saveSalonInfoBtn">

                        <i class="fas fa-save"></i>
                        Save Changes

                    </button>

                    <button type="button" class="danger-btn hidden" id="cancelSalonInfoBtn">

                        Cancel

                    </button>

                </div>

            </div>


            <!-- ==================================================
                 2. BOOKING SETTINGS
            =================================================== -->

            <div class="settings-card booking-settings-card">

                <div class="settings-card-header">

                    <div>

                        <h3>Booking Settings</h3>

                        <p class="settings-description">
                            Configure how customers can make bookings.
                        </p>

                    </div>

                    <button type="button" class="gold-btn settings-edit-btn"
                        id="editBookingSettingsBtn">

                        <i class="fas fa-pen"></i>
                        Edit

                    </button>

                </div>


                <div class="settings-form settings-booking-form">

                    <div class="settings-field">

                        <label for="bookingBuffer"> Booking Duration Buffer </label>

                        <select id="bookingBuffer" disabled>

                            <option value="0"> No Buffer </option>

                            <option value="5"> 5 Minutes </option>

                            <option value="10"> 10 Minutes </option>

                            <option value="15"> 15 Minutes </option>

                        </select>

                    </div>


                    <div class="settings-field">

                        <label for="onlineBooking"> Allow Online Booking </label>

                        <select id="onlineBooking" disabled>

                            <option value="true"> Enabled </option>

                            <option value="false"> Disabled </option>

                        </select>

                    </div>

                </div>


                <div class="settings-actions">

                    <button type="button" class="gold-btn hidden" id="saveBookingSettingsBtn">

                        <i class="fas fa-save"></i>
                        Save Changes

                    </button>

                    <button type="button" class="danger-btn hidden"
                        id="cancelBookingSettingsBtn">

                        Cancel

                    </button>

                </div>

            </div>


            <!-- ==================================================
                 3. ACCOUNT SETTINGS
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

                            <p> Update your username, phone number, email and profile image. </p>

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

                            <input id="profileImage" type="file" accept="image/*" disabled
                                hidden>

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

                                        <input id="phoneNumber" type="text"
                                            placeholder="Phone number"
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

                        <button type="button" class="danger-btn hidden"
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

                            <p>
                                Keep your account secure by changing
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

        </div>


        <!-- ==================================================
             CHANGE PASSWORD MODAL
        =================================================== -->

        <div id="changePasswordModal" class="password-modal" style="display:none;">

            <div class="password-modal-content">

                <h3> Change Password </h3>

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


    /* ==========================================================
       EVENT LISTENERS
    ========================================================== */

    const editSalonButton = document.getElementById("editSalonInfoBtn");

    const saveSalonButton = document.getElementById("saveSalonInfoBtn");

    const cancelSalonButton = document.getElementById("cancelSalonInfoBtn");


    if (editSalonButton) {
        editSalonButton.onclick = enableSalonEditing;
    }

    if (saveSalonButton) {
        saveSalonButton.onclick = saveSalonInfo;
    }

    if (cancelSalonButton) {
        cancelSalonButton.onclick = cancelSalonEditing;
    }


    /* ----------------------------------------------------------
       Booking Settings
    ---------------------------------------------------------- */

    const editBookingButton = document.getElementById("editBookingSettingsBtn");

    const saveBookingButton = document.getElementById("saveBookingSettingsBtn");

    const cancelBookingButton = document.getElementById("cancelBookingSettingsBtn");


    if (editBookingButton) {
        editBookingButton.onclick = enableBookingEditing;
    }

    if (saveBookingButton) {
        saveBookingButton.onclick = saveBookingSettings;
    }

    if (cancelBookingButton) {
        cancelBookingButton.onclick = cancelBookingEditing;
    }


    /* ----------------------------------------------------------
       User Details
    ---------------------------------------------------------- */

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


    /* ----------------------------------------------------------
       Profile Image
    ---------------------------------------------------------- */

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


    /* ----------------------------------------------------------
       Password
    ---------------------------------------------------------- */

    const passwordButton = document.getElementById("changePasswordBtn");

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


    /* ----------------------------------------------------------
       Load Settings
    ---------------------------------------------------------- */

    loadSettings();

};


/* ==========================================================
   LOAD SETTINGS
========================================================== */

window.loadSettings = async function () {

    try {

        const [settings, user] = await Promise.all([

            apiRequest("/settings/salon-config-info/"),

            apiRequest("/staffs/staff/me/")

        ]);


        if (!settings) {
            return;
        }


        /* ======================================================
           SALON INFORMATION
        ====================================================== */

        const salonName = document.getElementById("salonName");

        const salonPhone = document.getElementById("salonPhone");

        const salonCountry = document.getElementById("salonCountry");

        const salonAddress = document.getElementById("salonAddress");


        if (salonName) {

            salonName.value = settings.salon_info?.salon_name || "";

        }

        if (salonPhone) {

            salonPhone.value = settings.salon_info?.salon_phone_number || "";

        }

        if (salonCountry) {

            salonCountry.value = settings.salon_info?.country || "";

        }

        if (salonAddress) {

            salonAddress.value = settings.salon_info?.salon_address || "";

        }

        salonSettingsSnapshot = {

            name: salonName?.value || "",

            phone: salonPhone?.value || "",

            country: salonCountry?.value || "",

            address: salonAddress?.value || ""

        };


        /* ======================================================
           BOOKING SETTINGS
        ====================================================== */

        const bookingBuffer = document.getElementById("bookingBuffer");

        const onlineBooking = document.getElementById("onlineBooking");


        if (bookingBuffer) {

            bookingBuffer.value =
                String( settings.salon_booking_buffer ?.booking_duration_buffer ?? 0 );

        }

        if (onlineBooking) {

            onlineBooking.value =
                String( settings.salon_booking_buffer ?.allow_online_booking ?? true );

        }

        bookingSettingsSnapshot = {

            booking_buffer: bookingBuffer?.value || "0",

            online_booking: onlineBooking?.value || "true"

        };


        /* ======================================================
           ACCOUNT SETTINGS
           USER DETAILS
        ====================================================== */

        const username = document.getElementById("username");

        const phoneNumber = document.getElementById("phoneNumber");

        const email = document.getElementById("email");

        if (username) {

            username.value = user?.username || user?.name || user?.full_name || "";

        }

        if (phoneNumber) {

            phoneNumber.value = user?.phone_number || user?.phoneNumber || user?.phone || "";

        }

        if (email) {

            email.value = user?.email || "";

        }


        /* ======================================================
           PROFILE IMAGE
        ====================================================== */

        const profileImageUrl = user?.image ||  user?.profile_image ||
                        user?.profileImage || user?.avatar ||  "";


        if (profileImageUrl) {

            setProfileAvatar(profileImageUrl);

        }

        else {

            resetProfileAvatar();

        }


        /* ======================================================
           USER DETAILS SNAPSHOT
        ====================================================== */

        userDetailsSnapshot = {

            username: username?.value || "",

            phone_number: phoneNumber?.value || "",

            email: email?.value || "",

            profile_image: profileImageUrl || ""

        };

    }

    catch (error) {

        console.error( "Unable to load settings:", error );

    }

};



/* ==========================================================
   resetProfileAvatar
========================================================== */
function resetProfileAvatar() {

    const avatar = document.getElementById("profileAvatar");

    if (!avatar) {
        return;
    }

    avatar.innerHTML = '<i class="fas fa-user"></i>';

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
   SALON INFORMATION EDITING
========================================================== */

function enableSalonEditing() {

    setFieldsDisabled(

        [ "salonName",  "salonPhone", "salonCountry", "salonAddress" ],

        false

    );


    toggleHidden( "saveSalonInfoBtn", false );


    toggleHidden( "cancelSalonInfoBtn", false );


    toggleHidden( "editSalonInfoBtn", true );

    document.getElementById("salonName") ?.focus();

}


function cancelSalonEditing() {

    if (salonSettingsSnapshot) {

        const salonName = document.getElementById("salonName");

        const salonPhone = document.getElementById("salonPhone");

        const salonCountry = document.getElementById("salonCountry");

        const salonAddress = document.getElementById("salonAddress");


        if (salonName) {
            salonName.value = salonSettingsSnapshot.name;
        }

        if (salonPhone) {
            salonPhone.value = salonSettingsSnapshot.phone;
        }

        if (salonCountry) {
            salonCountry.value = salonSettingsSnapshot.country;
        }

        if (salonAddress) {
            salonAddress.value = salonSettingsSnapshot.address;
        }

    }

    setFieldsDisabled(

        [  "salonName", "salonPhone", "salonCountry", "salonAddress" ],

        true

    );

    toggleHidden( "saveSalonInfoBtn", true );

    toggleHidden( "cancelSalonInfoBtn", true );

    toggleHidden( "editSalonInfoBtn", false );

}


/* ==========================================================
   SAVE SALON INFORMATION
========================================================== */

async function saveSalonInfo() {

    const salonName = document.getElementById("salonName");

    const salonPhone = document.getElementById("salonPhone");

    const salonCountry = document.getElementById("salonCountry");

    const salonAddress = document.getElementById("salonAddress");


    if (!salonName) {
        return;
    }


    const data = {

        name: salonName.value.trim(),

        phone: salonPhone?.value.trim() || "",

        country: salonCountry?.value.trim() || "",

        address: salonAddress?.value.trim() || ""

    };


    if (!data.name) {

        alert( "Salon name is required." );

        salonName.focus();

        return;

    }


    try {

        await apiRequest( "/settings/salon-info/", "POST",  data );

        salonSettingsSnapshot = { ...data };

        alert( "Salon information saved successfully." );

        cancelSalonEditing();

    }

    catch (error) {

        console.error( "Unable to save salon information:", error );

        alert( "Unable to save salon information." );

    }

}


/* ==========================================================
   BOOKING SETTINGS EDITING
========================================================== */

function enableBookingEditing() {

    setFieldsDisabled(

        [ "bookingBuffer", "onlineBooking" ],

        false

    );


    toggleHidden( "saveBookingSettingsBtn", false );

    toggleHidden( "cancelBookingSettingsBtn", false );

    toggleHidden( "editBookingSettingsBtn", true );

}


function cancelBookingEditing() {

    if (bookingSettingsSnapshot) {

        const bookingBuffer = document.getElementById("bookingBuffer");

        const onlineBooking = document.getElementById("onlineBooking");

        if (bookingBuffer) {

            bookingBuffer.value = bookingSettingsSnapshot.booking_buffer;

        }


        if (onlineBooking) {

            onlineBooking.value = bookingSettingsSnapshot.online_booking;

        }

    }

    setFieldsDisabled( [ "bookingBuffer", "onlineBooking" ], true );


    toggleHidden( "saveBookingSettingsBtn", true );

    toggleHidden( "cancelBookingSettingsBtn", true );

    toggleHidden( "editBookingSettingsBtn", false );

}


/* ==========================================================
   SAVE BOOKING SETTINGS
========================================================== */

async function saveBookingSettings() {

    const bookingBuffer = document.getElementById("bookingBuffer");

    const onlineBooking = document.getElementById("onlineBooking");

    if (!bookingBuffer || !onlineBooking) {
        return;
    }

    const data = {

        booking_buffer: bookingBuffer.value,

        online_booking: onlineBooking.value === "true"

    };

    try {

        await apiRequest( "/settings/salon-booking-buffer/", "POST", data );

        bookingSettingsSnapshot = {

            booking_buffer: String(data.booking_buffer),

            online_booking: String(data.online_booking)

        };


        /*
         * Keep the UI consistent with the value saved by
         * the backend.
         */
        onlineBooking.value = String(data.online_booking);


        alert( "Booking settings saved successfully." );

        cancelBookingEditing();

    }

    catch (error) {

        console.error( "Unable to save booking settings:", error );

        alert( "Unable to save booking settings." );

    }

}


/* ==========================================================
   USER DETAILS EDITING
========================================================== */

function enableUserDetailsEditing() {

    setFieldsDisabled(

        [ "username", "phoneNumber", "email", "profileImage" ],

        false

    );


    toggleHidden( "saveUserDetailsBtn", false );

    toggleHidden( "cancelUserDetailsBtn", false );

    toggleHidden( "editUserDetailsBtn", true );

}


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


        /* --------------------------------------------------
           Restore previous profile image
        -------------------------------------------------- */

        if (userDetailsSnapshot.profile_image) {

            setProfileAvatar( userDetailsSnapshot.profile_image );

        }

        else {

            resetProfileAvatar();

        }

    }


    /* ------------------------------------------------------
       Reset selected file
    ------------------------------------------------------ */

    const profileImage = document.getElementById("profileImage");

    if (profileImage) {

        profileImage.value = "";

    }


    /* ------------------------------------------------------
       Disable editing
    ------------------------------------------------------ */

    setFieldsDisabled(

        [ "username", "phoneNumber", "email", "profileImage" ],

        true

    );


    toggleHidden( "saveUserDetailsBtn", true );


    toggleHidden( "cancelUserDetailsBtn", true );

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

        alert( "Profile image must be smaller than 5 MB." );

        event.target.value = "";

        return;

    }


    const reader = new FileReader();

    reader.onload = function (e) {

        if (e.target?.result) {

            setProfileAvatar( e.target.result );

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


    /*
     * Avoid directly injecting an arbitrary URL into innerHTML.
     * This also makes the function safer when the image URL
     * comes from the API.
     */

    avatar.innerHTML = "";


    const image =
        document.createElement("img");


    image.src = source;
    image.alt = "Profile image";


    image.onerror = function () {

        avatar.innerHTML =
            '<i class="fas fa-user"></i>';

    };


    avatar.appendChild(image);

}


/* ==========================================================
   SAVE USER DETAILS
========================================================== */

async function saveUserDetails() {

    const usernameElement = document.getElementById("username");

    const phoneElement = document.getElementById("phoneNumber");

    const emailElement = document.getElementById("email");

    const profileImage = document.getElementById("profileImage");


    if ( !usernameElement || !emailElement ) {
        return;
    }

    const username = usernameElement.value.trim();

    const phoneNumber = phoneElement?.value.trim() || "";

    const email = emailElement.value.trim();


    /* ----------------------------------------------------------
       Frontend validation
    ---------------------------------------------------------- */

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


    /*
     * Basic email validation.
     */
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


    if (!emailPattern.test(email)) {

        alert( "Please enter a valid email address." );

        emailElement.focus();

        return;

    }


    /*
     * FormData is required because this request may contain
     * both text fields and a profile image.
     */
    const formData = new FormData();


    formData.append( "username", username );


    formData.append( "phone_number", phoneNumber );


    formData.append( "email", email );


    if ( profileImage && profileImage.files && profileImage.files.length > 0 ) {

        formData.append( "profile_image", profileImage.files[0] );

    }

    try {

        await apiRequest( "/staffs/self/details-update/", "PATCH", formData );

        /*
         * Reload the settings so that the avatar and any values
         * returned by the backend are immediately reflected.
         */
        await loadSettings();

        cancelUserDetailsEditing();

        alert( "User details saved successfully." );

    }


    catch (error) {

        console.error( "Unable to save user details:", error );

        alert( getApiErrorMessage( error, "Unable to save user details." ) );

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

    const modal = document.getElementById( "changePasswordModal" );

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

    const currentPasswordElement = document.getElementById("currentPassword");

    const newPasswordElement = document.getElementById( "newPassword" );

    const confirmNewPasswordElement = document.getElementById( "confirmNewPassword" );


    if ( !currentPasswordElement || !newPasswordElement || !confirmNewPasswordElement ) {
        return;
    }

    const currentPassword = currentPasswordElement.value;

    const newPassword = newPasswordElement.value;

    const confirmNewPassword = confirmNewPasswordElement.value;


    /* ----------------------------------------------------------
       Frontend validation
    ---------------------------------------------------------- */

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


    if (newPassword !== confirmNewPassword) {

        alert( "New passwords don't match." );

        confirmNewPasswordElement.focus();

        return;

    }


    if (currentPassword === newPassword) {

        alert( "Your new password must be different from your current password." );

        newPasswordElement.focus();

        return;

    }


    /*
     * Prevent accidentally submitting an extremely short password.
     * The backend should still perform the authoritative validation.
     */
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

        console.error( "Unable to change password:", error );

        alert(
            getApiErrorMessage(
                error,
                "Unable to change password. Please check your current password and try again."
            )
        );

    }

}


/* ==========================================================
   API ERROR MESSAGE HELPER
========================================================== */

function getApiErrorMessage(error, fallback) {

    if (!error) {
        return fallback;
    }


    /*
     * Handle common apiRequest error formats.
     */

    if (typeof error === "string") {
        return error;
    }


    if (error.message) {

        /*
         * Don't display generic fetch/network errors as the
         * backend validation message unless no better message
         * exists.
         */
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

        /*
         * Django REST Framework-style validation errors.
         */
        if (typeof data === "object") {

            const messages = [];


            Object.keys(data).forEach(function (key) {

                const value = data[key];


                if (Array.isArray(value)) {

                    messages.push(
                        `${key}: ${value.join(", ")}`
                    );

                }

                else if (value !== undefined && value !== null) {

                    messages.push(
                        `${key}: ${String(value)}`
                    );

                }

            });

            if (messages.length) {
                return messages.join("\n");
            }

        }

    }


    return fallback;

}


/* ==========================================================
   OPTIONAL: CLOSE PASSWORD MODAL WHEN CLICKING OUTSIDE
========================================================== */

document.addEventListener(
    "click",
    function (event) {

        const modal = document.getElementById( "changePasswordModal"  );

        if (!modal) {
            return;
        }

        if ( event.target === modal && modal.style.display === "flex" ) {

            closePasswordModal();

        }

    }
);


/* ==========================================================
   OPTIONAL: ESCAPE KEY CLOSES PASSWORD MODAL
========================================================== */

document.addEventListener(
    "keydown",
    function (event) {

        if (event.key !== "Escape") {
            return;
        }

        const modal = document.getElementById( "changePasswordModal" );

        if (  modal && modal.style.display === "flex" ) {

            closePasswordModal();

        }

    }
);
