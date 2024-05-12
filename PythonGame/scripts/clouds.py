import random

# Cloud class, draws clouds in the background, which move
class Cloud:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    # Moves the cloud with its speed
    def update(self):
        self.pos[0] += self.speed

    def render(self, surf, offset=(0, 0)):
        # Determine which position to blit at
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        # Blit the cloud
        surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width(), render_pos[1] % (surf.get_height() + self.img.get_height()) - self.img.get_height()))

# Clouds class, meant to create cloud objects from the Cloud class
class Clouds:
    # Initialize the clouds
    def __init__(self, cloud_images, count=16):
        self.clouds = []
        # Make 16 clouds, with random pos, image (there are 2 different), speed and depth
        for i in range(count):
            self.clouds.append(Cloud((random.random() * 99999, random.random() * 99999), random.choice(cloud_images), random.random() * 0.05 + 0.05, random.random() * 0.6 + 0.2))

        #Sorted by depth
        self.clouds.sort(key=lambda x: x.depth)

    # Updates all the clouds
    def update(self):
        for cloud in self.clouds:
            cloud.update()

    # Blit/Render all the clouds
    def render(self, surf, offset=(0,0)):
        for cloud in self.clouds:
            cloud.render(surf, offset=offset)