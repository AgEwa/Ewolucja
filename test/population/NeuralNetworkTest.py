from src.population.Specimen import Specimen
from src.typess import Coord
from utils.utils import generate_hex


def test_genome_to_NN():
    genome = [generate_hex() for _ in range(10)]
    net = Specimen(0, Coord(0, 0), genome).brain
    print(net.neurons)


def main():
    test_genome_to_NN()

    return


if __name__ == '__main__':
    main()
