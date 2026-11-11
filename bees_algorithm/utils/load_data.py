from bees_algorithm.utils.exceptions import DataError

FILE_DETAILS = ["NAME", "TYPE", "COMMENT", "EDGE_WEIGHT_TYPE", "NODE_COORD_SECTION"]


def load_data(file):
    with open(file, "r") as f:

        city_coordinates = {}
        processed_cities = 0
        cities = 0

        while True:
            line = f.readline()

            # Break condition
            if line == "EOF\n":
                f.close()
                if cities == processed_cities:
                    return city_coordinates
                else:
                    raise DataError("The no. of cities extracted did not match")
            elif any(detail in line for detail in FILE_DETAILS):
                continue
            elif "DIMENSION" in line:
                cities = int(line.split(":")[1])
            else:
                city, x, y = line.split()
                x, y = map(float, (x, y))
                city_coordinates[city] = [x, y]
                processed_cities += 1
