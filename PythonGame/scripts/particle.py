# Particle class, meant for all types of particles in the game
class Particle:
    # Initialize variabels
    def __init__(self, game, p_type, pos, velocity=[0, 0], frame=0):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self.game.assets['particle/' + p_type].copy()  # Loads all the images for the animations
        self.animation.frame = frame
    
    # Update the particle position untill it dies/ gets removed
    def update(self):
        kill = False
        if self.animation.done:
            kill = True


        self.pos[0] += self.velocity[0] # x pos
        self.pos[1] += self.velocity[1] # y pos

        self.animation.update()

        return kill
    
    # Render the particle
    def render(self, surf, offset=(0,0), gem=False):
        img = self.animation.img()
        if gem: # if it is a gem render it from top left corner and not middle
            surf.blit(img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        else: # else middle
            surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))