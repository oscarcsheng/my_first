# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 10:09:43 2018

@author: yando
"""

"""
Environment for 2D car driving.
You can customize this script in a way you want.
View more on [莫烦Python] : https://morvanzhou.github.io/tutorials/
Requirement:
pyglet >= 1.2.4
numpy >= 1.12.1
"""
import numpy as np
import pyglet


pyglet.clock.set_fps_limit(10000)


class CarEnv(object):
    n_sensor = 9
    action_dim = 1
    state_dim = n_sensor
    viewer = None
    viewer_xy = (1000, 1000)
    sensor_max = 150.
    start_point = [950, 500]
    speed = 50.
    dt = 0.1

    def __init__(self, discrete_action=False):
        self.is_discrete_action = discrete_action
        if discrete_action:
            self.actions = [-1, 0, 1]
        else:
            self.action_bound = [-1, 1]

        self.terminal = False
        # node1 (x, y, r, w, l),
        self.car_info = np.array([0, 0, 0, 15, 30], dtype=np.float64)   # car coordination
        self.obstacle_coords = np.array([
            [900, 100],
            [900, 900],
            [700, 900],
            [700, 100],
            [600, 100],
            [600, 300],
            [500, 400],
            [200, 400],
            [200, 200],
            [300, 200],
            [400, 100],
            [100, 200],
            [100, 500],
            [600, 500],
            [700, 600],
            [600, 700],
            [700, 800],
            [600, 700],
            [400, 700],
            [400, 900],
            [400, 700],
            [100, 700],
            [100, 900],            
        ])
        self.obstacle_coords1 = np.array([
            [300, 300],
            [400, 300],
            [500, 200],
            [500, 1],
            [1,1],
            [1, 600],
            [500, 600],
            [1, 600],
            [1, 999],
            [200, 999],
            [200, 800],
            [300, 800],
            [300, 999],
            [500, 999],
            [500, 800],
            [600, 999],
            [999, 999],
            [999, 1],
            [800, 1],
            [800, 800],
        ])
        self.sensor_info = self.sensor_max + np.zeros((self.n_sensor, 3))  # n sensors, (distance, end_x, end_y)

    def step(self, action):
        if self.is_discrete_action:
            action = self.actions[action]
        else:
            action = np.clip(action, *self.action_bound)[0]
        self.car_info[2] += action * np.pi/30  # max r = 6 degree
        self.car_info[:2] = self.car_info[:2] + \
                            self.speed * self.dt * np.array([np.cos(self.car_info[2]), np.sin(self.car_info[2])])

        self._update_sensor()
        s = self._get_state()
        r = -5 if self.terminal else 0
        return s, r, self.terminal

    def reset(self):
        self.terminal = False
        self.car_info[:3] = np.array([*self.start_point, -np.pi/2])
        self._update_sensor()
        return self._get_state()

    def render(self):
        if self.viewer is None:
            self.viewer = Viewer(*self.viewer_xy, self.car_info, self.sensor_info, self.obstacle_coords, self.obstacle_coords1)
#            self.viewer = Viewer(*self.viewer_xy, self.car_info, self.sensor_info, self.obstacle_coords)
        self.viewer.render()

    def sample_action(self):
        if self.is_discrete_action:
            a = np.random.choice(list(range(3)))
        else:
            a = np.random.uniform(*self.action_bound, size=self.action_dim)
        return a

    def set_fps(self, fps=30):
        pyglet.clock.set_fps_limit(fps)

    def _get_state(self):
        s = self.sensor_info[:, 0].flatten()/self.sensor_max
        return s

    def _update_sensor(self):
        cx, cy, rotation = self.car_info[:3]

        n_sensors = len(self.sensor_info)
        sensor_theta = np.linspace(-np.pi / 2, np.pi / 2, n_sensors)
        xs = cx + (np.zeros((n_sensors, ))+self.sensor_max) * np.cos(sensor_theta)
        ys = cy + (np.zeros((n_sensors, ))+self.sensor_max) * np.sin(sensor_theta)
        xys = np.array([[x, y] for x, y in zip(xs, ys)])    # shape (5 sensors, 2)

        # sensors
        tmp_x = xys[:, 0] - cx
        tmp_y = xys[:, 1] - cy
        # apply rotation
        rotated_x = tmp_x * np.cos(rotation) - tmp_y * np.sin(rotation)
        rotated_y = tmp_x * np.sin(rotation) + tmp_y * np.cos(rotation)
        # rotated x y
        self.sensor_info[:, -2:] = np.vstack([rotated_x+cx, rotated_y+cy]).T

        q = np.array([cx, cy])
        for si in range(len(self.sensor_info)):
            s = self.sensor_info[si, -2:] - q
            possible_sensor_distance = [self.sensor_max]
            possible_intersections = [self.sensor_info[si, -2:]]

            # obstacle collision
            for oi in range(len(self.obstacle_coords)-1):
                p = self.obstacle_coords[oi]
                r = self.obstacle_coords[(oi + 1) % len(self.obstacle_coords)] - self.obstacle_coords[oi]
                if np.cross(r, s) != 0:  # may collision
                    t = np.cross((q - p), s) / np.cross(r, s)
                    u = np.cross((q - p), r) / np.cross(r, s)
                    if 0 <= t <= 1 and 0 <= u <= 1:
                        intersection = q + u * s
                        possible_intersections.append(intersection)
                        possible_sensor_distance.append(np.linalg.norm(u*s))
            for oi in range(len(self.obstacle_coords1)-1):
                p = self.obstacle_coords1[oi]
                r = self.obstacle_coords1[(oi + 1) % len(self.obstacle_coords1)] - self.obstacle_coords1[oi]
                if np.cross(r, s) != 0:  # may collision
                    t = np.cross((q - p), s) / np.cross(r, s)
                    u = np.cross((q - p), r) / np.cross(r, s)
                    if 0 <= t <= 1 and 0 <= u <= 1:
                        intersection = q + u * s
                        possible_intersections.append(intersection)
                        possible_sensor_distance.append(np.linalg.norm(u*s))
            # window collision
            win_coord = np.array([
                [0, 0],
                [self.viewer_xy[0], 0],
                [*self.viewer_xy],
                [0, self.viewer_xy[1]],
                [0, 0],
            ])
            for oi in range(4):
                p = win_coord[oi]
                r = win_coord[(oi + 1) % len(win_coord)] - win_coord[oi]
                if np.cross(r, s) != 0:  # may collision
                    t = np.cross((q - p), s) / np.cross(r, s)
                    u = np.cross((q - p), r) / np.cross(r, s)
                    if 0 <= t <= 1 and 0 <= u <= 1:
                        intersection = p + t * r
                        possible_intersections.append(intersection)
                        possible_sensor_distance.append(np.linalg.norm(intersection - q))

            distance = np.min(possible_sensor_distance)
            distance_index = np.argmin(possible_sensor_distance)
            self.sensor_info[si, 0] = distance
            self.sensor_info[si, -2:] = possible_intersections[distance_index]
            if distance < self.car_info[-1]/3:
                self.terminal = True


class Viewer(pyglet.window.Window):
    color = {
        'background': [1]*3 + [1]
    }
    fps_display = pyglet.clock.ClockDisplay()
    bar_thc = 5

    def __init__(self, width, height, car_info, sensor_info, obstacle_coords, obstacle_coords1):
#    def __init__(self, width, height, car_info, sensor_info, obstacle_coords):
        super(Viewer, self).__init__(width, height, resizable=False, caption='2D car', vsync=False)  # vsync=False to not use the monitor FPS
        self.set_location(x=80, y=10)
        pyglet.gl.glClearColor(*self.color['background'])

        self.car_info = car_info
        self.sensor_info = sensor_info

        self.batch = pyglet.graphics.Batch()
        self.batch1 = pyglet.graphics.Batch()

        background = pyglet.graphics.OrderedGroup(0)
        foreground = pyglet.graphics.OrderedGroup(1)

        self.sensors = []
        line_coord = [0, 0] * 2
        c = (73, 73, 73) * 2
        for i in range(len(self.sensor_info)):
            self.sensors.append(self.batch.add(2, pyglet.gl.GL_LINES, foreground, ('v2f', line_coord), ('c3B', c)))

        car_box = [0, 0] * 4
        c = (249, 86, 86) * 4
        self.car = self.batch.add(4, pyglet.gl.GL_QUADS, foreground, ('v2f', car_box), ('c3B', c))

        c = (134, 181, 244) * 23
        self.obstacle = self.batch.add(23, pyglet.gl.GL_LINE_STRIP, background, ('v2f', obstacle_coords.flatten()), ('c3B', c))
        
        c = (134, 181, 244) * 20
        self.obstacle1 = self.batch1.add(20, pyglet.gl.GL_LINE_STRIP, background, ('v2f', obstacle_coords1.flatten()), ('c3B', c))

    def render(self):
        pyglet.clock.tick()
        self._update()
        self.switch_to()
        self.dispatch_events()
        self.dispatch_event('on_draw')
        self.flip()

    def on_draw(self):
        self.clear()
        self.batch.draw()
        self.batch1.draw()

        # self.fps_display.draw()

    def _update(self):
        cx, cy, r, w, l = self.car_info

        # sensors
        for i, sensor in enumerate(self.sensors):
            sensor.vertices = [cx, cy, *self.sensor_info[i, -2:]]

        # car
        xys = [
            [cx + l / 2, cy + w / 2],
            [cx - l / 2, cy + w / 2],
            [cx - l / 2, cy - w / 2],
            [cx + l / 2, cy - w / 2],
        ]
        r_xys = []
        for x, y in xys:
            tempX = x - cx
            tempY = y - cy
            # apply rotation
            rotatedX = tempX * np.cos(r) - tempY * np.sin(r)
            rotatedY = tempX * np.sin(r) + tempY * np.cos(r)
            # rotated x y
            x = rotatedX + cx
            y = rotatedY + cy
            r_xys += [x, y]
        self.car.vertices = r_xys


if __name__ == '__main__':
    np.random.seed(1)
    env = CarEnv()
    env.set_fps(30)
    for ep in range(20):
        s = env.reset()
        # for t in range(100):
        while True:
            env.render()
            s, r, done = env.step(env.sample_action())
            if done:
                break