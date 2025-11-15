function createMarkerIcon(name) {
    const shortName = name.length > 18 ? name.substring(0, 18) + "…" : name;

    const svg = `
        <svg xmlns="http://www.w3.org/2000/svg" width="170" height="55">
            <rect x="0" y="0" rx="28" ry="28" width="170" height="55"
                  fill="#0B7832" stroke="#055022" stroke-width="2"/>
            <g transform="translate(10, 10)">
                <circle cx="17" cy="17" r="16" fill="white"/>
                <text x="17" y="24" text-anchor="middle"
                      font-size="22" font-weight="bold"
                      fill="#0B7832">&#9851;</text>
            </g>
            <text x="60" y="32" font-size="16" fill="white" font-weight="bold">
                ${shortName}
            </text>
        </svg>
    `;

    return {
        url: "data:image/svg+xml;charset=UTF-8," + encodeURIComponent(svg),
        scaledSize: new google.maps.Size(170, 55)
    };
}
