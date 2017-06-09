from mpl_toolkits.mplot3d import Axes3D
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pylab

def show_3d(data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')


    xs = data[:,0]
    ys = data[:,1]
    zs = data[:,2]
    colors = data[:,3]
    ax.scatter(xs, ys, zs, c=colors)

    ax.set_xlabel('N Matches')
    ax.set_ylabel('KDA')
    ax.set_zlabel('Dmg')

    plt.show()

def show_2d(data):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("KDA", fontsize=12)
    ax.set_ylabel("Dmg", fontsize=12)
    ax.grid(True, linestyle='-', color='0.75')
    # colors = ['blue', 'cyan', 'green', 'orange', 'red']
    colors = ['brown', 'gray', 'orange', 'blue', 'red']

    xs = data[:,0]
    ys = data[:,1]
    labels = data[:,2]

    ax.scatter(xs, ys, c=labels, cmap=matplotlib.colors.ListedColormap(colors))

    plt.show()
