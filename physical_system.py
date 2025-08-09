import numpy as np
import math


class Vector:
    """三维矢量类，封装矢量操作"""

    def __init__(self, x, y, z=None):
        """
        初始化矢量
        :param x: x分量
        :param y: y分量
        :param z: z分量（可选，默认为0）
        """
        self.data = np.array([x, y, z if z is not None else 0], dtype=float)

    def __add__(self, other):
        """矢量加法"""
        return Vector(*(self.data + other.data))

    def __sub__(self, other):
        """矢量减法"""
        return Vector(*(self.data - other.data))

    def __mul__(self, scalar):
        """标量乘法"""
        return Vector(*(self.data * scalar))

    def __rmul__(self, scalar):
        """标量乘法（右侧）"""
        return self.__mul__(scalar)

    def magnitude(self):
        """计算矢量大小"""
        return np.linalg.norm(self.data)

    def normalized(self):
        """返回归一化后的矢量"""
        mag = self.magnitude()
        if mag > 0:
            return Vector(*(self.data / mag))
        return Vector(0, 0, 0)  # 零矢量

    def dot(self, other):
        """点积"""
        return np.dot(self.data, other.data)

    def cross(self, other):
        """叉积"""
        return Vector(*np.cross(self.data, other.data))

    def as_tuple(self):
        """转换为元组"""
        return tuple(self.data)

    def __repr__(self):
        return f"Vector({self.data[0]:.2f}, {self.data[1]:.2f}, {self.data[2]:.2f})"


class PhysicalSystem:
    """表示物理系统中的单个物体，封装其力学属性和接触关系"""

    def __init__(self, system_id: str, mass: float, position):
        """
        初始化物理系统
        :param system_id: 系统唯一标识符
        :param mass: 质量(kg)
        :param position: 位置坐标，可以是元组或Vector对象
        """
        self.id = system_id
        self.mass = mass

        # 位置处理：兼容元组输入或Vector对象
        if isinstance(position, Vector):
            self.position = position
        else:
            self.position = Vector(*position) if len(position) == 3 else Vector(position[0], position[1], 0)

        self.forces = []  # 存储(名称, Vector)的列表
        self.contact_surfaces = []  # 接触面对象列表
        self.acceleration = Vector(0, 0, 0)  # 加速度向量(m/s²)
        self.velocity = Vector(0, 0, 0)  # 速度向量(m/s)

    def add_gravity(self, g=9.8, direction=(0, -1, 0)):
        """
        添加重力
        :param g: 重力加速度大小，默认9.8m/s²
        :param direction: 重力方向向量，默认(0,-1,0)表示向下
        """
        # 处理方向输入
        if not isinstance(direction, Vector):
            direction = Vector(*direction)

        direction_vec = direction.normalized()
        gravity_vec = direction_vec * (self.mass * g)
        self.forces.append(('gravity', gravity_vec))
        return gravity_vec

    def add_external_force(self, force_name: str, magnitude: float, direction):
        """
        添加外部力
        :param force_name: 力的名称(如"拉力", "推力")
        :param magnitude: 力的大小(N)
        :param direction: 力的方向
            二维情况: 与水平正方向的夹角(度)
            三维情况: (x,y,z)方向向量、欧拉角(alpha,beta)或Vector对象
        """
        # 处理方向输入
        if isinstance(direction, (int, float)):
            # 二维情况: 角度输入
            rad = direction * (math.pi / 180)
            force_vec = Vector(math.cos(rad), math.sin(rad), 0) * magnitude
        elif isinstance(direction, Vector):
            # 已经是矢量对象
            force_vec = direction.normalized() * magnitude
        elif len(direction) == 2:
            # 欧拉角(alpha,beta)
            alpha, beta = direction
            alpha_rad = alpha * (math.pi / 180)
            beta_rad = beta * (math.pi / 180)
            x = math.cos(alpha_rad) * math.cos(beta_rad)
            y = math.sin(alpha_rad) * math.cos(beta_rad)
            z = math.sin(beta_rad)
            force_vec = Vector(x, y, z).normalized() * magnitude
        else:
            # 方向向量(x,y,z)
            if not isinstance(direction, Vector):
                direction = Vector(*direction)
            force_vec = direction.normalized() * magnitude

        self.forces.append((force_name, force_vec))
        return force_vec

    def add_contact_surface(self, surface_id: str, other_system, normal_direction, friction_coeff=0):
        """
        添加与其他系统的接触面
        :param surface_id: 接触面唯一标识符
        :param other_system: 接触的另一系统对象
        :param normal_direction: 接触面法线方向
            二维情况: 法线角度(度)
            三维情况: (x,y,z)法线向量或Vector对象
        :param friction_coeff: 摩擦系数(0表示光滑)
        """
        # 处理法线方向
        if isinstance(normal_direction, (int, float)):
            # 二维情况: 角度转向量
            rad = normal_direction * (math.pi / 180)
            normal_vec = Vector(math.cos(rad), math.sin(rad), 0).normalized()
        elif isinstance(normal_direction, Vector):
            # 已经是矢量对象
            normal_vec = normal_direction.normalized()
        else:
            # 三维情况: 归一化向量
            normal_vec = Vector(*normal_direction).normalized()

        contact = {
            'id': surface_id,
            'system1': self,
            'system2': other_system,
            'normal_direction': normal_vec,
            'friction_coeff': friction_coeff
        }
        self.contact_surfaces.append(contact)
        other_system.contact_surfaces.append(contact)  # 双向绑定
        return contact

    def calculate_net_force(self):
        """
        计算物体所受合力
        :return: 合力Vector对象
        :raises: ZeroDivisionError 当物体质量为0时
        """
        if self.mass == 0:
            raise ZeroDivisionError("Cannot calculate net force for zero mass object")

        net_force = Vector(0, 0, 0)
        for _, force_vec in self.forces:
            net_force += force_vec

        return net_force

    def update_kinematics(self, time_delta=0.1):
        """
        根据当前合力更新运动状态（牛顿第二定律）
        :param time_delta: 时间间隔(s)
        """
        net_force = self.calculate_net_force()
        self.acceleration = net_force * (1 / self.mass)  # F = ma

        # 更新速度和位置（欧拉法）
        # v = v0 + a * dt
        self.velocity += self.acceleration * time_delta

        # p = p0 + v0 * dt + 0.5 * a * dt^2
        self.position += self.velocity * time_delta + self.acceleration * (0.5 * time_delta ** 2)

    def to_dict(self):
        """将系统状态转为字典格式，便于JSON序列化"""

        # 序列化矢量对象
        def serialize_vector(vec):
            if isinstance(vec, Vector):
                return vec.as_tuple()
            return vec

        # 处理力数据
        serialized_forces = []
        for force in self.forces:
            name, vec = force
            serialized_forces.append((name, vec.as_tuple()))

        # 处理接触面
        serialized_contacts = []
        for cs in self.contact_surfaces:
            contact = {
                'id': cs['id'],
                'other_system': cs['system2'].id,
                'normal_direction': serialize_vector(cs['normal_direction']),
                'friction_coeff': cs['friction_coeff']
            }
            serialized_contacts.append(contact)

        return {
            'id': self.id,
            'mass': self.mass,
            'position': serialize_vector(self.position),
            'velocity': serialize_vector(self.velocity),
            'acceleration': serialize_vector(self.acceleration),
            'forces': serialized_forces,
            'contact_surfaces': serialized_contacts
        }