let regMap;
let regMarker = null;

function initRegisterMap() {
    const center = { lat: INITIAL_LAT, lng: INITIAL_LNG };

    regMap = new google.maps.Map(document.getElementById("register-map"), {
        zoom: 11,
        center: center,
    });

    // On click, place or move marker and update form fields
    regMap.addListener("click", (e) => {
        const clickedPos = e.latLng;

        if (regMarker === null) {
            regMarker = new google.maps.Marker({
                position: clickedPos,
                map: regMap,
                draggable: true,
            });

            // Also allow dragging the marker to fine-tune
            regMarker.addListener("dragend", () => {
                const pos = regMarker.getPosition();
                updateLatLngInputs(pos.lat(), pos.lng());
            });
        } else {
            regMarker.setPosition(clickedPos);
        }

        updateLatLngInputs(clickedPos.lat(), clickedPos.lng());
    });
}

function updateLatLngInputs(lat, lng) {
    const latInput = document.getElementById("id_latitude");
    const lngInput = document.getElementById("id_longitude");

    if (latInput && lngInput) {
        latInput.value = lat.toFixed(6);
        lngInput.value = lng.toFixed(6);
    }
}
