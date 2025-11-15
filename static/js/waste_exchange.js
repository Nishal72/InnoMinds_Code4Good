let map;

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 11,
        center: { lat: -20.348404, lng: 57.552152 },
    });

    businesses.forEach(business => {
        addMarker(business);
    });
}

function addMarker(business) {
    const marker = new google.maps.Marker({
        position: { lat: business.latitude, lng: business.longitude },
        map: map,
        title: business.name,
        icon: createMarkerIcon(business.name)
    });

    marker.addListener("click", () => {
    // Go to Django detail page for this business
    if (business.detail_url) {
        window.location.href = business.detail_url;
    }
});

}

function openModal(business) {
    document.getElementById("businessName").innerText = business.name;
    document.getElementById("businessWaste").innerText = business.waste;
    document.getElementById("businessPhone").innerText = business.phone;
    document.getElementById("businessEmail").innerText = business.email;

    if (business.image) {
        document.getElementById("businessImage").src = business.image;
    }

    const modal = new bootstrap.Modal(document.getElementById("businessModal"));
    modal.show();
}
