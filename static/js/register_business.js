let regMap;
let regMarker = null;

function initRegisterMap() {
    const center = { lat: INITIAL_LAT, lng: INITIAL_LNG };

    regMap = new google.maps.Map(document.getElementById("register-map"), {
        zoom: 11,
        center: center,
    });

    regMap.addListener("click", (e) => {
        placeMarker({
            lat: e.latLng.lat(),
            lng: e.latLng.lng()
        });
    });
}

function placeMarker(position) {
    if (regMarker === null) {
        regMarker = new google.maps.Marker({
            position: position,
            map: regMap,
            draggable: true,
        });

        regMarker.addListener("dragend", () => {
            const pos = regMarker.getPosition();
            updateLatLngInputs(pos.lat(), pos.lng());
        });
    } else {
        regMarker.setPosition(position);
    }

    updateLatLngInputs(position.lat, position.lng);

    regMap.setCenter(position);
    regMap.setZoom(15);
}

function updateLatLngInputs(lat, lng) {
    const latInput = document.getElementById("id_latitude");
    const lngInput = document.getElementById("id_longitude");

    if (latInput && lngInput) {
        latInput.value = lat.toFixed(6);
        lngInput.value = lng.toFixed(6);
    }
}

function useMyLocation() {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            placeMarker({
                lat: position.coords.latitude,
                lng: position.coords.longitude,
            });
        },
        () => {
            alert("Unable to retrieve your location.");
        }
    );
}
