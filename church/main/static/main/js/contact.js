document.addEventListener("DOMContentLoaded", async () => {
    const r = await fetch("/api/contacts/");
    const data = await r.json();

    document.getElementById("contact-address").innerHTML = data.address.replace(/\n/g,"<br>");
    document.getElementById("contact-phone").innerHTML   = data.phone.replace(/\n/g,"<br>");
    document.getElementById("contact-email").textContent = data.email;
    document.getElementById("contact-work-time").textContent = data.work_hours;

    const map = document.getElementById("contact-map");
    map.setAttribute("src", data.map_url);
});