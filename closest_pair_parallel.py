#Preamble
import multiprocessing
from time import time
import math
import random
import matplotlib.pyplot as plt

# The sequential implementation code takes great inspiration from the following:
# syphh. (2021, July 24). closest_pair.py [Gist]. GitHub. http://gist.github.com/syphh/b6668694edacf8cc987f89bf1270125c

#sequential implementation
def get_distance(p1, p2):
  return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) 

def merge_closest(y_sorted, pivot, l1, l2, ld, r1, r2, rd):
  p1, p2, d = (l1, l2, ld) if ld < rd else (r1, r2, rd)

  rem = []
  for point in y_sorted:
    if abs(point[0]-pivot[0]) < d:
      rem.append(point)
  
  for i in range(len(rem)):
    for j in range(i+1, len(rem)):
      if abs(rem[j][1] - rem[i][1]) >= d:
        break
      else:
        cur_d = get_distance(rem[i], rem[j])
        if cur_d < d:
          p1, p2, d = rem[i], rem[j], cur_d

  return p1, p2, d

def closest_pair(x_sorted, y_sorted):
  if len(x_sorted) <= 4:
    return brute_force(x_sorted)
  
  mid = len(x_sorted)//2
  pivot = x_sorted[mid]
  x_1 = x_sorted[:mid+1]
  y_1 = []
  x_2 = x_sorted[mid+1:]
  y_2 = []
  for point in y_sorted:
    if point[0] < pivot[0] or (point[0] == pivot[0] and point[1] <= pivot[1]):
      y_1.append(point)
    else:
      y_2.append(point)

  l1, l2, ld = left_closest = closest_pair(x_1, y_1)
  r1, r2, rd = right_closest = closest_pair(x_2, y_2)
  
  return merge_closest(y_sorted, pivot, l1, l2, ld, r1, r2, rd)

def brute_force(A):
  d = None
  for i in range(len(A)):
    for j in range(i+1, len(A)):
      cur_d = get_distance(A[i], A[j])
      
      if d is None or cur_d < d:
        p1, p2, d = A[i], A[j], cur_d
        
  return p1, p2, d

def closest_pair_wrapper(points):
  x_sorted = sorted(points)
  y_sorted = sorted(points, key = lambda x:x[1])
  return closest_pair(x_sorted, y_sorted)

#parallel implementation
def parr_closest_pair(A, n):
  x_sorted = sorted(A)
  y_sorted = sorted(A, key = lambda x:x[1])

  chunk_size = len(A) // n
  upper_limits = [x_sorted[(i+1)*chunk_size - 1] if i < n - 1 else x_sorted[-1] for i in range(n)]

  x_i = [x_sorted[i*chunk_size:(i+1)*chunk_size] if i < n-1 else x_sorted[i*chunk_size:] for i in range(n)]
  y_i = [[] for i in range(n)]

  for point in y_sorted:
    for i, upper_limit in enumerate(upper_limits):
      if point[0] < upper_limit[0] or (point[0] == upper_limit[0] and point[1] <= upper_limit[1]):
        y_i[i].append(point)
        break

  with multiprocessing.Pool() as pool:
    result = pool.imap(worker_func, zip(x_i, y_i))
    chunks = []
    for res in result:
      chunks.append(res)
    
  while len(chunks) > 1:
    new_chunks = []
    y_i = [merge_lsts(y_i[i], y_i[i+1] if i+1 < len(y_i) else []) for i in range(0, len(y_i), 2)]

    for i in range(0, len(chunks), 2):
      if i + 1 < len(chunks):
        new_chunks.append(merge_closest(y_i[i//2], upper_limits[i], *chunks[i], *chunks[i+1]))
      else:
        new_chunks.append(chunks[i])
        
    upper_limits = [upper_limits[i+1] if i + 1 < len(y_i) else upper_limits[i] for i in range(0, len(upper_limits), 2)]
    chunks = new_chunks

  return chunks[0]

def merge_lsts(y_1, y_2):
  i = j = 0
  y_sorted = []

  while i + j < len(y_1) + len(y_2):
    if j == len(y_2) or (i < len(y_1) and y_1[i][1] <= y_2[j][1]):
      y_sorted.append(y_1[i])
      i += 1
    else:
      y_sorted.append(y_2[j])
      j += 1

  return y_sorted

def worker_func(arrayTuple):
  x_sorted = arrayTuple[0]
  y_sorted = arrayTuple[1]
  return closest_pair(x_sorted, y_sorted)

def parr_closest_pair_wrapper(A):
  return parr_closest_pair(A, min(8, len(A)//4))

#Generate Random points across a grid with -100 <= x <= 100 and -100 <= y <= 100
def generatePoints(n):
  points = [(random.randint(-100,100), random.randint(-100,100)) for i in range(n)]
  return points

#find average time over a given number of runs of searching the list (lst) of size sz using the given search function.
def calculateExecutionTime(pair_finder, pointsGenerator, size, runs):
  totalTime = 0 #store total time across all runs
  for i in range(runs):
    points = pointsGenerator(size)
    start_time = time()
    pair_finder(points)
    end_time = time()
    print("run", i+1, "of size", size, "finished")
    totalTime += end_time - start_time #add the time taken to run the given search function
  return totalTime/runs #return average time

def analyse():
    sizes = [10000, 40000, 100000, 300000, 500000, 800000, 1000000] #the different list sizes
    cp_times = [] #to store the avg time taken for the different lists for linear search
    p_cp_times = [] #to store the avg time taken for the different lists for sentinel search

    runs = 10 #number of runs the time is averaged over

    for size in sizes:
        points = generatePoints(size)
        cp_times.append(calculateExecutionTime(closest_pair_wrapper, generatePoints, size, runs))
        p_cp_times.append(calculateExecutionTime(parr_closest_pair_wrapper, generatePoints, size, runs))

    print("Sequential Closest Pair times: ", cp_times)
    print("Parallel Closest Pair times: ", p_cp_times)

    #plot graph of time against number of items
    plt.plot(sizes, cp_times, label="Sequential Closest Pair")
    plt.plot(sizes, p_cp_times, label="Parallel Closest Pair")

    plt.legend(loc="upper left")
    plt.xlabel('Number of Points')
    plt.ylabel('Average Time of Execution')
    plt.show()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    analyse()