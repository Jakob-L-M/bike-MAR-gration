function getIcon(num_bikes) {
    const svgIcon = L.divIcon({
        html: `
      <svg
        width="32"
        height="32"
        viewBox="0 0 32 32"
        version="1.1"
        preserveAspectRatio="xMaxYMid meet"
      >
        <circle style="stroke: rgb(8, 8, 181); fill: rgb(8, 0, 241);" cx="16" cy="16" r="15"></circle>
        <circle style="stroke: rgb(0, 0, 0); fill: rgb(255, 255, 255);" cx="16" cy="16" r="11"></circle>
        <text style="fill: rgb(51, 51, 51); font-family: Arial, sans-serif; font-size: 12px; font-weight: 700; text-anchor: middle; dominant-baseline: central;" x="16" y="16">${num_bikes}</text>
      </svg>`,
        className: "svg-icon",
        iconSize: [32, 32],
        iconAnchor: [16, 16],
      });

      return svgIcon
}