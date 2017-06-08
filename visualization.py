from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

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
    xs = data[:,0]
    ys = data[:,1]
    colors = data[:,2]
    plt.scatter(xs, ys, c=colors)

    plt.show()