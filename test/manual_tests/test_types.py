from src.world.LocationTypes import Coord, Conversions


def main():
    coord = Coord(10, -10)
    print(coord)
    print(Conversions.coord_as_direction(coord))

    pass


if __name__ == '__main__':
    main()
