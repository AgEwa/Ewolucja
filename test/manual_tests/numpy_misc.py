import numpy as np


def main():
    np.random.seed(1234)
    field = np.random.randint(0, 100, size=(10, 10))

    potentials = np.argwhere(field == 0)

    result = potentials[np.random.choice(potentials.shape[0])]

    print(field)
    print(potentials)
    print(result)
    print(f'{type(result[0].item())} {result[0].item()} | {type(result[1].item())} {result[1].item()}')

    return


if __name__ == '__main__':
    main()
