# Parse the TXT file and validate the polygon.

def parse_polygon_file(file_path):
    """
    Parses the uploaded text file and extracts metadata and polygon coordinates.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    data = {"details": {}, "coordinates": []}
    metadata_section = True

    for line in lines:
        line = line.strip()
        data.details += line

        # Skip delimiters and empty lines
        if line.startswith("---") or line == "":
            continue

        if metadata_section:
            if line.startswith("LATITUDE LONGITUDE"):
                metadata_section = False  # Move to the coordinates section
        else:
            # Parse coordinates
            parts = line.split()
            if len(parts) == 2:  # Ensure valid coordinates
                lat, lng = map(float, parts)
                data["coordinates"].append((lat, lng))

    # Ensure polygon is closed
    if data["coordinates"][0] != data["coordinates"][-1]:
        data["coordinates"].append(data["coordinates"][0])

    return data