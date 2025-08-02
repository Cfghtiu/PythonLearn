import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *

# 定义正方体的8个顶点坐标
vertices = np.array([
    [-0.5, -0.5, -0.5],  # 0: 左下后
    [ 0.5, -0.5, -0.5],  # 1: 右下后
    [ 0.5,  0.5, -0.5],  # 2: 右上后
    [-0.5,  0.5, -0.5],  # 3: 左上后
    [-0.5, -0.5,  0.5],  # 4: 左下前
    [ 0.5, -0.5,  0.5],  # 5: 右下前
    [ 0.5,  0.5,  0.5],  # 6: 右上前
    [-0.5,  0.5,  0.5]   # 7: 左上前
], dtype=np.float32)

# 定义正方体的12条边（每条边由两个顶点组成）
edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # 后面的四条边
    (4, 5), (5, 6), (6, 7), (7, 4),  # 前面的四条边
    (0, 4), (1, 5), (2, 6), (3, 7)   # 连接前后面的四条边
]

# 添加旋转角度变量
rotation_angle = 0.0


def draw_cube():
    """
    使用OpenGL绘制正方体的边框
    """
    glBegin(GL_LINES)  # 开始绘制线段
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])  # 指定顶点坐标
    glEnd()  # 结束绘制


def init():
    """
    初始化OpenGL环境
    """
    glClearColor(0.0, 0.0, 0.0, 0.0)  # 设置背景颜色为黑色
    glEnable(GL_DEPTH_TEST)  # 启用深度测试，实现遮挡效果
    glMatrixMode(GL_PROJECTION)  # 设置当前矩阵为投影矩阵
    glLoadIdentity()  # 将当前矩阵重置为单位矩阵
    glOrtho(-2, 2, -2, 2, -2, 2)  # 设置正交投影矩阵
    glMatrixMode(GL_MODELVIEW)  # 设置当前矩阵为模型视图矩阵


def display():
    """
    显示函数
    """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # 清除颜色和深度缓冲区
    glLoadIdentity()  # 将当前矩阵重置为单位矩阵
    # 使用动态角度旋转正方体
    glRotatef(rotation_angle, 1, 1, 0)  # 绕(1,1,0)向量旋转
    glColor3f(1.0, 1.0, 1.0)  # 设置线条颜色为白色
    draw_cube()
    glutSwapBuffers()  # 交换前后缓冲区，显示绘制结果


# 使用计时器函数控制动画
def timer(value):
    """
    计时器回调函数，用于更新动画
    """
    global rotation_angle
    rotation_angle += 2.0  # 每帧增加2度
    if rotation_angle >= 360.0:
        rotation_angle -= 360.0
    glutPostRedisplay()  # 标记当前窗口需要重绘
    # 重新注册计时器，16毫秒约等于60FPS
    glutTimerFunc(16, timer, 0)


def main():
    """
    主函数
    """
    glutInit()  # 初始化GLUT库
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # 设置显示模式：双缓冲、RGB颜色模式、深度缓冲
    glutInitWindowSize(500, 500)  # 设置窗口大小为500x500像素
    glutCreateWindow(b"Cube Wireframe")  # 创建窗口，标题为"Cube Wireframe"
    init()
    glutDisplayFunc(display)  # 注册显示回调函数
    # 注册计时器回调函数，16毫秒约等于60FPS
    glutTimerFunc(16, timer, 0)
    glutMainLoop()  # 进入GLUT主循环


if __name__ == '__main__':
    main()