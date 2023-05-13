#Preamble
import multiprocessing
from time import time
import math
import random
import matplotlib.pyplot as plt

#sequential implementation

def merge(S1, S2):
  S = []
  i = j = 0
  while len(S) < len(S1) + len(S2):
    if j == len(S2) or (i < len(S1) and S1[i] < S2[j]):
      S.append(S1[i])
      i += 1
    else:
      S.append(S2[j])
      j += 1
  return S

def merge_sort(S):
  n = len(S)
  if n < 2:
    return S

  mid = n // 2
  
  S1 = S[0:mid]
  S2 = S[mid:n]

  S1 = merge_sort(S1)
  S2 = merge_sort(S2)

  S = merge(S1, S2)
  return S

#parallel implemenation
def parr_merge_sort(data, num_chunks):
  chunk_size = math.ceil(len(data)/num_chunks)
  chunks = []
  for i in range(num_chunks):
    chunks.append(data[i*chunk_size:(i+1)*chunk_size])

  with multiprocessing.Pool() as pool:
    result = pool.imap_unordered(merge_sort, chunks)
    chunks = []
    for res in result:
      chunks.append(res)

  while len(chunks) > 1:
    new_chunks = []
    for i in range(0, len(chunks), 2):
      new_chunks.append(merge(chunks[i], chunks[i+1] if i+1 < len(chunks) else []))
    chunks = new_chunks
  return chunks[0]

def parr_merge_sort_wrapper(data):
  return parr_merge_sort(data, 8)

#Generate the randomly sorted array of distinct numbers from 1 till size(e.g. 100,000)
def generateArray(size):
  arr = list(range(1,size+1))
  random.shuffle(arr)
  return arr

#find average time over a given number of runs of searching the list (lst) of size sz using the given sorting function.
def calculateSortTime(sorting_func, lstGenerator, size, runs):
  totalTime = 0 #store total time across all runs
  for i in range(runs):
    lst = lstGenerator(size)
    start_time = time()
    sorting_func(lst)
    end_time = time()
    print("run", i+1, "of size", size, "finished")
    totalTime += end_time - start_time #add the time taken to run the given search function
  return totalTime/runs #return average time

def analyse():
    import matplotlib.pyplot as plt

    sizes = [10000, 40000, 100000, 300000, 500000, 800000, 1000000] #the different list sizes
    ms_times = [] #to store the avg time taken for the different lists for linear search
    p_ms_times = [] #to store the avg time taken for the different lists for sentinel search

    runs = 10 #number of runs the time is averaged over

    for size in sizes:
        lst = generateArray(size)
        ms_times.append(calculateSortTime(merge_sort, generateArray, size, runs))
        p_ms_times.append(calculateSortTime(parr_merge_sort_wrapper, generateArray, size, runs))



    print("Merge sort sorting times: ", ms_times)
    print("Parallel Merge sort sorting times: ", p_ms_times)

    #plot graph of time against number of items
    plt.plot(sizes, ms_times, label="Merge Sort")
    plt.plot(sizes, p_ms_times, label="Parallel Merge Sort")

    plt.legend(loc="upper left")
    plt.xlabel('Number of Items')
    plt.ylabel('Average Sorting Time')
    plt.show()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    analyse()