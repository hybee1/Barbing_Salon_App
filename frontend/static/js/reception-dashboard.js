
const API="/api";

const token=localStorage.getItem("access");

if(!token){

    window.location="/staff/login/";

}

const headers={

    Authorization:`Bearer ${token}`

};


/* ----------------------- */

document
.getElementById("logoutBtn")
.onclick=()=>{

    localStorage.clear();

    location="/staff/login/";

};


/* ----------------------- */

async function loadUser(){

    const res=await fetch(
        `${API}/accounts/me/`,
        {headers}
    );

    if(res.status!==200){

        location="/staff/login/";

        return;

    }

    const user=await res.json();

    userName.textContent=user.full_name;

    avatar.textContent=user.full_name[0];

}


/* ----------------------- */

async function loadDashboard(){

    const res=await fetch(

        `${API}/dashboard/reception/`,

        {headers}

    );

    if(res.status===403){

        location="/staff/login/";

        return;

    }

    const data=await res.json();

    todayBookings.textContent=data.stats.today;

    arrivedBookings.textContent=data.stats.arrived;

    waitingBookings.textContent=data.stats.waiting;

    completedBookings.textContent=data.stats.completed;

    renderBookings(data.bookings);

}


/* ----------------------- */

function renderBookings(bookings){

    bookingTable.innerHTML="";

    bookings.forEach(b=>{

        bookingTable.innerHTML+=`

<tr>

<td>${b.start_time}</td>

<td>${b.customer_name}</td>

<td>${b.service}</td>

<td>${b.staff}</td>

<td>

<span class="badge badge-${badge(b.status)}">

${b.status}

</span>

</td>

<td>

<button
class="gold-btn"
onclick="viewBooking(${b.id})">

View

</button>

</td>

</tr>

`;

    });

}


function badge(status){

    status=status.toLowerCase();

    if(status==="confirmed") return"confirmed";

    if(status==="completed") return"completed";

    if(status==="cancelled") return"cancelled";

    return"progress";

}


/* ----------------------- */

async function viewBooking(id){

    location=`/staff/bookings/${id}/`;

}


/* ----------------------- */

function clock(){

    const now=new Date();

    document.getElementById("clock").innerHTML=`

<strong>

${now.toLocaleTimeString()}

</strong>

<span>

${now.toDateString()}

</span>

`;

}

setInterval(clock,1000);

clock();

loadUser();

loadDashboard();

setInterval(loadDashboard,30000);