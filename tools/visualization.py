import matplotlib
import matplotlib.pyplot as plt

from db.summoner import Elo


def show_3d(data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    xs = data[:,0]
    ys = data[:,1]
    zs = data[:,2]

    labels = data[:,3]
    colors = ['brown', 'gray', 'orange', 'blue', 'red', 'black']
    cmap = matplotlib.colors.ListedColormap(colors)

    ax.scatter(xs, ys, zs, c=labels, cmap=cmap)

    ax.set_xlabel('N Matches')
    ax.set_ylabel('KDA')
    ax.set_zlabel('Dmg')

    plt.show()

def show_2d(data, axes):
    data = data.loc[:, axes]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel(axes[0], fontsize=12)
    ax.set_ylabel(axes[1], fontsize=12)
    ax.grid(True, linestyle='-', color='0.75')

    xs = data.iloc[:,0]
    ys = data.iloc[:,1]
    labels = data.iloc[:,2]

    #colors = ['brown', 'gray', 'orange', 'blue', 'red', 'black']
    colors = ['brown', 'gray', 'orange', 'cyan', 'blue']
    cmap = matplotlib.colors.ListedColormap(colors)
    scatter = ax.scatter(xs, ys, c=labels, cmap=cmap)

    cbar = plt.colorbar(scatter)
    cbar.ax.get_yaxis().set_ticks([])
    for j, lab in enumerate(Elo.elos_list(limited=True)):
        cbar.ax.text(.5, (2 * j + 1) / 10.0, lab, va='center')

    plt.show()
