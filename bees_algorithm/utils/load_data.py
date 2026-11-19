
#AI to load data
from pathlib import Path
from bees_algorithm.utils.exceptions import DataError


def load_data(file):

    city_coordinates = {}

    # Store the expected header information
    headers = {
        "NAME": None,
        "TYPE": None,
        "DIMENSION": None,
        "EDGE_WEIGHT_TYPE": None
    }

    node_section_found = False
    dimension = None

    # Get filename without .tsp
    expected_name = Path(file).stem

    try:
        with open(file, "r") as f:

            for line in f:

                line = line.strip()

                # Ignore empty lines
                if not line:
                    continue

                # Stop at EOF
                if line == "EOF":
                    break

                # Check whether we reached the coordinate section
                if line == "NODE_COORD_SECTION":
                    node_section_found = True
                    continue

                # Before the coordinate section: read headers
                if not node_section_found:

                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip()

                        if key in headers:
                            headers[key] = value

                    continue

                # After NODE_COORD_SECTION: read city coordinates
                parts = line.split()

                # Each coordinate row must have exactly 3 fields
                if len(parts) != 3:
                    raise DataError("Invalid coordinate row")

                # Convert all three fields to numbers
                try:
                    city_id = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])

                except ValueError:
                    raise DataError("Coordinate row contains non-numeric values")

                # Check for duplicate city IDs
                if city_id in city_coordinates:
                    raise DataError("Duplicate city ID")

                # Store coordinates
                city_coordinates[city_id] = [x, y]

    except OSError as e:
        raise DataError(f"Could not read file: {e}")

    # Validate that all required headers exist
    for key, value in headers.items():
        if value is None:
            raise DataError(f"Missing header: {key}")

    # Validate NAME
    if headers["NAME"] != expected_name:
        raise DataError("NAME does not match filename")

    # Validate TYPE
    if headers["TYPE"] != "TSP":
        raise DataError("TYPE must be TSP")

    # Validate EDGE_WEIGHT_TYPE
    if headers["EDGE_WEIGHT_TYPE"] != "EUC_2D":
        raise DataError("EDGE_WEIGHT_TYPE must be EUC_2D")

    # Validate DIMENSION
    try:
        dimension = int(headers["DIMENSION"])
    except ValueError:
        raise DataError("DIMENSION must be an integer")

    # Validate that NODE_COORD_SECTION exists
    if not node_section_found:
        raise DataError("Missing NODE_COORD_SECTION")

    # Validate number of cities
    if len(city_coordinates) != dimension:
        raise DataError("Number of cities does not match DIMENSION")

    # Validate city IDs are exactly 1 through dimension
    expected_ids = set(range(1, dimension + 1))

    if set(city_coordinates.keys()) != expected_ids:
        raise DataError("City IDs must be exactly 1..DIMENSION")

    return city_coordinates


"""
FILE_DETAILS = ["NAME", "TYPE", "COMMENT", "EDGE_WEIGHT_TYPE", "NODE_COORD_SECTION"]


def load_data(file):
    with open(file, "r") as f:

        city_coordinates = {}
        processed_cities = 0
        cities = 0
        
        while True:
            line = f.readline()

            # Break condition
            if line.strip() == "EOF":
                f.close()
                if cities == processed_cities:
                    return city_coordinates
                else:
                    raise DataError("The no. of cities extracted did not match")
            elif any(detail in line for detail in FILE_DETAILS): #if any of the words are in the line you are at
                #any: if at least one True 
                continue
            elif "DIMENSION" in line:
                cities = int(line.split(":")[1])
            else:
                city, x, y = line.split()
                city, x, y = map(float, (city, x, y))
                city_coordinates[city] = [x, y]
                processed_cities += 1

    return city_coordinates

"""