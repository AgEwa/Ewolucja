import os
import uuid

import imageio.v2 as imageio
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

WIDTH = 100
HEIGHT = 100
POPULATION = 100


def generate(width, height, pop):
    np.random.seed(1234)

    field = np.zeros((width, height), dtype=np.int16)
    potentials = np.argwhere(field == 0)
    selected = potentials[np.random.choice(potentials.shape[0], pop, replace=False)]
    field[selected[:, 0], selected[:, 1]] = 1

    return field


def make_plot(data, folder_name, target_name):
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    field_to_color = np.ma.masked_where(data == 0, data)

    fig, ax = plt.subplots()
    cmap = mpl.colormaps['gray']
    cmap.set_bad(color='white')
    ax.matshow(field_to_color, cmap=cmap)
    ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labeltop=False, labelright=False,
                   labelleft=False)

    name = os.path.join(folder_name, f'{target_name}.png')

    plt.savefig(name)
    plt.close()

    return name


def to_gif(target_name, filenames):
    with imageio.get_writer(f'{target_name}.gif', mode='I') as writer:
        for filename in filenames:
            image = imageio.imread(filename)
            writer.append_data(image)


def main():
    field = generate(WIDTH, HEIGHT, POPULATION)

    folder_name = 'frames'
    uid = uuid.uuid4()

    filenames = [make_plot(field, folder_name, f'gif_{uid}_frame_0')]

    for i in range(POPULATION):
        # do sth here

        potentials = np.argwhere(field != 0)
        sl = potentials[np.random.choice(potentials.shape[0])]
        field[sl[0], sl[1]] = 0

        filenames.append(make_plot(field, folder_name, f'gif_{uid}_frame_{i + 1}'))

    to_gif(os.path.join(folder_name, f'gif_{uid}'), filenames)

    return


if __name__ == '__main__':
    main()
