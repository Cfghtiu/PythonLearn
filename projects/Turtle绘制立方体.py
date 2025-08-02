import time

import numpy as np
import turtle
import math
# 定义立方体的8个顶点坐标 (x, y, z)
vertices = np.array([
    [-100, -100, -100],  # 0: 左下后
    [ 100, -100, -100],  # 1: 右下后
    [ 100,  100, -100],  # 2: 右上后
    [-100,  100, -100],  # 3: 左上后
    [-100, -100,  100],  # 4: 左下前
    [ 100, -100,  100],  # 5: 右下前
    [ 100,  100,  100],  # 6: 右上前
    [-100,  100,  100]   # 7: 左上前
], dtype=float)

# 定义立方体的12条边（每条边由两个顶点组成）
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # 后面的四条边
    (4, 5), (5, 6), (6, 7), (7, 4),  # 前面的四条边
    (0, 4), (1, 5), (2, 6), (3, 7)   # 连接前后面的四条边
]

turtle.setup(800, 600)
# turtle.bgcolor("black")
turtle.title("3D Cube with Turtle")
turtle.tracer(0)
turtle.pensize(2)
turtle.hideturtle()


def get_rotation_matrix(angle):
    """
    获取绕Y轴旋转的旋转矩阵
    """
    cos_angle = math.cos(math.radians(angle))
    sin_angle = math.sin(math.radians(angle))

    # 绕y轴旋转的矩阵
    rotation_matrix = np.array([
        [cos_angle, 0, sin_angle],
        [0, 1, 0],
        [-sin_angle, 0, cos_angle]
    ])

    return rotation_matrix


def project_to_2d(x, y, z):
    factor = 300 / (300 + z)
    screen_x = x * factor
    screen_y = y * factor
    return screen_x, screen_y


angle = 0
while True:
    turtle.r()  # 注释这行有奇效
    rotation_matrix = get_rotation_matrix(angle)
    rotated_vertices = vertices @ rotation_matrix

    for edge in edges:
        # 抬笔，到顶点A
        turtle.penup()
        turtle.goto(*project_to_2d(*rotated_vertices[edge[0]]))
        # 落笔(开始画线)，到顶点B
        turtle.pendown()
        turtle.goto(*project_to_2d(*rotated_vertices[edge[1]]))
    angle += 1
    turtle.update()
    time.sleep(0.01)
