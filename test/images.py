import numpy as np
from PIL import Image
from PIL import Image
from matplotlib import cm


def main():
    np.random.seed(1234)

    field = np.zeros((10, 10), dtype=np.int16)
    potentials = np.argwhere(field == 0)
    selected = potentials[np.random.choice(potentials.shape[0], 10, replace=False)]
    field[selected[:, 0], selected[:, 1]] = 1
    print(field)

    im = Image.fromarray(np.uint8(cm.gist_earth(field) * 255))
    im.convert('RGB').save("your_file.jpeg")

    return


if __name__ == '__main__':
    main()
