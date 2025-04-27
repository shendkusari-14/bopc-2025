#! /usr/bin/env python
import csv

from re import U
import numpy as np
import argparse
import time
from multiprocessing import Pool, TimeoutError
from julia_curve import c_from_group
from dataclasses import dataclass


# Update according to your group size and number (see TUWEL)
GROUP_SIZE   = 2
GROUP_NUMBER = 3

# do not modify BENCHMARK_C
BENCHMARK_C = complex(-0.2, -0.65)

def compute_julia_set_sequential(xmin, xmax, ymin, ymax, im_width, im_height, c):

    zabs_max = 10
    nit_max = 300

    xwidth  = xmax - xmin
    yheight = ymax - ymin

    julia = np.zeros((im_width, im_height))
    for ix in range(im_width):
        for iy in range(im_height):
            nit = 0
            # Map pixel position to a point in the complex plane
            z = complex(ix / im_width * xwidth + xmin,
                        iy / im_height * yheight + ymin)
            # Do the iterations
            while abs(z) <= zabs_max and nit < nit_max:
                z = z**2 + c
                nit += 1
            ratio = nit / nit_max
            julia[ix,iy] = ratio

    return julia


@dataclass
class PatchTask:
    x_start: int
    y_start: int
    patch_size: int
    size: int
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    c: complex

def patch_worker(task: PatchTask):
    #Computes a single patch of the Julia set
    #x_start, y_start, patch_size, size, xmin, xmax, .ymin, ymax, c = task
    zabs_max = 10
    nit_max = 300

    # Maybe try different calculations?
    xwidth = task.xmax - task.xmin
    yheight = task.ymax - task.ymin

    patch_width = min(task.patch_size, task.size - task.x_start)
    patch_height = min(task.patch_size, task.size - task.y_start)
    #print(patch_height)
    patch_result = np.zeros((patch_width, patch_height))

    
        
    for ix in range(patch_width):
        for iy in range(patch_height):
            nit = 0
            zx = (task.x_start + ix) / task.size * xwidth + task.xmin
            zy = (task.y_start + iy) / task.size * yheight + task.ymin
            z = complex(zx, zy)
            while abs(z) <= zabs_max and nit < nit_max:
                z = z**2 + task.c
                nit += 1
            patch_result[ix, iy] = nit / nit_max


    # Maybe log patch? (for checking)
    # print(f'Patch done at ({task.x_start},{task.y_start})')



    return (task.x_start, task.y_start, patch_result)


def compute_julia_in_parallel(size, xmin, xmax, ymin, ymax, patch, nprocs, c):
    task_list = []
    for x in range(0, size, patch):
        for y in range(0, size, patch):
            task_list.append(PatchTask(x, y, patch, size, xmin, xmax, ymin, ymax, c))


    julia_img = np.zeros((size, size))

   
   
    with Pool(processes=nprocs) as pool:

        # print("Starting pool map...")

        completed_patches = pool.map(patch_worker, task_list, chunksize=1)

    for x_start, y_start, patch_data in completed_patches:
        w, h = patch_data.shape
        julia_img[x_start:x_start+w, y_start:y_start+h] = patch_data

    return julia_img



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--size", help="image size in pixels (square images)", type=int, default=500)
    parser.add_argument("--xmin", help="", type=float, default=-1.5)
    parser.add_argument("--xmax", help="", type=float, default=1.5)
    parser.add_argument("--ymin", help="", type=float, default=-1.5)
    parser.add_argument("--ymax", help="", type=float, default=1.5)
    parser.add_argument("--group-size", help="", type=int, default=None)
    parser.add_argument("--group-number", help="", type=int, default=None)
    parser.add_argument("--patch", help="patch size in pixels (square images)", type=int, default=20)
    parser.add_argument("--nprocs", help="number of workers", type=int, default=1)
    parser.add_argument("--draw-axes", help="Whether to draw axes", action="store_true")
    parser.add_argument("-o", help="output file")
    parser.add_argument("--benchmark", help="Whether to execute the script with the benchmark Julia set", action="store_true")
    args = parser.parse_args()

    #print(args)
    if args.group_size is not None:
        GROUP_SIZE = args.group_size
    if args.group_number is not None:
        GROUP_NUMBER = args.group_number

    # assign c based on mode
    c = None
    if args.benchmark:
        c = BENCHMARK_C 
    else:
        c = c_from_group(GROUP_SIZE, GROUP_NUMBER) 

    stime = time.perf_counter()
    julia_img = compute_julia_in_parallel(
        args.size,
        args.xmin, args.xmax, 
        args.ymin, args.ymax, 
        args.patch,
        args.nprocs,
        c)
    rtime = time.perf_counter() - stime

    print(f"{args.size};{args.patch};{args.nprocs};{rtime}")

    mode = 'benchmark' if args.benchmark else 'student'
    with open(f'benchmark_data_{mode}.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([args.size, args.patch, args.nprocs, round(rtime, 6)])

    if not args.o is None:
        import matplotlib
        matplotlib.use('agg')
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        fig, ax = plt.subplots()
        ax.imshow(julia_img, interpolation='nearest', cmap=plt.get_cmap("hot"))

        if args.draw_axes:
            # set labels correctly
            im_width = args.size
            im_height = args.size
            xmin = args.xmin
            xmax = args.xmax
            xwidth = args.xmax - args.xmin
            ymin = args.ymin
            ymax = args.ymax
            yheight = args.ymax - args.ymin

            xtick_labels = np.linspace(xmin, xmax, 7)
            ax.set_xticks([(x-xmin) / xwidth * im_width for x in xtick_labels])
            ax.set_xticklabels(['{:.1f}'.format(xtick) for xtick in xtick_labels])
            ytick_labels = np.linspace(ymin, ymax, 7)
            ax.set_yticks([(y-ymin) / yheight * im_height for y in ytick_labels])
            ax.set_yticklabels(['{:.1f}'.format(-ytick) for ytick in ytick_labels])
            ax.set_xlabel("Imag")
            ax.set_ylabel("Real")
        else:
            # disable axes
            ax.axis("off") 

        plt.tight_layout()
        plt.savefig(args.o, bbox_inches='tight')
        plt.show()