"""优化算法基类"""
import sys
sys.path.append(r"/home/r0bin/projects/t231101/t231110/12")

import io
import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image
from EA.algs.base.unit import Unit

class Algorithm_Impl:
    def __init__(self, dim, size, iter_max, range_min_list, range_max_list, 
                 is_cal_max=True, fitfunction=None, silent=False):
        self.name = 'EA_Base'
        
        self.dim = dim
        """维度"""
        self.size = size
        """种群大小"""
        self.iter_max = iter_max
        """最大迭代次数"""
        self.range_min_list = range_min_list
        """解空间下界"""
        self.range_max_list = range_max_list
        """解空间上界"""
        self.is_cal_max = is_cal_max
        """是否为最大化问题"""
        self.fitfunction = fitfunction
        """适应度函数"""
        self.silence = silent
        """是否静默"""

        self.cal_fit_num = 0
        """适应度函数调用次数"""
        self.unit_class = Unit
        """个体类"""
        self.unit_list = []
        """个体列表"""
        self.position_best = np.zeros(self.dim)
        """最优个体位置"""
        self.value_best = -np.finfo(np.float64).max
        """最优个体适应度"""
        self.value_best_history = []
        """最优个体适应度历史记录"""
        self.position_best_history = []
        """最优个体位置历史记录"""

    def run(self, unit_list=[]):
        """运行算法"""
        start_time = time.time()
        self.init(unit_list)
        self.iteration()
        end_time = time.time()
        self.time_cost = end_time - start_time
        if not self.silence:
            print(f"运行时间: {end_time - start_time}")

    def init(self, unit_list=[]):
        """
        初始化算法，初始化内容：
        - 最优个体位置
        - 最优个体适应度
        - 最优个体适应度历史记录
        - 最优个体位置历史记录
        """
        self.unit_list = [] if len(unit_list) == 0 else unit_list
        self.position_best = np.zeros(self.dim)
        self.value_best_history = []
        self.position_best_history = []
        self.value_best = -np.finfo(np.float64).max

    def iteration(self):
        """迭代内容，由子类实现"""
        for iter in range(1, self.iter_max + 1):
            self.update(iter)

    def update(self, iter):
        for i in range(self.size):
            if self.unit_list[i].fitness > self.value_best:
                self.value_best = self.unit_list[i].fitness
                self.position_best = self.unit_list[i].position
            self.unit_list[i].save()

        if not self.silence:
            print(f"第 {iter} 代")
        if self.is_cal_max:
            self.value_best_history.append(self.value_best)
            if not self.silence:
                print(f"最优值= {self.value_best}")
        else:
            self.value_best_history.append(-self.value_best)
            if not self.silence:
                print(f"最优值= {-self.value_best}")

        self.position_best_history.append(self.position_best)
        if not self.silence:
            print(f"最优解= {self.position_best}")

    def cal_fitfunction(self, position):
        """
        计算适应度函数值，对于最大化问题，返回值不变；对于最小化问题，返回值取相反数
        """
        if self.fitfunction is None:
            value = 0
        else:
            value = self.fitfunction(position) if self.is_cal_max else -self.fitfunction(position)
        self.cal_fit_num += 1
        return value

    def get_out_bound_value(self, position, min_list=None, max_list=None):
        """边界处理，超出边界的位置将被限制在边界内"""
        min_list = self.range_min_list if min_list is None else min_list
        max_list = self.range_max_list if max_list is None else max_list
        position_tmp = np.clip(position, min_list, max_list)
        return position_tmp

    def get_out_bound_value_rand(self, position, min_list=None, max_list=None):
        """边界处理，超出边界的位置将被随机替换"""
        min_list = self.range_min_list if min_list is None else min_list
        max_list = self.range_max_list if max_list is None else max_list
        position_tmp = position.copy()
        position_rand = np.random.uniform(min_list, max_list, position.shape)
        position_tmp[position < min_list] = position_rand[position < min_list]
        position_tmp[position > max_list] = position_rand[position > max_list]
        return position_tmp
    
    def set_unit_list(self, unit_list, surr):
        X = np.array([ind.position for ind in unit_list])
        y = surr.predict(X)
        self.cal_fit_num += len(y)

        self.unit_list = []
        for i in range(len(unit_list)):
            if i >= self.size:
                break
            unit = self.unit_class()
            unit.position = unit_list[i].position.copy()
            unit.fitness = y[i]
            self.unit_list.append(unit)

    def toStr(self):
        str = f"name: {self.name}\n"
        str += f"dim: {self.dim}\n"
        str += f"size: {self.size}\n"
        str += f"iter_max: {self.iter_max}\n"
        str += f"range_min_list: {self.range_min_list}\n"
        str += f"range_max_list: {self.range_max_list}\n"
        str += f"is_cal_max: {self.is_cal_max}\n"
        str += f"fitfunction: {self.fitfunction}\n"
        str += f"cal_fit_num: {self.cal_fit_num}\n"
        str += f"silence: {self.silence}\n"
        str += f"unit_class: {self.unit_class.__class__.__name__}\n"
        return str
    
    def save_result(self):
        """保存self.value_best_history、self.position_best_history、self.value_best、self.position_best到result.txt"""
        with open('result.txt', 'w') as f:
            f.write(
                f"--------------------------------------Info--------------------------------------\n")
            algo_str = self.toStr()
            f.write(algo_str)

            f.write(
                f"--------------------------------------Result--------------------------------------\n")
            f.write(f"value_best: {self.value_best}\n")
            f.write(f"position_best: {self.position_best}\n")

            f.write(f"history:\n")
            for i in range(len(self.value_best_history)):
                f.write(f"{i + 1}: {self.position_best_history[i]} {self.value_best_history[i]}\n")
    
    def draw2_gif1(self, step, is_save, name):
        if self.dim < 2:
            print('维度太低，无法绘制图像')
            return
        if step < 1:
            step = 1

        images = []

        for i in range(1, self.iter_max + 1):
            if i % step > 0 and i > 1:
                continue

            plt.figure(figsize=(8, 6))
            for s in range(self.size):
                cur_position = self.unit_list[s].position_history_list[i-1, :]
                plt.scatter(cur_position[0], cur_position[1], 10, 'b')

            range_size_x = self.range_max_list[0] - self.range_min_list[0]
            range_size_y = self.range_max_list[1] - self.range_min_list[1]
            plt.axis([self.range_min_list[0] - 0.2 * range_size_x, self.range_max_list[0] + 0.2 * range_size_x,
                    self.range_min_list[1] - 0.2 * range_size_y, self.range_max_list[1] + 0.2 * range_size_y])
            plt.text(self.range_min_list[0], self.range_max_list[1], str(i), fontsize=20)
            plt.gca().set_aspect('equal', adjustable='box')

            if is_save:
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                img = Image.open(buf)
                images.append(img)
                if images:
                    filename = f"{name}_2d.gif"
                    images[0].save(filename, save_all=True, append_images=images[1:], loop=0, duration=200)
                buf.close()

            plt.close()

        print("draw 2d gif done.")

    def draw2_gif(self, step, is_save, name, is_cal_max=None):
        if self.dim < 2:
            print('维度太低，无法绘制图像')
            return
        if self.dim > 3:
            print('维度太高，无法绘制图像')
            return
        if step < 1:
            step = 1

        images = []
        flag = is_cal_max if is_cal_max is not None else self.is_cal_max
        t = 1 if flag else -1

        # 创建绘制函数深度图的网格数据
        x = np.linspace(self.range_min_list[0], self.range_max_list[0], 100)
        y = np.linspace(self.range_min_list[1], self.range_max_list[1], 100)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X)
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                Z[i, j] = self.fitfunction(np.array([X[i, j], Y[i, j]])) * t

        for i in range(1, self.iter_max + 1):
            if i % step > 0 and i > 1:
                continue

            plt.figure(figsize=(8, 6))
            # 绘制函数的深度图
            plt.imshow(Z, extent=[self.range_min_list[0], self.range_max_list[0], 
                                self.range_min_list[1], self.range_max_list[1]],
                    origin='lower', cmap='viridis', alpha=0.7)
            plt.colorbar()  # 显示颜色条

            for s in range(self.size):
                cur_position = self.unit_list[s].position_history_list[i-1, :]
                plt.scatter(cur_position[0], cur_position[1], 10, 'b')  # 保持原来的散点样式

            # 设置图形范围和比例
            range_size_x = self.range_max_list[0] - self.range_min_list[0]
            range_size_y = self.range_max_list[1] - self.range_min_list[1]
            plt.axis([self.range_min_list[0] - 0.2 * range_size_x, self.range_max_list[0] + 0.2 * range_size_x,
                    self.range_min_list[1] - 0.2 * range_size_y, self.range_max_list[1] + 0.2 * range_size_y])
            plt.text(self.range_min_list[0], self.range_max_list[1], str(i), fontsize=20)
            plt.gca().set_aspect('equal', adjustable='box')

            if is_save:
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                img = Image.open(buf)
                images.append(img)
                if images:
                    filename = f"{name}_2d.gif"
                    images[0].save(filename, save_all=True, append_images=images[1:], loop=0, duration=300)
                buf.close()

            plt.close()

        # if is_save and images:
        #     filename = f"{name}_2d.gif"
        #     images[0].save(filename, save_all=True, append_images=images[1:], loop=0, duration=200)
            
        print("draw 2d gif done.")


    def draw3_gif(self, step, is_save, name):
        if self.dim < 3:
            print('维度太低，无法绘制三维图像')
            return
        if step < 1:
            step = 1

        images = []

        for i in range(1, self.iter_max + 1):
            if i % step > 0 and i > 1:
                continue

            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection='3d')

            for s in range(self.size):
                cur_position = self.unit_list[s].position_history_list[i - 1, :]
                ax.scatter(cur_position[0], cur_position[1], cur_position[2], 10, 'b')

            range_size_x = self.range_max_list[0] - self.range_min_list[0]
            range_size_y = self.range_max_list[1] - self.range_min_list[1]
            range_size_z = self.range_max_list[2] - self.range_min_list[2]
            ax.set_xlim([self.range_min_list[0] - 0.1 * range_size_x, self.range_max_list[0] + 0.1 * range_size_x])
            ax.set_ylim([self.range_min_list[1] - 0.1 * range_size_y, self.range_max_list[1] + 0.1 * range_size_y])
            ax.set_zlim([self.range_min_list[2] - 0.1 * range_size_z, self.range_max_list[2] + 0.1 * range_size_z])
            ax.text(self.range_min_list[0], self.range_max_list[1], self.range_max_list[2], str(i), fontsize=20)

            if is_save:
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                img = Image.open(buf)
                images.append(img)
                buf.close()

            plt.close()

        if is_save and images:
            filename = f"{name}_3d.gif"
            images[0].save(filename, save_all=True, append_images=images[1:], loop=0, duration=100)

