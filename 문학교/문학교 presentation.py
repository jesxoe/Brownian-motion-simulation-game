from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import random
import math

app = Ursina()

random.seed(0)
Entity.default_shader = lit_with_shadows_shader

ground = Entity(model='plane', collider='box', scale=900, texture='grass', texture_scale=(4, 4))

editor_camera = EditorCamera(enabled=False, ignore_paused=True)
players = []

player = FirstPersonController(model='cube', z=-10, color=color.orange, origin_y=-.5, speed=20, collider='box')
player.collider = BoxCollider(player, Vec3(0, 1, 0), Vec3(1, 2, 1))
players.append(player)

class Zombie(Entity):
    def __init__(self, **kwargs):
        super().__init__(model='sphere', scale_x=4, scale_y=4, scale_z=4, color=color.red, origin_y=-.5, collider='box',
                         **kwargs)
        self.speed = 50
        self.random_direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()

    def update(self):
        origin = self.world_position + (self.up * .5)
        hit_info = boxcast(origin, direction=self.random_direction, distance=2.5, thickness=(2, 2),
                           traverse_target=scene, ignore=(self,), debug=False)
        if not hit_info.hit:
            self.position += self.random_direction * time.dt * self.speed
        else:
            if self.random_direction[0] >= 0:
                self.random_direction[0] -= 0.5
            else:
                self.random_direction[0] += 0.5
            if self.random_direction[2] >= 0:
                self.random_direction[2] -= 0.5
            else:
                self.random_direction[2] += 0.5

        if random.random() < 0.01:
            self.random_direction = Vec3(random.uniform(-1, 1), 0, random.uniform(-1, 1)).normalized()

        self.position.x = clamp(self.position.x, -ground.scale.x, ground.scale.x)
        self.position.z = clamp(self.position.z, -ground.scale.z, ground.scale.z)

zombie_count = 20

player_start_x = player.x
player_start_z = player.z

zombie_positions = []
for _ in range(zombie_count):
    while True:
        x = random.uniform(player_start_x - 20, player_start_x + 20)
        z = random.uniform(player_start_z - 20, player_start_z + 20)
        valid_position = True

        for pos in zombie_positions:
            if math.dist((x, z), pos) < 5.0:
                valid_position = False
                break

        if valid_position:
            zombie_positions.append((x, z))
            break

for pos in zombie_positions:
    zombie = Zombie(position=(pos[0], 0, pos[1]))

def pause_input(key):
    if key == 'tab':
        editor_camera.enabled = not editor_camera.enabled
        for player in players:
            player.visible_self = editor_camera.enabled
            player.cursor.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = players[0].position
        application.paused = editor_camera.enabled

pause_handler = Entity(ignore_paused=True, input=pause_input)

sun = DirectionalLight()
sun.look_at(Vec3(1, -1, -1))

camera.rotation_x = 90
camera.position = (0, 100, 0)   

Sky()

app.run()
