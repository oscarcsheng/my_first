# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 10:18:23 2018

@author: yando
"""

"""
Environment for Robot Arm.
You can customize this script in a way you want.
View more on [莫烦Python] : https://morvanzhou.github.io/tutorials/
Requirement:
pyglet >= 1.2.4
numpy >= 1.12.1
"""
import numpy as np
import pyglet



pyglet.clock.set_fps_limit(10000)


class ArmEnv(object):
    action_bound = [-1, 1]
    action_dim = 2
    state_dim = 11
#    state_dim = 7
    dt = .05  # refresh rate
    arm1l = 100
    arm2l = 100
    viewer = None
    viewer_xy = (400, 400)
    get_point = False
    mouse_in = np.array([False])
    point_l = 15
    grab_counter = 0

    def __init__(self, mode='easy'):
        # node1 (l, d_rad, x, y),
        # node2 (l, d_rad, x, y)
        self.mode = mode
        self.arm_info = np.zeros((2, 4))
        self.arm_info[0, 0] = self.arm1l
        self.arm_info[1, 0] = self.arm2l
        self.point_info = np.array([250, 303])
        self.point_info_init = self.point_info.copy()
        self.center_coord = np.array(self.viewer_xy)/2

    def step(self, action):
        # action = (node1 angular v, node2 angular v)
        action = np.clip(action, *self.action_bound)
        self.arm_info[:, 1] += action * self.dt
        self.arm_info[:, 1] %= np.pi * 2

        arm1rad = self.arm_info[0, 1]
        arm2rad = self.arm_info[1, 1]
        arm1dx_dy = np.array([self.arm_info[0, 0] * np.cos(arm1rad), self.arm_info[0, 0] * np.sin(arm1rad)])
        arm2dx_dy = np.array([self.arm_info[1, 0] * np.cos(arm2rad), self.arm_info[1, 0] * np.sin(arm2rad)])
        self.arm_info[0, 2:4] = self.center_coord + arm1dx_dy  # (x1, y1)
        self.arm_info[1, 2:4] = self.arm_info[0, 2:4] + arm2dx_dy  # (x2, y2)

        s, arm2_distance = self._get_state()
        r = self._r_func(arm2_distance)

        return s, r, self.get_point

    def reset(self):
        self.get_point = False
        self.grab_counter = 0

        if self.mode == 'hard':
            pxy1 = np.clip(np.random.rand() * 90 + 150, 150, 240)
            pxy3 = np.clip(np.random.rand() * 30 + 320, 320, 350)
            pxy2 = np.clip(np.random.rand() * 110 + 240, 240, 350)
            pxy4 = np.clip(np.random.rand() * 110 + 50, 50, 160)
            xx = np.random.choice([pxy1, pxy3])
            yy = np.random.choice([pxy2, pxy4])
            self.point_info[:] = [xx, yy]
        else:
            arm1rad, arm2rad = np.random.rand(2) * np.pi * 2
            self.arm_info[0, 1] = arm1rad
            self.arm_info[1, 1] = arm2rad
            arm1dx_dy = np.array([self.arm_info[0, 0] * np.cos(arm1rad), self.arm_info[0, 0] * np.sin(arm1rad)])
            arm2dx_dy = np.array([self.arm_info[1, 0] * np.cos(arm2rad), self.arm_info[1, 0] * np.sin(arm2rad)])
            self.arm_info[0, 2:4] = self.center_coord + arm1dx_dy  # (x1, y1)
            self.arm_info[1, 2:4] = self.arm_info[0, 2:4] + arm2dx_dy  # (x2, y2)

            self.point_info[:] = self.point_info_init
        return self._get_state()[0]

    def render(self):
        if self.viewer is None:
            self.viewer = Viewer(*self.viewer_xy, self.arm_info, self.point_info, self.point_l, self.mouse_in)
        self.viewer.render()

    def sample_action(self):
        return np.random.uniform(*self.action_bound, size=self.action_dim)

    def set_fps(self, fps=30):
        pyglet.clock.set_fps_limit(fps)

    def _get_state(self):
        # return the distance (dx, dy) between arm finger point with blue point
        arm_end = self.arm_info[:, 2:4]
        t_arms = np.ravel(arm_end - self.point_info)
        center_dis = (self.center_coord - self.point_info)/200
        in_point = 1 if self.grab_counter > 0 else 0
        BP1 = [280, 200] - self.arm_info[0, 2:4]
        BP = [280, 200] - self.arm_info[1, 2:4]
        
        return np.hstack([in_point, t_arms/200, center_dis, -BP1/200, -BP/200
                          # arm1_distance_p, arm1_distance_b,
                          ]), t_arms[-2:]

    def _r_func(self, distance):
        obstacle_arm1 = 0
        obstacle_arm2 = 0
        t = 10
        abs_distance = np.sqrt(np.sum(np.square(distance)))
        r = -abs_distance/200
        
        AP1 = [280, 200] - self.center_coord
        BP1 = [280, 200] - self.arm_info[0, 2:4]
        AB1 = -self.center_coord + self.arm_info[0, 2:4]
        ratio1 = np.dot(AP1, AB1)/np.sum(np.square(AB1))
        PC1 = AP1 - ratio1*AB1
        
        if ratio1 <= 0:
            obstacle_arm1 = np.sqrt(np.sum(np.square(AP1)))
        elif 0 < ratio1 <= 1:
            obstacle_arm1 = np.sqrt(np.sum(np.square(PC1)))
        elif ratio1 > 1:
            obstacle_arm1 = np.sqrt(np.sum(np.square(BP1)))
        
        AP = [280, 200] - self.arm_info[0, 2:4]
        BP = [280, 200] - self.arm_info[1, 2:4]
        AB = self.arm_info[1, 2:4] - self.arm_info[0, 2:4]
        ratio = np.dot(AP, AB)/np.sum(np.square(AB))
        PC = AP - ratio*AB
        
        if ratio <= 0:
            obstacle_arm2 = np.sqrt(np.sum(np.square(AP)))
        elif 0 < ratio <= 1:
            obstacle_arm2 = np.sqrt(np.sum(np.square(PC)))
        elif ratio > 1:
            obstacle_arm2 = np.sqrt(np.sum(np.square(BP)))
        
        if 0 < obstacle_arm1 < 60:
            r = r - min([30/obstacle_arm1, 30])
        if 0 < obstacle_arm2 < 20:
            r = r - min([15/obstacle_arm2, 20])
            if abs_distance - obstacle_arm2 > 0:
                r = r - 10
        
        if abs_distance < self.point_l and (not self.get_point):
            r += 3.
            self.grab_counter += 1
            if self.grab_counter > t:
                r += 1.
                self.get_point = True
        elif abs_distance > self.point_l:
            self.grab_counter = 0
            self.get_point = False
        return r

    def min_distance2(self):
        AP = [280, 200] - self.arm_info[0, 2:4]
        BP = [280, 200] - self.arm_info[1, 2:4]
        AB = self.arm_info[1, 2:4] - self.arm_info[0, 2:4]
        ratio = np.dot(AP, AB)/np.sum(np.square(AB))
        PC = AP - ratio*np.sqrt(np.sum(np.square(AB)))
        
        if ratio <= 0:
            return np.sqrt(np.sum(np.square(AP)))
        elif 0 < ratio <= 1:
            return np.sqrt(np.sum(np.square(PC)))
        elif ratio > 1:
            return np.sqrt(np.sum(np.square(BP)))
        
    def min_distance1(self):
        AP1 = [280, 200] - self.center_coord
        BP1 = [280, 200] - self.arm_info[0, 2:4]
        AB1 = self.arm_info[1, 2:4] - self.arm_info[0, 2:4]
        ratio1 = np.dot(AP1, AB1)/np.sum(np.square(AB1))
        PC1 = AP1 - ratio1*np.sqrt(np.sum(np.square(AB1)))
        
        if ratio1 <= 0:
            return np.sqrt(np.sum(np.square(AP1)))
        elif 0 < ratio1 <= 1:
            return np.sqrt(np.sum(np.square(PC1)))
        elif ratio1 > 1:
            return np.sqrt(np.sum(np.square(BP1)))


class Viewer(pyglet.window.Window):
    color = {
        'background': [1]*3 + [1]
    }
    fps_display = pyglet.clock.ClockDisplay()
    bar_thc = 5

    def __init__(self, width, height, arm_info, point_info, point_l, mouse_in):
        super(Viewer, self).__init__(width, height, resizable=False, caption='Arm', vsync=False)  # vsync=False to not use the monitor FPS
        self.set_location(x=80, y=10)
        pyglet.gl.glClearColor(*self.color['background'])

        self.arm_info = arm_info
        self.point_info = point_info
        self.mouse_in = mouse_in
        self.point_l = point_l

        self.center_coord = np.array((min(width, height)/2, ) * 2)
        self.batch = pyglet.graphics.Batch()
        self.batch1 = pyglet.graphics.Batch()

        arm1_box, arm2_box, point_box = [0]*8, [0]*8, [0]*8
        obstacle_box = np.array([265, 185, 295, 185, 295, 215, 265, 215])
        c1, c2, c3 = (249, 86, 86)*4, (86, 109, 249)*4, (249, 39, 65)*4
        self.point = self.batch.add(4, pyglet.gl.GL_QUADS, None, ('v2f', point_box), ('c3B', c2))
        self.arm1 = self.batch.add(4, pyglet.gl.GL_QUADS, None, ('v2f', arm1_box), ('c3B', c1))
        self.arm2 = self.batch.add(4, pyglet.gl.GL_QUADS, None, ('v2f', arm2_box), ('c3B', c1))
        self.obstacle = self.batch1.add(4, pyglet.gl.GL_QUADS, None, ('v2f', obstacle_box),('c3B', c3))

    def render(self):
        pyglet.clock.tick()
        self._update_arm()
        self.switch_to()
        self.dispatch_events()
        self.dispatch_event('on_draw')
        self.flip()

    def on_draw(self):
        self.clear()
        self.batch.draw()
        self.batch1.draw()
        # self.fps_display.draw()

    def _update_arm(self):
        point_l = self.point_l
        point_box = (self.point_info[0] - point_l, self.point_info[1] - point_l,
                     self.point_info[0] + point_l, self.point_info[1] - point_l,
                     self.point_info[0] + point_l, self.point_info[1] + point_l,
                     self.point_info[0] - point_l, self.point_info[1] + point_l)
        self.point.vertices = point_box

        arm1_coord = (*self.center_coord, *(self.arm_info[0, 2:4]))  # (x0, y0, x1, y1)
        arm2_coord = (*(self.arm_info[0, 2:4]), *(self.arm_info[1, 2:4]))  # (x1, y1, x2, y2)
        arm1_thick_rad = np.pi / 2 - self.arm_info[0, 1]
        x01, y01 = arm1_coord[0] - np.cos(arm1_thick_rad) * self.bar_thc, arm1_coord[1] + np.sin(
            arm1_thick_rad) * self.bar_thc
        x02, y02 = arm1_coord[0] + np.cos(arm1_thick_rad) * self.bar_thc, arm1_coord[1] - np.sin(
            arm1_thick_rad) * self.bar_thc
        x11, y11 = arm1_coord[2] + np.cos(arm1_thick_rad) * self.bar_thc, arm1_coord[3] - np.sin(
            arm1_thick_rad) * self.bar_thc
        x12, y12 = arm1_coord[2] - np.cos(arm1_thick_rad) * self.bar_thc, arm1_coord[3] + np.sin(
            arm1_thick_rad) * self.bar_thc
        arm1_box = (x01, y01, x02, y02, x11, y11, x12, y12)
        arm2_thick_rad = np.pi / 2 - self.arm_info[1, 1]
        x11_, y11_ = arm2_coord[0] + np.cos(arm2_thick_rad) * self.bar_thc, arm2_coord[1] - np.sin(
            arm2_thick_rad) * self.bar_thc
        x12_, y12_ = arm2_coord[0] - np.cos(arm2_thick_rad) * self.bar_thc, arm2_coord[1] + np.sin(
            arm2_thick_rad) * self.bar_thc
        x21, y21 = arm2_coord[2] - np.cos(arm2_thick_rad) * self.bar_thc, arm2_coord[3] + np.sin(
            arm2_thick_rad) * self.bar_thc
        x22, y22 = arm2_coord[2] + np.cos(arm2_thick_rad) * self.bar_thc, arm2_coord[3] - np.sin(
            arm2_thick_rad) * self.bar_thc
        arm2_box = (x11_, y11_, x12_, y12_, x21, y21, x22, y22)
        self.arm1.vertices = arm1_box
        self.arm2.vertices = arm2_box

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.UP:
            self.arm_info[0, 1] += .1
            print(self.arm_info[:, 2:4] - self.point_info)
        elif symbol == pyglet.window.key.DOWN:
            self.arm_info[0, 1] -= .1
            print(self.arm_info[:, 2:4] - self.point_info)
        elif symbol == pyglet.window.key.LEFT:
            self.arm_info[1, 1] += .1
            print(self.arm_info[:, 2:4] - self.point_info)
        elif symbol == pyglet.window.key.RIGHT:
            self.arm_info[1, 1] -= .1
            print(self.arm_info[:, 2:4] - self.point_info)
        elif symbol == pyglet.window.key.Q:
            pyglet.clock.set_fps_limit(1000)
        elif symbol == pyglet.window.key.A:
            pyglet.clock.set_fps_limit(30)

    def on_mouse_motion(self, x, y, dx, dy):
        self.point_info[:] = [x, y]

    def on_mouse_enter(self, x, y):
        self.mouse_in[0] = True

    def on_mouse_leave(self, x, y):
        self.mouse_in[0] = False
