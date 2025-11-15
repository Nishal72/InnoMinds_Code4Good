let map;
let allMarkers = [];

function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 11,
        center: { lat: -20.348404, lng: 57.552152 },
    });

    businesses.forEach(business => {
        addMarker(business);
    });

    // Hook category filter
    const categorySelect = document.getElementById("categoryFilter");
    if (categorySelect) {
        categorySelect.addEventListener("change", function () {
            filterMarkers(this.value);
        });
    }
}

function addMarker(business) {
    const marker = new google.maps.Marker({
        position: { lat: business.latitude, lng: business.longitude },
        map: map,
        title: business.name,
        icon: createMarkerIcon(business.name),
        category: business.category // add category data to marker
    });

    marker.addListener("click", () => {
        if (business.detail_url) {
            window.location.href = business.detail_url;
        }
    });

    allMarkers.push(marker);
}

function filterMarkers(category) {
    allMarkers.forEach(marker => {
        if (category === "all" || marker.category === category) {
            marker.setMap(map);// Show marker
        } else {
            marker.setMap(null);// Hide marker
        }
    });
}
