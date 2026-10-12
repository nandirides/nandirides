alert("paymentProcess.js loaded");

(function () {
    "use strict";
    const isEditMode = {% if is_edit %}true{% else %}false{% endif %};
    let rideMap = null;
    let pickupMarker = null;
    let dropMarker = null;
    let routeLayer = null;
    let routeRequestInProgress = false;
    let pickupGeocodeInProgress = false;
    let dropGeocodeInProgress = false;
    let fareRequestInProgress = false;
    let formSubmitting = false;
    let paymentSubmitting = false;
    let updatingPickupAddress = false;
    let updatingDropAddress = false;
    let pickupCityName = "";
    let dropCityName = "";
    let selectedPaymentMethod = "";
    const DEFAULT_CENTER = [20.5937, 78.9629];
    const DEFAULT_ZOOM = 5;
    const form = document.getElementById("rideRequestForm");
    const pickupAddress = document.getElementById("{{ form.pickup_address.id_for_label }}");
    const dropAddress = document.getElementById("{{ form.drop_address.id_for_label }}");
    const pickupLatitude = document.getElementById("{{ form.pickup_latitude.id_for_label }}");
    const pickupLongitude = document.getElementById("{{ form.pickup_longitude.id_for_label }}");
    const dropLatitude = document.getElementById("{{ form.drop_latitude.id_for_label }}");
    const dropLongitude = document.getElementById("{{ form.drop_longitude.id_for_label }}");
    const pickupCityField = document.getElementById("{{ form.pickup_city.id_for_label }}");
    const dropCityField = document.getElementById("{{ form.drop_city.id_for_label }}");
    const estimatedDistance = document.getElementById("{{ form.estimated_distance.id_for_label }}");
    const estimatedDuration = document.getElementById("{{ form.estimated_duration.id_for_label }}");
    const estimatedFare = document.getElementById("{{ form.estimated_fare.id_for_label }}");
    const pickupStatus = document.getElementById("pickupStatus");
    const dropStatus = document.getElementById("dropStatus");
    const pickupIndicatorText = document.getElementById("pickupIndicatorText");
    const dropIndicatorText = document.getElementById("dropIndicatorText");
    const pickupCheck = document.getElementById("pickupCheck");
    const dropCheck = document.getElementById("dropCheck");
    const sideDistance = document.getElementById("sideDistance");
    const sideDuration = document.getElementById("sideDuration");
    const sideFare = document.getElementById("sideFare");
    const routeSummary = document.getElementById("routeSummary");
    const routeSummaryTitle = document.getElementById("routeSummaryTitle");
    const routeSummaryText = document.getElementById("routeSummaryText");
    const fareStatus = document.getElementById("fareStatus");
    const locationStatusBadge = document.getElementById("locationStatusBadge");
    const mapLoading = document.getElementById("mapLoading");
    const mapLoadingText = document.getElementById("mapLoadingText");

    function hasValue(element) {
        return !!element && String(element.value || "").trim() !== "";
    }

    function getNumber(element) {
        if (!element || !hasValue(element)) {
            return null;
        }
        const value = Number(element.value);
        return Number.isFinite(value) ? value : null;
    }

    function setMapLoading(show, text) {
        if (!mapLoading) {
            return;
        }
        if (show) {
            mapLoadingText.textContent = text || "Loading...";
            mapLoading.classList.remove("d-none");
        } else {
            mapLoading.classList.add("d-none");
        }
    }

    function setLocationBadge(text, type) {
        if (!locationStatusBadge) {
            return;
        }
        locationStatusBadge.textContent = text;
        locationStatusBadge.className = "badge rounded-pill border";
        if (type === "success") {
            locationStatusBadge.classList.add("bg-success-subtle", "text-success");
        } else if (type === "danger") {
            locationStatusBadge.classList.add("bg-danger-subtle", "text-danger");
        } else if (type === "warning") {
            locationStatusBadge.classList.add("bg-warning-subtle", "text-warning");
        } else {
            locationStatusBadge.classList.add("bg-light", "text-secondary");
        }
    }

    function setCityField(field, cityName) {
        if (!field || !cityName) {
            return;
        }
        const normalizedCity = cityName.trim().toLowerCase();
        if (field.tagName === "SELECT") {
            const options = Array.from(field.options);
            const exactTextMatch = options.find(function (option) {
                return option.text.trim().toLowerCase() === normalizedCity;
            });
            if (exactTextMatch) {
                field.value = exactTextMatch.value;
                return;
            }
            const partialTextMatch = options.find(function (option) {
                return option.text.trim().toLowerCase().includes(normalizedCity);
            });
            if (partialTextMatch) {
                field.value = partialTextMatch.value;
            }
            return;
        }
        field.value = cityName;
    }

    function setPickupState(selected) {
        if (!pickupCheck || !pickupIndicatorText) {
            return;
        }
        if (selected) {
            pickupCheck.textContent = "Ready";
            pickupCheck.className = "badge bg-success-subtle text-success";
            pickupIndicatorText.textContent = pickupAddress.value || "Pickup selected";
        } else {
            pickupCheck.textContent = "Pending";
            pickupCheck.className = "badge bg-light text-secondary";
            pickupIndicatorText.textContent = "Not selected";
        }
    }

    function setDropState(selected) {
        if (!dropCheck || !dropIndicatorText) {
            return;
        }
        if (selected) {
            dropCheck.textContent = "Ready";
            dropCheck.className = "badge bg-success-subtle text-success";
            dropIndicatorText.textContent = dropAddress.value || "Destination selected";
        } else {
            dropCheck.textContent = "Pending";
            dropCheck.className = "badge bg-light text-secondary";
            dropIndicatorText.textContent = "Not selected";
        }
    }

    function resetRouteData() {
        if (routeLayer && rideMap) {
            rideMap.removeLayer(routeLayer);
            routeLayer = null;
        }
        if (estimatedDistance) {
            estimatedDistance.value = "";
        }
        if (estimatedDuration) {
            estimatedDuration.value = "";
        }
        if (estimatedFare) {
            estimatedFare.value = "";
        }
        if (sideDistance) {
            sideDistance.textContent = "—";
        }
        if (sideDuration) {
            sideDuration.textContent = "—";
        }
        if (sideFare) {
            sideFare.textContent = "—";
        }
        if (routeSummary) {
            routeSummary.classList.add("d-none");
        }
        if (fareStatus) {
            fareStatus.textContent = "Fare will be calculated after route calculation.";
        }
    }

    function createMap() {
        const mapElement = document.getElementById("rideMap");
        if (!mapElement) {
            return;
        }
        if (typeof L === "undefined") {
            mapElement.innerHTML =
                '<div class="d-flex align-items-center justify-content-center h-100 text-danger">Map library failed to load.</div>';
            return;
        }
        rideMap = L.map("rideMap", {
            zoomControl: true,
            scrollWheelZoom: true,
            attributionControl: false
        }).setView(DEFAULT_CENTER, DEFAULT_ZOOM);

        L.tileLayer(
            "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=cb1_3wf8_1_477b9c969e22fe3e205f303d",
            {
                subdomains: "abcd",
                maxZoom: 20
            }
        ).addTo(rideMap);

        rideMap.on("click", async function (event) {
            await setDropFromCoordinates(
                event.latlng.lat,
                event.latlng.lng,
                true
            );
        });

        setTimeout(function () {
            rideMap.invalidateSize();
        }, 200);
    }

    function escapeHtml(value) {
        return String(value || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function markerTooltipHtml(title, address, lat, lng) {
        const locationName =
            address && String(address).trim()
                ? String(address).trim()
                : "Location selected on map";

        return (
            '<div class="map-marker-tooltip">' +
            '<div class="fw-semibold mb-1">' +
            escapeHtml(title) +
            "</div>" +
            '<div class="small mb-1">' +
            escapeHtml(locationName) +
            "</div>" +
            '<div class="small text-muted">Latitude: ' +
            Number(lat).toFixed(6) +
            "</div>" +
            '<div class="small text-muted">Longitude: ' +
            Number(lng).toFixed(6) +
            "</div>" +
            "</div>"
        );
    }

    function updatePickupMarkerTooltip() {
        if (!pickupMarker) {
            return;
        }
        const lat = getNumber(pickupLatitude);
        const lng = getNumber(pickupLongitude);
        if (lat === null || lng === null) {
            return;
        }
        pickupMarker.unbindTooltip();
        pickupMarker.bindTooltip(
            markerTooltipHtml(
                "Pickup Location",
                pickupAddress ? pickupAddress.value : "",
                lat,
                lng
            ),
            {
                direction: "top",
                sticky: true,
                opacity: 0.98,
                className: "map-location-tooltip"
            }
        );
    }

    function updateDropMarkerTooltip() {
        if (!dropMarker) {
            return;
        }
        const lat = getNumber(dropLatitude);
        const lng = getNumber(dropLongitude);
        if (lat === null || lng === null) {
            return;
        }
        dropMarker.unbindTooltip();
        dropMarker.bindTooltip(
            markerTooltipHtml(
                "Destination",
                dropAddress ? dropAddress.value : "",
                lat,
                lng
            ),
            {
                direction: "top",
                sticky: true,
                opacity: 0.98,
                className: "map-location-tooltip"
            }
        );
    }

    function createPickupMarker(lat, lng) {
        if (!rideMap) {
            return;
        }
        if (pickupMarker) {
            rideMap.removeLayer(pickupMarker);
        }
        pickupMarker = L.marker(
            [lat, lng],
            {
                title: "Pickup Location"
            }
        ).addTo(rideMap);
        updatePickupMarkerTooltip();
    }

    function createDropMarker(lat, lng) {
        if (!rideMap) {
            return;
        }
        if (dropMarker) {
            rideMap.removeLayer(dropMarker);
        }
        dropMarker = L.marker(
            [lat, lng],
            {
                title: "Destination"
            }
        ).addTo(rideMap);
        updateDropMarkerTooltip();
    }

    function fitRouteBounds() {
        if (!rideMap) {
            return;
        }
        const points = [];
        const pickupLat = getNumber(pickupLatitude);
        const pickupLng = getNumber(pickupLongitude);
        const dropLat = getNumber(dropLatitude);
        const dropLng = getNumber(dropLongitude);

        if (pickupLat !== null && pickupLng !== null) {
            points.push([pickupLat, pickupLng]);
        }
        if (dropLat !== null && dropLng !== null) {
            points.push([dropLat, dropLng]);
        }
        if (!points.length) {
            rideMap.setView(DEFAULT_CENTER, DEFAULT_ZOOM);
            return;
        }
        if (points.length === 1) {
            rideMap.setView(points[0], 15);
            return;
        }
        rideMap.fitBounds(
            points,
            {
                padding: [40, 40]
            }
        );
    }

    async function reverseGeocode(latitude, longitude) {
        const url =
            "https://nominatim.openstreetmap.org/reverse" +
            "?format=jsonv2" +
            "&lat=" + encodeURIComponent(latitude) +
            "&lon=" + encodeURIComponent(longitude) +
            "&zoom=18" +
            "&addressdetails=1";

        const response = await fetch(
            url,
            {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                }
            }
        );

        if (!response.ok) {
            throw new Error(
                "Unable to identify this location."
            );
        }

        return await response.json();
    }

    async function searchGeocoding(query) {
        const url =
            "https://nominatim.openstreetmap.org/search" +
            "?format=jsonv2" +
            "&limit=1" +
            "&addressdetails=1" +
            "&q=" + encodeURIComponent(query);

        const response = await fetch(
            url,
            {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                }
            }
        );

        if (!response.ok) {
            throw new Error(
                "Location search failed."
            );
        }

        const data = await response.json();

        if (!Array.isArray(data) || !data.length) {
            return null;
        }

        return data[0];
    }

    function getCityFromAddress(address) {
        if (!address) {
            return "";
        }

        return (
            address.city ||
            address.town ||
            address.village ||
            address.municipality ||
            address.county ||
            ""
        );
    }

    function getReadableAddress(data, fallback) {
        if (!data) {
            return fallback;
        }

        if (data.display_name) {
            return data.display_name;
        }

        if (data.address) {
            const parts = [
                data.address.road,
                data.address.neighbourhood,
                data.address.suburb,
                data.address.city,
                data.address.town,
                data.address.village,
                data.address.state,
                data.address.country
            ].filter(Boolean);

            if (parts.length) {
                return parts.join(", ");
            }
        }

        return fallback;
    }

    async function resolvePickupAddress(showStatus = true) {
        const query = String(
            pickupAddress.value || ""
        ).trim();

        if (!query || pickupGeocodeInProgress) {
            return false;
        }

        pickupGeocodeInProgress = true;

        if (showStatus) {
            pickupStatus.textContent =
                "Finding pickup location...";
            setLocationBadge(
                "Finding pickup",
                "warning"
            );
        }

        try {
            const result =
                await searchGeocoding(query);

            if (!result) {
                throw new Error(
                    "No matching pickup location was found."
                );
            }

            const latitude = Number(result.lat);
            const longitude = Number(result.lon);

            if (
                !Number.isFinite(latitude) ||
                !Number.isFinite(longitude)
            ) {
                throw new Error(
                    "Invalid pickup coordinates were returned."
                );
            }

            pickupLatitude.value =
                latitude.toFixed(6);
            pickupLongitude.value =
                longitude.toFixed(6);

            pickupCityName =
                getCityFromAddress(
                    result.address
                );

            setCityField(
                pickupCityField,
                pickupCityName
            );

            updatingPickupAddress = true;
            pickupAddress.value =
                result.display_name || query;
            updatingPickupAddress = false;

            createPickupMarker(
                latitude,
                longitude
            );

            setPickupState(true);
            updatePickupMarkerTooltip();

            pickupStatus.textContent =
                pickupCityName
                    ? "Pickup selected in " + pickupCityName + "."
                    : "Pickup location selected.";

            setLocationBadge(
                "Pickup ready",
                "success"
            );

            fitRouteBounds();
            return true;
        } catch (error) {
            pickupLatitude.value = "";
            pickupLongitude.value = "";
            pickupCityName = "";

            if (pickupCityField) {
                pickupCityField.value = "";
            }

            setPickupState(false);

            pickupStatus.textContent =
                error.message ||
                "Unable to find pickup location.";

            setLocationBadge(
                "Pickup not found",
                "danger"
            );

            return false;
        } finally {
            pickupGeocodeInProgress = false;
        }
    }

    async function resolveDropAddress(showStatus = true) {
        const query = String(
            dropAddress.value || ""
        ).trim();

        if (!query || dropGeocodeInProgress) {
            return false;
        }

        dropGeocodeInProgress = true;

        if (showStatus) {
            dropStatus.textContent =
                "Finding destination...";

            setLocationBadge(
                "Finding destination",
                "warning"
            );
        }

        try {
            const result =
                await searchGeocoding(query);

            if (!result) {
                throw new Error(
                    "No matching destination was found."
                );
            }

            const latitude = Number(result.lat);
            const longitude = Number(result.lon);

            if (
                !Number.isFinite(latitude) ||
                !Number.isFinite(longitude)
            ) {
                throw new Error(
                    "Invalid destination coordinates were returned."
                );
            }

            dropLatitude.value =
                latitude.toFixed(6);
            dropLongitude.value =
                longitude.toFixed(6);

            dropCityName =
                getCityFromAddress(
                    result.address
                );

            setCityField(
                dropCityField,
                dropCityName
            );

            updatingDropAddress = true;
            dropAddress.value =
                result.display_name || query;
            updatingDropAddress = false;

            createDropMarker(
                latitude,
                longitude
            );

            setDropState(true);
            updateDropMarkerTooltip();

            dropStatus.textContent =
                dropCityName
                    ? "Destination selected in " + dropCityName + "."
                    : "Destination selected.";

            setLocationBadge(
                "Destination ready",
                "success"
            );

            fitRouteBounds();
            return true;
        } catch (error) {
            dropLatitude.value = "";
            dropLongitude.value = "";
            dropCityName = "";

            if (dropCityField) {
                dropCityField.value = "";
            }

            setDropState(false);

            dropStatus.textContent =
                error.message ||
                "Unable to find destination.";

            setLocationBadge(
                "Destination not found",
                "danger"
            );

            return false;
        } finally {
            dropGeocodeInProgress = false;
        }
    }

    async function useCurrentLocation() {
        if (!navigator.geolocation) {
            pickupStatus.textContent =
                "Geolocation is not supported by this browser.";

            setLocationBadge(
                "GPS unavailable",
                "danger"
            );

            return false;
        }

        const button =
            document.getElementById(
                "useCurrentLocationBtn"
            );

        if (button) {
            button.disabled = true;
            button.innerHTML =
                '<span class="spinner-border spinner-border-sm me-1"></span> Detecting';
        }

        pickupStatus.textContent =
            "Requesting your current location...";

        setLocationBadge(
            "Detecting location",
            "warning"
        );

        return new Promise(function (resolve) {
            navigator.geolocation.getCurrentPosition(
                async function (position) {
                    try {
                        const latitude =
                            Number(
                                position.coords.latitude
                            );

                        const longitude =
                            Number(
                                position.coords.longitude
                            );

                        if (
                            !Number.isFinite(latitude) ||
                            !Number.isFinite(longitude)
                        ) {
                            throw new Error(
                                "Invalid GPS coordinates."
                            );
                        }

                        pickupLatitude.value =
                            latitude.toFixed(6);

                        pickupLongitude.value =
                            longitude.toFixed(6);

                        createPickupMarker(
                            latitude,
                            longitude
                        );

                        setPickupState(true);

                        if (rideMap) {
                            rideMap.setView(
                                [
                                    latitude,
                                    longitude
                                ],
                                16
                            );
                        }

                        pickupStatus.textContent =
                            "Location detected. Finding address...";

                        try {
                            const data =
                                await reverseGeocode(
                                    latitude,
                                    longitude
                                );

                            updatingPickupAddress = true;

                            pickupAddress.value =
                                getReadableAddress(
                                    data,
                                    "Current Location"
                                );

                            updatePickupMarkerTooltip();

                            updatingPickupAddress = false;

                            pickupCityName =
                                getCityFromAddress(
                                    data.address
                                );

                            setCityField(
                                pickupCityField,
                                pickupCityName
                            );

                            pickupStatus.textContent =
                                pickupCityName
                                    ? "Current location saved in " + pickupCityName + "."
                                    : "Current location saved.";

                            setPickupState(true);

                            setLocationBadge(
                                "Pickup ready",
                                "success"
                            );
                        } catch (error) {
                            updatingPickupAddress = true;

                            pickupAddress.value =
                                latitude.toFixed(6) +
                                ", " +
                                longitude.toFixed(6);

                            updatingPickupAddress = false;

                            pickupCityName = "";

                            pickupStatus.textContent =
                                "GPS coordinates saved. Address lookup failed.";

                            setPickupState(true);

                            setLocationBadge(
                                "GPS pickup ready",
                                "success"
                            );
                        }

                        fitRouteBounds();

                        if (
                            getNumber(dropLatitude) !== null &&
                            getNumber(dropLongitude) !== null
                        ) {
                            await calculateRoute();
                        }

                        resolve(true);
                    } catch (error) {
                        pickupStatus.textContent =
                            error.message ||
                            "Unable to save current location.";

                        setLocationBadge(
                            "Location failed",
                            "danger"
                        );

                        resolve(false);
                    } finally {
                        if (button) {
                            button.disabled = false;
                            button.innerHTML =
                                '<i class="bi bi-crosshair me-1"></i> Current';
                        }
                    }
                },
                function (error) {
                    let message =
                        "Unable to detect your location.";

                    if (error.code === 1) {
                        message =
                            "Location permission was denied. Please allow location access.";
                    } else if (error.code === 2) {
                        message =
                            "Your current location could not be determined.";
                    } else if (error.code === 3) {
                        message =
                            "Location request timed out. Please try again.";
                    }

                    pickupStatus.textContent =
                        message;

                    setLocationBadge(
                        "Location failed",
                        "danger"
                    );

                    if (button) {
                        button.disabled = false;
                        button.innerHTML =
                            '<i class="bi bi-crosshair me-1"></i> Current';
                    }

                    resolve(false);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 15000,
                    maximumAge: 30000
                }
            );
        });
    }

    function clearPickup() {
        pickupLatitude.value = "";
        pickupLongitude.value = "";
        pickupCityName = "";

        if (pickupAddress) {
            pickupAddress.value = "";
        }

        if (pickupCityField) {
            pickupCityField.value = "";
        }

        if (pickupMarker && rideMap) {
            rideMap.removeLayer(pickupMarker);
            pickupMarker = null;
        }

        setPickupState(false);

        pickupStatus.textContent =
            "Enter pickup address or click Current.";

        resetRouteData();

        setLocationBadge(
            "Pickup pending",
            "warning"
        );

        if (pickupAddress) {
            pickupAddress.focus();
        }
    }

    async function setDropFromCoordinates(
        latitude,
        longitude,
        reverseLookup
    ) {
        dropLatitude.value =
            Number(latitude).toFixed(6);

        dropLongitude.value =
            Number(longitude).toFixed(6);

        createDropMarker(
            latitude,
            longitude
        );

        setDropState(true);

        if (rideMap) {
            rideMap.setView(
                [
                    latitude,
                    longitude
                ],
                Math.max(
                    rideMap.getZoom(),
                    14
                )
            );
        }

        if (reverseLookup) {
            dropStatus.textContent =
                "Destination selected. Finding address...";

            try {
                const data =
                    await reverseGeocode(
                        latitude,
                        longitude
                    );

                updatingDropAddress = true;

                dropAddress.value =
                    getReadableAddress(
                        data,
                        "Selected Destination"
                    );

                updateDropMarkerTooltip();

                updatingDropAddress = false;

                dropCityName =
                    getCityFromAddress(
                        data.address
                    );

                setCityField(
                    dropCityField,
                    dropCityName
                );

                dropStatus.textContent =
                    dropCityName
                        ? "Destination selected in " + dropCityName + "."
                        : "Destination selected.";
            } catch (error) {
                updatingDropAddress = true;

                dropAddress.value =
                    "Selected Destination";

                updatingDropAddress = false;

                dropCityName = "";

                dropStatus.textContent =
                    "Destination selected, but address lookup failed.";
            }
        }

        setLocationBadge(
            "Destination ready",
            "success"
        );

        return await calculateRoute();
    }

    async function searchDestination() {
        const query =
            String(
                dropAddress.value || ""
            ).trim();

        if (!query) {
            dropStatus.textContent =
                "Enter a destination before searching.";

            dropAddress.focus();

            setLocationBadge(
                "Destination required",
                "warning"
            );

            return false;
        }

        const button =
            document.getElementById(
                "searchDestinationBtn"
            );

        if (button) {
            button.disabled = true;
            button.innerHTML =
                '<span class="spinner-border spinner-border-sm me-1"></span> Searching';
        }

        try {
            const resolved =
                await resolveDropAddress(true);

            if (!resolved) {
                return false;
            }

            return await calculateRoute();
        } finally {
            if (button) {
                button.disabled = false;
                button.innerHTML =
                    '<i class="bi bi-search me-1"></i> Search';
            }
        }
    }

    async function calculateRoute() {
        const pickupLat =
            getNumber(pickupLatitude);

        const pickupLng =
            getNumber(pickupLongitude);

        const dropLat =
            getNumber(dropLatitude);

        const dropLng =
            getNumber(dropLongitude);

        if (
            pickupLat === null ||
            pickupLng === null ||
            dropLat === null ||
            dropLng === null
        ) {
            return false;
        }

        if (
            Math.abs(pickupLat - dropLat) < 0.000001 &&
            Math.abs(pickupLng - dropLng) < 0.000001
        ) {
            routeSummary.classList.remove("d-none");

            routeSummaryTitle.textContent =
                "Invalid route";

            routeSummaryText.textContent =
                "Pickup and destination cannot be the same.";

            setLocationBadge(
                "Invalid route",
                "danger"
            );

            return false;
        }

        if (routeRequestInProgress) {
            return false;
        }

        routeRequestInProgress = true;

        setMapLoading(
            true,
            "Calculating route..."
        );

        setLocationBadge(
            "Calculating route",
            "warning"
        );

        try {
            const coordinates =
                pickupLng +
                "," +
                pickupLat +
                ";" +
                dropLng +
                "," +
                dropLat;

            const url =
                "https://router.project-osrm.org/route/v1/driving/" +
                coordinates +
                "?overview=full&geometries=geojson&steps=false";

            const response =
                await fetch(
                    url,
                    {
                        method: "GET",
                        headers: {
                            "Accept": "application/json"
                        }
                    }
                );

            if (!response.ok) {
                throw new Error(
                    "Routing service is unavailable."
                );
            }

            const data =
                await response.json();

            if (
                data.code !== "Ok" ||
                !data.routes ||
                !data.routes.length
            ) {
                throw new Error(
                    "No driving route was found."
                );
            }

            const route =
                data.routes[0];

            const distanceKm =
                Number(route.distance) / 1000;

            const durationMinutes =
                Math.max(
                    1,
                    Math.round(
                        Number(route.duration) / 60
                    )
                );

            estimatedDistance.value =
                distanceKm.toFixed(2);

            estimatedDuration.value =
                durationMinutes;

            sideDistance.textContent =
                distanceKm.toFixed(2) +
                " km";

            sideDuration.textContent =
                durationMinutes +
                " min";

            if (
                routeLayer &&
                rideMap
            ) {
                rideMap.removeLayer(
                    routeLayer
                );
                routeLayer = null;
            }

            if (
                route.geometry &&
                route.geometry.coordinates &&
                route.geometry.coordinates.length
            ) {
                const latLngs =
                    route.geometry.coordinates.map(
                        function (point) {
                            return [
                                point[1],
                                point[0]
                            ];
                        }
                    );

                routeLayer =
                    L.polyline(
                        latLngs,
                        {
                            weight: 5,
                            opacity: 0.85
                        }
                    ).addTo(rideMap);

                rideMap.fitBounds(
                    routeLayer.getBounds(),
                    {
                        padding: [40, 40]
                    }
                );
            } else {
                fitRouteBounds();
            }

            routeSummary.classList.remove("d-none");

            routeSummaryTitle.textContent =
                "Route calculated successfully";

            routeSummaryText.textContent =
                distanceKm.toFixed(2) +
                " km · approximately " +
                durationMinutes +
                " minutes";

            setLocationBadge(
                "Route ready",
                "success"
            );

            await updateFareDisplay();

            return true;
        } catch (error) {
            routeSummary.classList.remove("d-none");

            routeSummaryTitle.textContent =
                "Route calculation failed";

            routeSummaryText.textContent =
                error.message ||
                "Unable to calculate route.";

            setLocationBadge(
                "Route failed",
                "danger"
            );

            return false;
        } finally {
            routeRequestInProgress = false;
            setMapLoading(false);
        }
    }

    async function updateFareDisplay() {
        const vehicleType =
            document.getElementById(
                "{{ form.vehicle_type.id_for_label }}"
            );

        const vehicleFareHint =
            document.getElementById(
                "vehicleFareHint"
            );

        const distance =
            getNumber(
                estimatedDistance
            );

        const duration =
            getNumber(
                estimatedDuration
            );

        const selectedVehicle =
            vehicleType
                ? vehicleType.value
                : "";

        const cityName =
            pickupCityName ||
            dropCityName;

        const cityId =
            pickupCityField &&
            pickupCityField.value
                ? pickupCityField.value
                : (
                    dropCityField &&
                    dropCityField.value
                        ? dropCityField.value
                        : ""
                );

        if (
            !selectedVehicle ||
            distance === null ||
            duration === null ||
            (!cityName && !cityId)
        ) {
            fareStatus.textContent =
                !selectedVehicle
                    ? "Select a vehicle type to calculate the fare."
                    : "Location city is still being identified.";
            return;
        }

        if (fareRequestInProgress) {
            return;
        }

        fareRequestInProgress = true;

        fareStatus.innerHTML =
            '<span class="spinner-border spinner-border-sm me-1"></span> Updating fare...';

        if (vehicleFareHint) {
            vehicleFareHint.textContent =
                "Calculating fare for the selected vehicle and route...";
        }

        try {
            const url =
                new URL(
                    window.location.href
                );

            url.searchParams.set(
                "fare_preview",
                "1"
            );

            url.searchParams.set(
                "vehicle_type",
                selectedVehicle
            );

            if (cityName) {
                url.searchParams.set(
                    "city_name",
                    cityName
                );
            }

            if (cityId) {
                url.searchParams.set(
                    "city_id",
                    cityId
                );
            }

            url.searchParams.set(
                "distance",
                distance.toFixed(2)
            );

            url.searchParams.set(
                "duration",
                Math.round(duration)
            );

            const response =
                await fetch(
                    url.toString(),
                    {
                        method: "GET",
                        headers: {
                            "Accept": "application/json",
                            "X-Requested-With": "XMLHttpRequest"
                        }
                    }
                );

            const data =
                await response.json();

            if (
                !response.ok ||
                !data.success
            ) {
                throw new Error(
                    data.message ||
                    "Fare could not be calculated."
                );
            }

            const fare =
                Number(data.fare);

            if (!Number.isFinite(fare)) {
                throw new Error(
                    "Invalid fare was returned."
                );
            }

            estimatedFare.value =
                fare.toFixed(2);

            sideFare.textContent =
                "₹" +
                fare.toFixed(2);

            fareStatus.textContent =
                "Fare updated for " +
                (data.vehicle_type || selectedVehicle) +
                " in " +
                (data.city || cityName) +
                ".";

            if (vehicleFareHint) {
                vehicleFareHint.textContent =
                    "Fare updates automatically when vehicle or route changes.";
            }
        } catch (error) {
            fareStatus.textContent =
                error.message ||
                "Unable to update fare.";

            if (vehicleFareHint) {
                vehicleFareHint.textContent =
                    "Check the active pricing rule for this vehicle and location.";
            }
        } finally {
            fareRequestInProgress = false;
        }
    }

    function clearDestination() {
        dropLatitude.value = "";
        dropLongitude.value = "";
        dropAddress.value = "";
        dropCityName = "";

        if (dropCityField) {
            dropCityField.value = "";
        }

        if (dropMarker && rideMap) {
            rideMap.removeLayer(dropMarker);
            dropMarker = null;
        }

        setDropState(false);

        dropStatus.textContent =
            "Enter a destination or click the map.";

        resetRouteData();

        setLocationBadge(
            "Destination pending",
            "warning"
        );

        if (dropAddress) {
            dropAddress.focus();
        }
    }

    function focusDestination() {
        if (dropAddress) {
            dropAddress.focus();
            dropAddress.select();
        }
    }

    function initializeExistingLocations() {
        const pickupLat =
            getNumber(pickupLatitude);

        const pickupLng =
            getNumber(pickupLongitude);

        const dropLat =
            getNumber(dropLatitude);

        const dropLng =
            getNumber(dropLongitude);

        if (
            pickupLat !== null &&
            pickupLng !== null
        ) {
            createPickupMarker(
                pickupLat,
                pickupLng
            );

            setPickupState(true);
        }

        if (
            dropLat !== null &&
            dropLng !== null
        ) {
            createDropMarker(
                dropLat,
                dropLng
            );

            setDropState(true);
        }

        const existingDistance =
            getNumber(
                estimatedDistance
            );

        const existingDuration =
            getNumber(
                estimatedDuration
            );

        const existingFare =
            getNumber(
                estimatedFare
            );

        if (existingDistance !== null) {
            sideDistance.textContent =
                existingDistance.toFixed(2) +
                " km";
        }

        if (existingDuration !== null) {
            sideDuration.textContent =
                existingDuration +
                " min";
        }

        if (existingFare !== null) {
            sideFare.textContent =
                "₹" +
                existingFare.toFixed(2);
        }

        fitRouteBounds();
    }

    function getPaymentModal() {
        const modalElement =
            document.getElementById(
                "ridePaymentModal"
            );

        if (
            !modalElement ||
            typeof bootstrap === "undefined" ||
            !bootstrap.Modal
        ) {
            return null;
        }

        return bootstrap.Modal.getOrCreateInstance(
            modalElement
        );
    }

    function openPaymentModal() {
        if (isEditMode) {
            return;
        }

        const fare =
            getNumber(
                estimatedFare
            );

        const distance =
            getNumber(
                estimatedDistance
            );

        const duration =
            getNumber(
                estimatedDuration
            );

        if (
            fare === null ||
            fare <= 0
        ) {
            fareStatus.textContent =
                "Please wait until fare calculation is completed.";

            return;
        }

        document.getElementById(
            "paymentFareAmount"
        ).textContent =
            "₹" +
            fare.toFixed(2);

        document.getElementById(
            "paymentDistance"
        ).textContent =
            distance !== null
                ? distance.toFixed(2) + " km"
                : "—";

        document.getElementById(
            "paymentDuration"
        ).textContent =
            duration !== null
                ? Math.round(duration) + " min"
                : "—";

        changePaymentMethod();

        const modal =
            getPaymentModal();

        if (!modal) {
            alert(
                "Payment popup cannot open because Bootstrap Modal JavaScript is not loaded in base.html."
            );
            return;
        }

        modal.show();
    }

    function hidePaymentFields() {
        [
            "cardPaymentFields",
            "upiPaymentFields",
            "walletPaymentFields",
            "netbankingPaymentFields",
            "cashPaymentFields"
        ].forEach(
            function (id) {
                const element =
                    document.getElementById(id);

                if (element) {
                    element.classList.add(
                        "d-none"
                    );
                }
            }
        );
    }

    function selectPaymentMethod(method) {
        selectedPaymentMethod =
            method;

        document
            .querySelectorAll(
                ".payment-method-card"
            )
            .forEach(
                function (button) {
                    button.classList.toggle(
                        "active",
                        button.dataset.paymentMethod === method
                    );
                }
            );

        hidePaymentFields();

        const labels = {
            wallet: "Wallet",
            card: "Card",
            upi: "UPI",
            netbanking: "Net Banking",
            cash: "Cash"
        };

        const selectedSection =
            document.getElementById(
                "selectedPaymentSection"
            );

        const selectedText =
            document.getElementById(
                "selectedPaymentMethodText"
            );

        const continueButton =
            document.getElementById(
                "continuePaymentBtn"
            );

        selectedSection.classList.remove(
            "d-none"
        );

        selectedText.textContent =
            labels[method] ||
            method;

        const field =
            document.getElementById(
                method +
                "PaymentFields"
            );

        if (field) {
            field.classList.remove(
                "d-none"
            );
        }

        continueButton.disabled = false;

        const message =
            document.getElementById(
                "paymentGatewayMessage"
            );

        if (message) {
            message.className =
                "alert alert-light border mt-3 mb-0 d-none";

            message.innerHTML = "";
        }
    }

    function changePaymentMethod() {
        selectedPaymentMethod = "";

        document
            .querySelectorAll(
                ".payment-method-card"
            )
            .forEach(
                function (button) {
                    button.classList.remove(
                        "active"
                    );
                }
            );

        hidePaymentFields();

        const selectedSection =
            document.getElementById(
                "selectedPaymentSection"
            );

        const continueButton =
            document.getElementById(
                "continuePaymentBtn"
            );

        if (selectedSection) {
            selectedSection.classList.add(
                "d-none"
            );
        }

        if (continueButton) {
            continueButton.disabled = true;
        }

        const message =
            document.getElementById(
                "paymentGatewayMessage"
            );

        if (message) {
            message.className =
                "alert alert-light border mt-3 mb-0 d-none";

            message.innerHTML = "";
        }
    }

    function validatePaymentFields() {
        if (!selectedPaymentMethod) {
            return false;
        }

        if (selectedPaymentMethod === "card") {
            const cardNumber =
                document.getElementById(
                    "paymentCardNumber"
                );

            const cardName =
                document.getElementById(
                    "paymentCardName"
                );

            const expiry =
                document.getElementById(
                    "paymentCardExpiry"
                );

            const cvv =
                document.getElementById(
                    "paymentCardCvv"
                );

            if (
                !cardNumber ||
                !cardName ||
                !expiry ||
                !cvv
            ) {
                return false;
            }

            const digits =
                cardNumber.value.replace(
                    /\D/g,
                    ""
                );

            return (
                digits.length >= 12 &&
                cardName.value.trim() &&
                /^\d{2}\/\d{2}$/.test(
                    expiry.value.trim()
                ) &&
                /^\d{3,4}$/.test(
                    cvv.value.trim()
                )
            );
        }

        if (selectedPaymentMethod === "upi") {
            const upi =
                document.getElementById(
                    "paymentUpiId"
                );

            return !!(
                upi &&
                upi.value.trim() &&
                /^[^@\s]+@[^@\s]+$/.test(
                    upi.value.trim()
                )
            );
        }

        if (selectedPaymentMethod === "netbanking") {
            const bank =
                document.getElementById(
                    "paymentBank"
                );

            return !!(
                bank &&
                bank.value
            );
        }

        return true;
    }

    function showPaymentMessage(
        type,
        message
    ) {
        const element =
            document.getElementById(
                "paymentGatewayMessage"
            );

        if (!element) {
            return;
        }

        element.className =
            "alert alert-" +
            type +
            " mt-3 mb-0";

        element.innerHTML =
            message;
    }

    async function parseJsonResponse(
        response
    ) {
        const contentType =
            response.headers.get(
                "content-type"
            ) || "";

        if (
            contentType.toLowerCase().includes(
                "application/json"
            )
        ) {
            return await response.json();
        }

        const text =
            await response.text();

        const cleaned =
            text
                .replace(/<[^>]*>/g, " ")
                .replace(/\s+/g, " ")
                .trim();

        if (response.status === 403) {
            throw new Error(
                "Payment request was rejected by the server. Please refresh the page and try again."
            );
        }

        if (
            response.status === 401 ||
            response.redirected
        ) {
            throw new Error(
                "Your session has expired. Please login again and retry the payment."
            );
        }

        throw new Error(
            cleaned ||
            "Server returned an invalid payment response."
        );
    }

    function getCsrfToken() {
        const csrfInput =
            form.querySelector(
                'input[name="csrfmiddlewaretoken"]'
            );

        return csrfInput
            ? csrfInput.value
            : "";
    }

    async function continuePayment() {
        if (paymentSubmitting) {
            return;
        }

        if (!selectedPaymentMethod) {
            showPaymentMessage(
                "warning",
                '<i class="bi bi-exclamation-triangle me-1"></i> Please select a payment method.'
            );
            return;
        }

        if (!validatePaymentFields()) {
            showPaymentMessage(
                "warning",
                '<i class="bi bi-exclamation-triangle me-1"></i> Please complete the selected payment details.'
            );
            return;
        }

        const fare =
            getNumber(
                estimatedFare
            );

        if (
            fare === null ||
            fare <= 0
        ) {
            showPaymentMessage(
                "danger",
                '<i class="bi bi-exclamation-circle me-1"></i> Valid ride fare is required before payment.'
            );
            return;
        }

        paymentSubmitting = true;

        const continueButton =
            document.getElementById(
                "continuePaymentBtn"
            );

        if (continueButton) {
            continueButton.disabled = true;
            continueButton.innerHTML =
                '<span class="spinner-border spinner-border-sm me-2"></span> Processing...';
        }

        showPaymentMessage(
            "info",
            '<span class="spinner-border spinner-border-sm me-1"></span> Creating payment and validating ride details...'
        );

        try {
            const formData =
                new FormData(form);

            formData.set(
                "pickup_latitude",
                String(pickupLatitude.value || "")
            );

            formData.set(
                "pickup_longitude",
                String(pickupLongitude.value || "")
            );

            formData.set(
                "drop_latitude",
                String(dropLatitude.value || "")
            );

            formData.set(
                "drop_longitude",
                String(dropLongitude.value || "")
            );

            formData.set(
                "estimated_distance",
                String(estimatedDistance.value || "")
            );

            formData.set(
                "estimated_duration",
                String(estimatedDuration.value || "")
            );

            formData.set(
                "estimated_fare",
                String(estimatedFare.value || "")
            );

            formData.set(
                "payment_method",
                selectedPaymentMethod
            );

            if (
                selectedPaymentMethod ===
                "card"
            ) {
                formData.set(
                    "card_number",
                    document.getElementById(
                        "paymentCardNumber"
                    ).value.trim()
                );

                formData.set(
                    "card_name",
                    document.getElementById(
                        "paymentCardName"
                    ).value.trim()
                );

                formData.set(
                    "card_expiry",
                    document.getElementById(
                        "paymentCardExpiry"
                    ).value.trim()
                );

                formData.set(
                    "card_cvv",
                    document.getElementById(
                        "paymentCardCvv"
                    ).value.trim()
                );
            }

            if (
                selectedPaymentMethod ===
                "upi"
            ) {
                formData.set(
                    "upi_id",
                    document.getElementById(
                        "paymentUpiId"
                    ).value.trim()
                );
            }

            if (
                selectedPaymentMethod ===
                "netbanking"
            ) {
                formData.set(
                    "netbanking_bank",
                    document.getElementById(
                        "paymentBank"
                    ).value
                );
            }

            const createPaymentUrl =
                "{% url 'create_ride_payment' %}";

            const createResponse =
                await fetch(
                    createPaymentUrl,
                    {
                        method: "POST",
                        body: formData,
                        credentials: "same-origin",
                        headers: {
                            "X-CSRFToken":
                                getCsrfToken(),
                            "X-Requested-With":
                                "XMLHttpRequest",
                            "Accept":
                                "application/json"
                        }
                    }
                );

            const createData =
                await parseJsonResponse(
                    createResponse
                );

            if (
                !createResponse.ok ||
                !createData.success
            ) {
                let errorMessage =
                    createData.message ||
                    "Payment could not be initiated.";

                if (
                    createData.errors
                ) {
                    const errorParts = [];

                    Object.keys(
                        createData.errors
                    ).forEach(
                        function (field) {
                            const fieldErrors =
                                createData.errors[field];

                            const items =
                                Array.isArray(fieldErrors)
                                    ? fieldErrors
                                    : [fieldErrors];

                            items.forEach(
                                function (item) {
                                    const message =
                                        typeof item === "string"
                                            ? item
                                            : item && item.message
                                                ? item.message
                                                : String(item || "");

                                    if (
                                        message &&
                                        !errorParts.includes(
                                            message
                                        )
                                    ) {
                                        errorParts.push(
                                            message
                                        );
                                    }
                                }
                            );
                        }
                    );

                    if (errorParts.length) {
                        errorMessage +=
                            "<br>" +
                            errorParts.join(
                                "<br>"
                            );
                    }
                }

                throw new Error(
                    errorMessage
                );
            }

            const paymentId =
                createData.payment_id;

            if (!paymentId) {
                throw new Error(
                    "Payment ID was not returned by the server."
                );
            }

            showPaymentMessage(
                "info",
                '<span class="spinner-border spinner-border-sm me-1"></span> Payment created. Confirming payment...'
            );

            const confirmUrlTemplate =
                "{% url 'confirm_ride_payment' 999999 %}";

            const confirmUrl =
                confirmUrlTemplate.replace(
                    "999999",
                    String(paymentId)
                );

            const confirmResponse =
                await fetch(
                    confirmUrl,
                    {
                        method: "POST",
                        credentials: "same-origin",
                        headers: {
                            "X-CSRFToken":
                                getCsrfToken(),
                            "X-Requested-With":
                                "XMLHttpRequest",
                            "Accept":
                                "application/json"
                        }
                    }
                );

            const confirmData =
                await parseJsonResponse(
                    confirmResponse
                );

            if (
                !confirmResponse.ok ||
                !confirmData.success
            ) {
                let errorMessage =
                    confirmData.message ||
                    "Payment confirmation failed.";

                if (
                    confirmData.errors
                ) {
                    const errorParts = [];

                    Object.keys(
                        confirmData.errors
                    ).forEach(
                        function (field) {
                            const fieldErrors =
                                confirmData.errors[field];

                            const items =
                                Array.isArray(fieldErrors)
                                    ? fieldErrors
                                    : [fieldErrors];

                            items.forEach(
                                function (item) {
                                    const message =
                                        typeof item === "string"
                                            ? item
                                            : item && item.message
                                                ? item.message
                                                : String(item || "");

                                    if (
                                        message &&
                                        !errorParts.includes(
                                            message
                                        )
                                    ) {
                                        errorParts.push(
                                            message
                                        );
                                    }
                                }
                            );
                        }
                    );

                    if (errorParts.length) {
                        errorMessage +=
                            "<br>" +
                            errorParts.join(
                                "<br>"
                            );
                    }
                }

                throw new Error(
                    errorMessage
                );
            }

            let paymentInput =
                form.querySelector(
                    'input[name="payment_id"]'
                );

            if (!paymentInput) {
                paymentInput =
                    document.createElement("input");

                paymentInput.type = "hidden";
                paymentInput.name = "payment_id";

                form.appendChild(paymentInput);
            }

            paymentInput.value =
                String(paymentId);

            showPaymentMessage(
                "success",
                '<i class="bi bi-check-circle-fill me-1"></i> ' +
                (
                    confirmData.message ||
                    "Payment confirmed successfully."
                ) +
                '<br><span class="small">Opening Ride Request...</span>'
            );

            formSubmitting = true;

            setTimeout(
                function () {
                    if (
                        confirmData.redirect_url
                    ) {
                        window.location.href =
                            confirmData.redirect_url;
                    } else if (
                        confirmData.ride_request_id
                    ) {
                        window.location.href =
                            "{% url 'ride_request_details' 999999 %}".replace(
                                "999999",
                                String(
                                    confirmData.ride_request_id
                                )
                            );
                    } else {
                        window.location.reload();
                    }
                },
                500
            );
        } catch (error) {
            console.error(
                "NandiRide payment error:",
                error
            );

            showPaymentMessage(
                "danger",
                '<i class="bi bi-exclamation-circle-fill me-1"></i> ' +
                (
                    error.message ||
                    "Payment failed. Please try again."
                )
            );

            paymentSubmitting = false;

            if (continueButton) {
                continueButton.disabled = false;
                continueButton.innerHTML =
                    '<i class="bi bi-lock-fill me-1"></i> Confirm Payment';
            }
        }
    }

    async function validateBeforeSubmit(event) {
        event.preventDefault();

        if (formSubmitting) {
            return false;
        }

        let pickupLat =
            getNumber(
                pickupLatitude
            );

        let pickupLng =
            getNumber(
                pickupLongitude
            );

        let dropLat =
            getNumber(
                dropLatitude
            );

        let dropLng =
            getNumber(
                dropLongitude
            );

        if (
            pickupLat === null ||
            pickupLng === null
        ) {
            if (!hasValue(pickupAddress)) {
                pickupStatus.textContent =
                    "Please enter pickup address or use Current Location.";

                setLocationBadge(
                    "Pickup required",
                    "danger"
                );

                pickupAddress.focus();

                return false;
            }

            const pickupResolved =
                await resolvePickupAddress();

            if (!pickupResolved) {
                pickupAddress.focus();
                return false;
            }

            pickupLat =
                getNumber(
                    pickupLatitude
                );

            pickupLng =
                getNumber(
                    pickupLongitude
                );
        }

        if (
            dropLat === null ||
            dropLng === null
        ) {
            if (!hasValue(dropAddress)) {
                dropStatus.textContent =
                    "Please enter destination.";

                setLocationBadge(
                    "Destination required",
                    "danger"
                );

                dropAddress.focus();

                return false;
            }

            const dropResolved =
                await resolveDropAddress();

            if (!dropResolved) {
                dropAddress.focus();
                return false;
            }

            dropLat =
                getNumber(
                    dropLatitude
                );

            dropLng =
                getNumber(
                    dropLongitude
                );
        }

        if (
            pickupLat === null ||
            pickupLng === null ||
            dropLat === null ||
            dropLng === null
        ) {
            return false;
        }

        const routeReady =
            await calculateRoute();

        if (!routeReady) {
            return false;
        }

        await updateFareDisplay();

        const finalFare =
            getNumber(
                estimatedFare
            );

        if (
            finalFare === null ||
            finalFare <= 0
        ) {
            fareStatus.textContent =
                "Fare could not be calculated.";

            setLocationBadge(
                "Fare required",
                "warning"
            );

            return false;
        }

        if (isEditMode) {
            formSubmitting = true;

            const saveButton =
                document.getElementById(
                    "saveRideRequestBtn"
                );

            if (saveButton) {
                saveButton.disabled = true;

                saveButton.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-2"></span> Updating...';
            }

            HTMLFormElement.prototype.submit.call(
                form
            );

            return true;
        }

        const saveButton =
            document.getElementById(
                "saveRideRequestBtn"
            );

        if (saveButton) {
            saveButton.disabled = true;

            saveButton.innerHTML =
                '<span class="spinner-border spinner-border-sm me-2"></span> Opening Payment...';
        }

        openPaymentModal();

        setTimeout(
            function () {
                if (
                    saveButton &&
                    !formSubmitting
                ) {
                    saveButton.disabled = false;

                    saveButton.innerHTML =
                        '<i class="bi bi-credit-card me-1"></i> Continue to Payment';
                }
            },
            500
        );

        return false;
    }

    window.useCurrentLocation =
        useCurrentLocation;

    window.clearPickup =
        clearPickup;

    window.searchDestination =
        searchDestination;

    window.calculateRoute =
        calculateRoute;

    window.clearDestination =
        clearDestination;

    window.focusDestination =
        focusDestination;

    window.selectPaymentMethod =
        selectPaymentMethod;

    window.changePaymentMethod =
        changePaymentMethod;

    window.continuePayment =
        continuePayment;

    document.addEventListener(
        "DOMContentLoaded",
        function () {
            createMap();
            initializeExistingLocations();

            if (pickupAddress) {
                pickupAddress.addEventListener(
                    "input",
                    function () {
                        if (
                            updatingPickupAddress
                        ) {
                            return;
                        }

                        pickupLatitude.value = "";
                        pickupLongitude.value = "";
                        pickupCityName = "";

                        if (pickupCityField) {
                            pickupCityField.value = "";
                        }

                        if (
                            pickupMarker &&
                            rideMap
                        ) {
                            rideMap.removeLayer(
                                pickupMarker
                            );
                            pickupMarker = null;
                        }

                        setPickupState(
                            false
                        );

                        resetRouteData();

                        pickupStatus.textContent =
                            pickupAddress.value.trim()
                                ? "Pickup address changed. Search or press Enter."
                                : "Enter pickup address or click Current.";

                        setLocationBadge(
                            "Pickup pending",
                            "warning"
                        );
                    }
                );

                pickupAddress.addEventListener(
                    "blur",
                    async function () {
                        if (
                            updatingPickupAddress ||
                            !hasValue(
                                pickupAddress
                            )
                        ) {
                            return;
                        }

                        if (
                            getNumber(
                                pickupLatitude
                            ) === null ||
                            getNumber(
                                pickupLongitude
                            ) === null
                        ) {
                            await resolvePickupAddress();
                        }
                    }
                );

                pickupAddress.addEventListener(
                    "keydown",
                    async function (event) {
                        if (
                            event.key === "Enter"
                        ) {
                            event.preventDefault();

                            if (
                                hasValue(
                                    pickupAddress
                                )
                            ) {
                                await resolvePickupAddress();

                                if (
                                    getNumber(
                                        dropLatitude
                                    ) !== null &&
                                    getNumber(
                                        dropLongitude
                                    ) !== null
                                ) {
                                    await calculateRoute();
                                }
                            }
                        }
                    }
                );
            }

            if (dropAddress) {
                dropAddress.addEventListener(
                    "input",
                    function () {
                        if (
                            updatingDropAddress
                        ) {
                            return;
                        }

                        dropLatitude.value = "";
                        dropLongitude.value = "";
                        dropCityName = "";

                        if (dropCityField) {
                            dropCityField.value = "";
                        }

                        if (
                            dropMarker &&
                            rideMap
                        ) {
                            rideMap.removeLayer(
                                dropMarker
                            );
                            dropMarker = null;
                        }

                        setDropState(
                            false
                        );

                        resetRouteData();

                        dropStatus.textContent =
                            dropAddress.value.trim()
                                ? "Destination entered. Click Search or press Enter."
                                : "Enter destination or click the map.";

                        setLocationBadge(
                            "Destination pending",
                            "warning"
                        );
                    }
                );

                dropAddress.addEventListener(
                    "blur",
                    async function () {
                        if (
                            updatingDropAddress ||
                            !hasValue(
                                dropAddress
                            )
                        ) {
                            return;
                        }

                        if (
                            getNumber(
                                dropLatitude
                            ) === null ||
                            getNumber(
                                dropLongitude
                            ) === null
                        ) {
                            const resolved =
                                await resolveDropAddress();

                            if (resolved) {
                                await calculateRoute();
                            }
                        }
                    }
                );

                dropAddress.addEventListener(
                    "keydown",
                    async function (event) {
                        if (
                            event.key === "Enter"
                        ) {
                            event.preventDefault();

                            if (
                                hasValue(
                                    dropAddress
                                )
                            ) {
                                await searchDestination();
                            }
                        }
                    }
                );
            }

            if (form) {
                form.addEventListener(
                    "submit",
                    validateBeforeSubmit
                );
            }

            const vehicleType =
                document.getElementById(
                    "{{ form.vehicle_type.id_for_label }}"
                );

            if (vehicleType) {
                vehicleType.addEventListener(
                    "change",
                    async function () {
                        await updateFareDisplay();
                    }
                );
            }

            window.addEventListener(
                "resize",
                function () {
                    if (rideMap) {
                        rideMap.invalidateSize();
                    }
                }
            );

            setTimeout(
                function () {
                    if (rideMap) {
                        rideMap.invalidateSize();
                        fitRouteBounds();
                    }
                },
                500
            );
        }
    );
})();
