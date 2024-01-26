# maze_generator.py

import os.path
import pathlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch

from mazelib import Maze
from Prims import Prims

CACHE_DIR = os.path.abspath(os.path.join(pathlib.Path(__file__).parent.resolve(), '..', 'cache'))
FIGSIZE = (5,5)

def use_run(codes, vertices, run):
    """Helper method for plotXKCD. Updates path with newest run."""
    if run:
        codes += [Path.MOVETO] + [Path.LINETO] * (len(run) - 1)
        vertices += run

def plotXKCD(grid, start=None, end=None, outfile=None, color='black', title=None):
    """ Generate an XKCD-styled line-drawn image of the maze. """
    H = len(grid)
    W = len(grid[0])
    h = (H - 1) // 2
    w = (W - 1) // 2

    grid = grid.astype(float)
    NODE = 2
    if start is not None:
        grid[start[0], start[1]] = NODE
    if end is not None:
        grid[end[0], end[1]] = NODE

    with plt.xkcd():
        fig = plt.figure(figsize=FIGSIZE)
        ax = fig.add_subplot(111)

        vertices = []
        codes = []
        nodes = []

        # loop over horizontals
        for r,rr in enumerate(range(1, H, 2)):
            run = []
            for c,cc in enumerate(range(1, W, 2)):
                if grid[rr-1,cc] == 1:
                    if not run:
                        run = [(r,c)]
                    run += [(r,c+1)]
                else:
                    if grid[rr-1,cc] == NODE:
                        nodes.append((r,c+0.5))
                    use_run(codes, vertices, run)
                    run = []
            use_run(codes, vertices, run)

        # grab bottom side of last row
        run = []
        for c,cc in enumerate(range(1, W, 2)):
            if grid[H-1,cc] == 1:
                if not run:
                    run = [(H//2,c)]
                run += [(H//2,c+1)]
            else:
                if grid[H-1,cc] == NODE:
                    nodes.append((H//2,c+0.5))
                use_run(codes, vertices, run)
                run = []
            use_run(codes, vertices, run)

        # loop over verticals
        for c,cc in enumerate(range(1, W, 2)):
            run = []
            for r,rr in enumerate(range(1, H, 2)):
                if grid[rr,cc-1] == 1:
                    if not run:
                        run = [(r,c)]
                    run += [(r+1,c)]
                else:
                    if grid[rr,cc-1] == NODE:
                        nodes.append((r+0.5,c))
                    use_run(codes, vertices, run)
                    run = []
            use_run(codes, vertices, run)

        # grab far right column
        run = []
        for r,rr in enumerate(range(1, H, 2)):
            if grid[rr,W-1] == 1:
                if not run:
                    run = [(r,W//2)]
                run += [(r+1,W//2)]
            else:
                if grid[rr,W-1] == NODE:
                    nodes.append((r+0.5,W//2))
                use_run(codes, vertices, run)
                run = []
            use_run(codes, vertices, run)

        vertices = np.array(vertices, float)
        path = Path(vertices, codes)

        # for a line maze
        pathpatch = PathPatch(path, facecolor='None', edgecolor=color, lw=2)
        ax.add_patch(pathpatch)

        # hide axis and labels
        ax.axis('off')
        ax.dataLim.update_from_data_xy([(-0.1,-0.1), (h + 0.1, w + 0.1)])
        # ax.autoscale_view()
        if title is not None:
            plt.title(title, fontsize=20)
        
        plt.tight_layout()

        for node in nodes:
            plt.plot(node[0], node[1], '*', markersize=11, color='red')

        if outfile is not None:
            plt.savefig(outfile)
        else:
            plt.show()
        plt.close()

def showPNG(grid, start=None, end=None, shortest_path=None, outfile=None):
    """Generate a simple image of the maze."""
    plt.figure(figsize=FIGSIZE)

    if start is not None:
        grid[start[0], start[1]] = 0.
    if end is not None:
        grid[end[0], end[1]] = 0.

    plt.imshow(grid, cmap=plt.cm.binary, interpolation='nearest')
    # plot start and end
    if start is not None:
        plt.plot(start[1], start[0], '*', markersize=11, color='red')
    if end is not None:
        plt.plot(end[1], end[0], '*', markersize=11, color='green')
    # plot the shortest path
    if shortest_path is not None:
        plt.plot([p[1] for p in shortest_path], [p[0] for p in shortest_path], linewidth=3, color='cyan')
    plt.xticks([]), plt.yticks([])
    if outfile is not None:
        plt.savefig(outfile)
    plt.close()

def render(outfile, title=None):
    m = Maze()
    m.generator = Prims(9, 9)
    m.generate()
    m.generate_entrances()
    plotXKCD(m.grid.copy(), start=m.start, end=m.end, outfile=outfile, title=title)

def main(outdir):
    for name in ['Robin', 'Jordan']:
        fnm = 'maze_{}.png'.format(name[0].lower())
        outfile = os.path.join(outdir, fnm)
        # title = "{}'s maze".format(name)
        title = None
        render(outfile=outfile, title=title)

if __name__ == '__main__':
    main(CACHE_DIR)
