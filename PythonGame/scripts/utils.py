import os

import pygame

# path where i keep all my images
BASE_IMG_PATH = 'data/images/'

# function for loading images
def load_image(path):
    img = pygame.image.load(BASE_IMG_PATH + path).convert()             # load the image with pygames built in function, it loads with the basepath where i keep all my images and then the specific path for the singular image, then convert to convert all the pixel to none alpha values, which has to do with opacity.
    img.set_colorkey((0,0,0))                                           # the colorkey is used to ignore a specific color, in this case black to make the image transpararent in certant places
    return img                                                          # then reeturn the loaded image

# function for loading multiple images, doesn't use the load_image function so it doesn't get the colorkey, then loads one image at a time and places it in an array which is then returned
def load_images_without_colorkey(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):           # sorted is used to ensure that all the images is placed in the right order
        images.append(pygame.image.load(BASE_IMG_PATH + (path + '/' + img_name)).convert())
    return images

# function for loading multiple images, uses the load_image function, then loads one image at a time and places it in an array which is then returned
def load_images(path):
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

# animation class used to animate characters and particles, works by flipping through a bunch of images
class Animation:
    def __init__(self, images, img_dur=5, loop=True):                       #img_dur is the time it stays on the same image, loop is if it should keep to loop through the images or just do it once
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    # update function to flip through the images, works by increasing the frame(which image it is on) until it has looped through all the images, if the self.loop is True then it will 
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))              # this adds one frame every time and loops infinitely
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)                      # this also adds a frame every time, but doesn't loop, and also says when it is done
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    # returns the image that is being displayed
    def img(self):
        return self.images[int(self.frame / self.img_duration)]