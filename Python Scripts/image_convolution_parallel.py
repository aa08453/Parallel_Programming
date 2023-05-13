
import multiprocessing
from PIL import Image
from IPython.display import display

# drive.mount('/content/drive')

#takes a path to an image and loads it into a list (length is number of rows) of list (length is number of pixels per row) of tuples of rgb values
def load_img(path):
  image = Image.open(path)
  
  pixels = image.load()
  picture = []
  for y in range(image.height):
    picture.append([])
    for x in range(image.width):
      picture[-1].append(pixels[x, y])
  return picture

def build_img(pixels):
  new_img = Image.new("RGB", (len(pixels[0]), len(pixels)))
  new_img.putdata([pixels[x][y] for x in range(len(pixels[0])) for y in range(len(pixels))])
  ratio = len(pixels[0])//len(pixels)
  resized_img = new_img.resize((800, 800*ratio))
  display(resized_img)

def convolve_pixel(img,coords,kernel):
  x,y = coords
  ker_h,ker_w = len(kernel),len(kernel[0])
  img_h,img_w = len(img),len(img[0])

  left = max(0, x - ker_w//2)
  right = min(img_w-1, x + ker_w//2)
  top = max(0, y - ker_h//2)
  bottom = min(img_h-1, y + ker_h//2)

  if ker_w % 2 == 0:
    right -= 1
  if ker_h % 2 == 0:
    bottom -= 1
  lst = []
  result = 0
  for rgb in range(3):
    for i in range(top, bottom + 1):
        for j in range(left, right + 1):
            ker_x = j - x + ker_w//2
            ker_y = i - y + ker_h//2
            result += img[i][j][rgb]* kernel[ker_y][ker_x]
    lst.append(max(0,min(255,round(result))))
  tup = tuple(lst)
  return tup

def convolve_img(new_img, old_img, cords, size, kernel,num_processes):
  x,y = cords
  w, l = size
  for i in range(y, y+l):
    for j in range(x, x+w):
        new_img[i][j] = convolve_pixel(old_img, (i, j), kernel)
  return new_img

import random

from multiprocessing import Pool

def process_sub_image(old_img, sub_img, kernel):
  sub_x, sub_y, sub_w, sub_l = sub_img
  sub_conv_img = [[(0,0,0) for _ in range(sub_w)] for _ in range(sub_l)]
  for i in range(sub_y, sub_y+sub_l):
    for j in range(sub_x, sub_x+sub_w):
      sub_conv_img[i-sub_y][j-sub_x] = convolve_pixel(old_img, (i, j), kernel) #a pixel in old_img is slightly offset from pixel in sub_img (by factor k//2. k//2?) # convolve each pixel in the sub-image
  return sub_img, sub_conv_img

def parr_convolve_img(new_img, old_img, cords, size, kernel, num_processes):
  x,y = cords
  w,l = size
  step_x = w // num_processes  # calculate the width of each sub-image
  sub_images = []
  for i in range(num_processes):
    sub_x = x + i*step_x  # calculate the starting x coordinate of the sub-image
    if i < num_processes-1:
      sub_w = step_x #start from a bit before the chunk so u have all info needed
    else:
      sub_w = w - i*step_x  # calculate the width of the sub-image
    sub_images.append((sub_x, y, sub_w, l))  # store the coordinates and size of each sub-image in a list

  with Pool(num_processes) as pool:
    results = []
    for sub_img in sub_images:
      result = pool.apply_async(process_sub_image, (old_img, sub_img, kernel))  # create a new process for each sub-image
      results.append(result)

    for i, result in enumerate(results):
      sub_img, sub_conv_img = result.get()
      sub_x, sub_y, sub_w, sub_l = sub_img
      for j in range(sub_l):
        for k in range(sub_w):
          new_img[sub_y+j][sub_x+k] = sub_conv_img[j][k]  # copy the convolved sub-image back into the main image
          
  return new_img

from time import time

#find average time over a given number of runs of convolving the image of using the given convolution function.
def calculateConvolveTime(func,new_image,cords,size,kernel,num_processes,runs):
  totalTime = 0 #store total time across all runs
  for run in range(runs):
    image = [[(random.randint(0,255),random.randint(0,255),random.randint(0,255)) for j in range(size[0])] for i in range(size[0])]
    start_time = time()
    func(new_image,image,cords,size,kernel,num_processes)
    end_time = time()
    print("run", run+1, "of size", size, "finished")
    totalTime += end_time - start_time #add the time taken to run the given convolve function
  return totalTime/runs #return average time

import matplotlib.pyplot as plt

def analyse():
  sizes = [5,25,100,400,600, 800, 1000] #the different list sizes
  # sizes = [5,25,100] #the different list sizes
  sic_times = [] #to store the avg time taken for the different lists for Sequential Image Convolution
  pic_times = [] #to store the avg time taken for the different lists for Parallel Image Convolution

  runs = 10 #number of runs the time is averaged over
  kernel = [[random.randint(0,13)/100 for j in range(3)] for i in range(3)] #kernel of size 3

  for size in sizes:
    # image = [[(random.randint(0,255),random.randint(0,255),random.randint(0,255)) for j in range(size)] for i in range(size)]
    new_image = [[0 for j in range(size)] for i in range(size)]
    sic_times.append(calculateConvolveTime(convolve_img,new_image,(0,0),(size,size),kernel,2,runs))
    pic_times.append(calculateConvolveTime(parr_convolve_img,new_image,(0,0),(size,size),kernel,2,runs))

  print("Sequential Image Convolution times: ", sic_times)
  print("Parallel Image Convolution times: ", pic_times)
  sizes2 = [size**2 for size in sizes]
  #plot graph of time against number of items
  plt.plot(sizes2, sic_times, label="Sequential Image Convolution")
  plt.plot(sizes2, pic_times, label="Parallel Image Convolution")

  plt.legend(loc="upper left")
  plt.xlabel('Image Size (Number of Pixels)')
  plt.ylabel('Average Convolution Time')
  plt.show()

def analyse2():
  sizes = [i for i in range(3,26,2)] #the different list sizes
  sic_times = [] #to store the avg time taken for the different lists for Sequential Image Convolution
  pic_times = [] #to store the avg time taken for the different lists for Parallel Image Convolution

  runs = 5  #number of runs the time is averaged over
  cords = (0,0)
  image = [[(random.randint(0,255),random.randint(0,255),random.randint(0,255)) for j in range(75)] for i in range(75)]
  new_image = [[0 for j in range(len(image))] for i in range(len(image))]
  size = len(image)

  for area in sizes:
    kernel = [[random.randint(0,50)/100 for j in range(area)] for i in range(area)] 
    sic_times.append(calculateConvolveTime(convolve_img,new_image,cords,(size,size),kernel,2,runs))
    pic_times.append(calculateConvolveTime(parr_convolve_img,new_image,cords,(size,size),kernel,2,runs))

  print("Sequential Image Convolution times: ", sic_times)
  print("Parallel Image Convolution times: ", pic_times)

  sizes = [size**2 for size in sizes]
  #plot graph of time against number of items
  plt.plot(sizes, sic_times, label="Sequential Image Convolution")
  plt.plot(sizes, pic_times, label="Parallel Image Convolution")

  plt.legend(loc="upper left")
  plt.xlabel('Kernel Sizes (Total Area)')
  plt.ylabel('Average Convolution Time')
  plt.show()

if __name__ == '__main__':
    multiprocessing.freeze_support()
    analyse()
    analyse2()
