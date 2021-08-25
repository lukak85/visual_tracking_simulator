import os
from PIL import Image
import numpy as np

path = '/path/to/the/folder/'
f = open("groundtruth.txt","w+")

filepaths = []

for filename in os.listdir(path):

    filepaths.append(path+filename)


for filename in sorted(filepaths):

    if filename.endswith(".jpg"):

        print(path+filename)

        im = Image.open(filename, 'r')

        top = -1
        left = -1

        right = -1
        bottom = -1

        pixels = im.load()

        image_width, image_height = im.size

        current_image_RLE = []

        # Za bounding box
        for y in range(image_height):
            for x in range(image_width):
                r = pixels[x,y][0]
                g = pixels[x,y][1]
                b = pixels[x,y][2]

                color = r + g + b
                
                # To pomeni, da je ta stvar del maske, vse kar je temneje rečemo da ni
                if color > 255:
                    if top == -1:
                        top = y
                    if left == -1 or left > x:
                        left = x
                    if right == -1 or right < x:
                        right = x
                    
                    bottom = y
        
        bbox_x = max(0, left)
        bbox_y = max(0, top)
        bbox_width = max(0, right - left)
        bbox_height = max(0, bottom - top)

        current_image_RLE_string = "m" + str(bbox_x) + "," + str(bbox_y) + "," + str(bbox_width) + "," + str(bbox_height) + ","

        current_number_of_bw_pixels = 0
        isBlack = True

        # RLE znotraj tega bounding boxa
        for y in range(bbox_y, bbox_y + bbox_height):

            for x in range(bbox_x, bbox_x + bbox_width):
                r = pixels[x,y][0]
                g = pixels[x,y][1]
                b = pixels[x,y][2]

                color = r + g + b
                
                # To pomeni, da je ta stvar del maske, vse kar je temneje rečemo da ni
                if color > 255:
                    # Če je do zdaj bilo črno, spremenim encoding na belo, in štejem koliko belih je blo do zdaj
                    if isBlack:
                        isBlack = False
                        current_image_RLE.append(str(current_number_of_bw_pixels))
                        current_number_of_bw_pixels = 1
                    else:
                        current_number_of_bw_pixels = current_number_of_bw_pixels + 1
                else:
                    if not isBlack:
                        isBlack = True
                        current_image_RLE.append(str(current_number_of_bw_pixels))
                        current_number_of_bw_pixels = 1
                    else:
                        current_number_of_bw_pixels = current_number_of_bw_pixels + 1
        

        current_image_RLE_string = current_image_RLE_string + ",".join(current_image_RLE) + "\n"

        f.write(current_image_RLE_string)

        continue
    else:
        continue

f_anchor = open("anchor.value","w+")

for i in range(0, len(filepaths)):
    if i % 50 == 0 or i == len(filepaths) - 1:
        f_anchor.write("1\n")
    else:
        f_anchor.write("0\n")