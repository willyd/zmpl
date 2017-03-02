import numpy as np
import zmpl
zmpl.options['server_auto_start'] = False
from zmpl import pyplot as zplt
# from matplotlib import pyplot as zplt


def main():
    fig = zplt.figure(1)
    ax = fig.add_subplot(111)
    # ax.hold(True)
    # ax.imshow(np.random.random((100, 100, 3)))
    zplt.plot(range(100), 'k-')
    # ax.hold(False)
    zplt.show()
    # print(dir(fig))
    # print(dir(ax))


if __name__ == '__main__':
    main()
