#!/bin/bash

echo "=" | head -c 80; echo
echo "NOMINATIM INSTANCE SETUP OPTIONS"
echo "=" | head -c 80; echo
echo

echo "OPTION 1: Use Alternative Public Instance"
echo "  Some public Nominatim instances (may have different rate limits):"
echo "  - https://nominatim.openstreetmap.org (official, rate limited)"
echo "  - Check for community instances at: https://nominatim.org/community/"
echo
echo "  To use:"
echo "    export NOMINATIM_URL='https://your-instance.com'"
echo

echo "OPTION 2: Self-Hosted Nominatim (Docker)"
echo "  This requires:"
echo "  - Docker installed"
echo "  - ~50GB disk space"
echo "  - 4GB+ RAM"
echo
echo "  Quick setup:"
echo "    docker run -d \\"
echo "      --name nominatim \\"
echo "      -p 8080:8080 \\"
echo "      -e PBF_URL=https://download.geofabrik.de/asia/afghanistan-latest.osm.pbf \\"
echo "      -e REPLICATION_URL=https://download.geofabrik.de/asia/afghanistan-updates/ \\"
echo "      mediagis/nominatim:latest"
echo
echo "  Then set:"
echo "    export NOMINATIM_URL='http://localhost:8080'"
echo

echo "OPTION 3: Use Alternative Geocoding Service"
echo "  - Photon API: https://photon.komoot.io (different API format)"
echo "  - Mapbox Geocoding API (requires API key)"
echo "  - Google Geocoding API (requires API key)"
echo

echo "=" | head -c 80; echo
echo "RECOMMENDED: Test with current setup first"
echo "=" | head -c 80; echo
echo "The code now supports NOMINATIM_URL environment variable."
echo "You can test with a different instance by setting it before running tests."
echo
