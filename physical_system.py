from vector import *
import math


class ContactSurface:
    """表示两个物理系统之间的接触面"""

    def __init__(self, surface_id: str, system1, system2, normal_direction, friction_coeff: float = 0.0,
                 elastic_force=Force(0,0,0), friction=Force(0,0,0), friction_type="static"):
        """
        初始化接触面
        :param surface_id: 接触面唯一标识符
        :param system1: 第一个物理系统
        :param system2: 第二个物理系统
        :param normal_direction: 接触面法线方向
        :param friction: 摩擦力
        :param friction_type: 摩擦类型
        """
        self.id = surface_id
        self.system1 = system1
        self.system2 = system2

        # 两系统间相对速度矢量
        self.relative_velocity = system1.velocity - system2.velocity
        self.friction_coeff = friction_coeff  # 摩擦系数
        self.elastic_force = elastic_force  # 初始化弹力大小(N)
        self.friction = friction

        # 摩擦类型
        self.friction_type = "static" if abs(self.relative_velocity) < 1e-5 else "kinetic"

        # 处理法线方向
        if isinstance(normal_direction, (int, float)):
            rad = math.radians(normal_direction)
            self.normal_direction = Vector(math.cos(rad), math.sin(rad), 0).normalized()
        elif isinstance(normal_direction, Vector):
            self.normal_direction = normal_direction.normalized()
        elif hasattr(normal_direction, "__len__"):
            if len(normal_direction) == 1:
                rad = math.radians(normal_direction[0])
                self.normal_direction = Vector(math.cos(rad), math.sin(rad), 0).normalized()
            else:
                self.normal_direction = Vector(*normal_direction[:3]).normalized()
        else:
            raise TypeError(f"不支持的法线方向类型: {type(normal_direction)}")

    def calculate_friction_force(self):
        """
        计算摩擦力
        :return: 摩擦力矢量
        """
        # 根据相对速度选择摩擦类型

        return self.friction_coeff * self.elastic_force

    def update_elastic_force(self, penetration):
        """
        更新弹力(胡克定律简化版)
        :param penetration: 穿透深度(m)
        """
        # 简单线性弹力模型 F = k * x
        # 实际项目中可根据需要替换为更复杂的模型
        stiffness = 1000.0  # 刚度系数(N/m)
        self.elastic_force = stiffness * penetration

    def __repr__(self):
        return f"ContactSurface({self.id}, μ_s={self.friction})"


class PhysicalSystem:
    """表示物理系统中的单个物体，使用带量纲的矢量实现"""

    def __init__(self, system_id: str, mass: float, position, velocity=(0, 0, 0), acceleration=(0, 0, 0), contract_surfaces=None):
        """
        初始化物理系统
        :param system_id: 系统唯一标识符
        :param mass: 质量(kg)
        :param position: 位置坐标，可以是元组或Vector对象
        :param velocity: 速度矢量，可以是元组或Vector对象
        """


        self.id = system_id
        self.mass = mass

        # 位置处理：确保使用Displacement类
        self.position = self._process_vector(position, Displacement)

        # 速度处理：确保使用Velocity类
        self.velocity = self._process_vector(velocity, Velocity)

        # 加速度处理：确保使用Acceleration类
        self.acceleration = self._process_vector(acceleration, Acceleration)


        self.forces = []  # 存储(名称, Force矢量)的列表
        self.contact_surfaces = contract_surfaces  # 接触面对象字典

    def _process_vector(self, input_data, vector_class):
        """通用矢量处理方法"""
        if isinstance(input_data, vector_class):
            return input_data
        elif isinstance(input_data, Vector):
            # 将普通矢量转换为特定类型矢量
            return vector_class(input_data.data[0], input_data.data[1], input_data.data[2])
        else:
            if len(input_data) == 3:
                return vector_class(input_data[0], input_data[1], input_data[2])
            else:
                return vector_class(input_data[0], input_data[1], 0)

    def add_gravity(self, g=9.8, direction=(0, -1, 0)):
        """
        添加重力
        :param g: 重力加速度大小，默认9.8m/s²
        :param direction: 重力方向向量，默认(0,-1,0)表示向下
        """
        # 处理方向输入，并归一化
        if not isinstance(direction, Vector):
            direction = Vector(*direction)
        direction_vec = direction.normalized()

        # 创建重力矢量（Force类）
        gravity_vec = Force(
            direction_vec.data[0] * self.mass * g,
            direction_vec.data[1] * self.mass * g,
            direction_vec.data[2] * self.mass * g
        )
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
        # 处理角度输入（包括单个角度值）
        if isinstance(direction, (int, float)):
            # 角度输入（度数）
            rad = math.radians(direction)
            direction_vec = Vector(math.cos(rad), math.sin(rad), 0).normalized()
        elif isinstance(direction, Vector):
            # 已经是矢量对象
            direction_vec = direction.normalized()
        elif hasattr(direction, "__len__"):
            if len(direction) == 1:
                # 单个元素的角度值（元组形式）
                rad = math.radians(direction[0])
                direction_vec = Vector(math.cos(rad), math.sin(rad), 0).normalized()
            elif len(direction) == 2:
                # 欧拉角(alpha,beta)
                alpha, beta = direction
                alpha_rad = math.radians(alpha)
                beta_rad = math.radians(beta)
                x = math.cos(alpha_rad) * math.cos(beta_rad)
                y = math.sin(alpha_rad) * math.cos(beta_rad)
                z = math.sin(beta_rad)
                direction_vec = Vector(x, y, z).normalized()
            else:
                # 方向向量(x,y,z)
                direction_vec = Vector(*direction[:3]).normalized()
        else:
            raise TypeError(f"不支援的方向类型: {type(direction)}")

        # 创建力矢量
        force_vec = Force(
            direction_vec.data[0] * magnitude,
            direction_vec.data[1] * magnitude,
            direction_vec.data[2] * magnitude
        )
        self.forces.append((force_name, force_vec))
        return force_vec

    def add_contact_surface(self, surface_id: str, other_system, normal_direction, friction_coeff=0.0):
        """
        添加与其他系统的接触面
        :param surface_id: 接触面唯一标识符
        :param other_system: 接触的另一系统对象
        :param normal_direction: 接触面法线方向
            二维情况: 法线角度(度)或单个角度的元组
            三维情况: (x,y,z)法线向量或Vector对象
        :param friction_coeff: 摩擦系数(0表示光滑)
        """
        # 处理法线方向
        if isinstance(normal_direction, (int, float)):
            # 二维情况: 角度转向量
            rad = math.radians(normal_direction)
            normal_vec = Vector(math.cos(rad), math.sin(rad), 0).normalized()
        elif isinstance(normal_direction, Vector):
            # 已经是矢量对象
            normal_vec = normal_direction.normalized()
        elif hasattr(normal_direction, "__len__"):
            if len(normal_direction) == 1:
                # 单个角度的元组
                rad = math.radians(normal_direction[0])
                normal_vec = Vector(math.cos(rad), math.sin(rad), 0).normalized()
            else:
                # 三维方向向量
                normal_vec = Vector(*normal_direction[:3]).normalized()
        else:
            raise TypeError(f"不支援的法线方向类型: {type(normal_direction)}")

        contact = {
            'id': surface_id,
            'system1': self,
            'system2': other_system,
            'normal_direction': normal_vec,
            'friction_coeff': friction_coeff
        }
        self.contact_surfaces[surface_id] = ContactSurface(**contact)
        other_system.contact_surfaces.append(contact)
        return contact


    def calculate_net_force(self):
        """
        计算物体所受合力
        :return: 合力Vector对象
        :raises: ZeroDivisionError 当物体质量为0时
        """
        if self.mass == 0:
            raise ZeroDivisionError("Cannot calculate net force for zero mass object")

        # 创建零力矢量
        net_force = Force(0, 0, 0)
        for _, force_vec in self.forces:
            # 确保所有力都是Force类型
            if isinstance(force_vec, Force):
                net_force += force_vec
            else:
                try:
                    # 尝试转换为Force矢量
                    net_force += Force(force_vec.data[0], force_vec.data[1], force_vec.data[2])
                except:
                    raise TypeError(f"Force vector has unexpected type: {type(force_vec)}")

        return net_force

    def update_kinematics(self, time_delta=0.1):
        """
        根据当前合力更新运动状态（牛顿第二定律）
        :param time_delta: 时间间隔(s)
        """
        # 计算加速度：a = F/m
        net_force = self.calculate_net_force()
        acceleration_data = net_force.data / self.mass
        self.acceleration = Vector(
            acceleration_data[0],
            acceleration_data[1],
            acceleration_data[2],
            dimension=Dimension(length=1, time=-2)
        )

        # 使用当前加速度和当前速度更新位置
        # 位置更新公式：p_new = p_old + v_old * Δt + 0.5 * a * (Δt)^2

        # 速度贡献的位置变化
        displacement_from_velocity = Displacement(
            self.velocity.data[0] * time_delta,
            self.velocity.data[1] * time_delta,
            self.velocity.data[2] * time_delta
        )

        # 加速度贡献的位置变化
        displacement_from_acceleration = Displacement(
            0.5 * self.acceleration.data[0] * (time_delta ** 2),
            0.5 * self.acceleration.data[1] * (time_delta ** 2),
            0.5 * self.acceleration.data[2] * (time_delta ** 2)
        )

        self.position += displacement_from_velocity
        self.position += displacement_from_acceleration

        # 使用加速度更新速度：v_new = v_old + a * Δt
        velocity_change_data = [
            self.acceleration.data[0] * time_delta,
            self.acceleration.data[1] * time_delta,
            self.acceleration.data[2] * time_delta
        ]
        velocity_change = Velocity(
            velocity_change_data[0],
            velocity_change_data[1],
            velocity_change_data[2]
        )
        self.velocity += velocity_change

    def to_dict(self):
        """将系统状态转为字典格式，便于JSON序列化"""
        return {
            'id': self.id,
            'mass': self.mass,
            'position': self.position.as_tuple(),
            'velocity': self.velocity.as_tuple(),
            'acceleration': self.acceleration.as_tuple(),
            'forces': [
                (name, force.as_tuple())
                for name, force in self.forces
            ],
            'contact_surfaces': [
                {
                    'id': cs['id'],
                    'other_system': cs['system2'].id,
                    'normal_direction': cs['normal_direction'].as_tuple(),
                    'friction_coeff': cs['friction_coeff']
                }
                for cs in self.contact_surfaces
            ]
        }


# 测试用例
# 测试用例
if __name__ == "__main__":
    # 创建两个物理系统
    system1 = PhysicalSystem("sys1", 10.0, (0, 0, 0))
    system2 = PhysicalSystem("sys2", 5.0, (2, 0, 0))

    # 添加重力
    system1.add_gravity()
    system2.add_gravity()

    # 添加外部力 - 各种方向输入方式
    system1.add_external_force("push", 20.0, 45)  # 标量角度
    system1.add_external_force("pull", 15.0, (30,))  # 单元素元组角度
    system2.add_external_force("lift", 10.0, (0, 45))  # 欧拉角
    system2.add_external_force("drag", 5.0, (1, 0, 0))  # 方向向量

    # 添加接触面 - 各种法线方向输入方式
    contact1 = system1.add_contact_surface("contact1", system2, 0)  # 0度法线
    contact2 = system1.add_contact_surface("contact2", system2, (90,))  # 90度法线
    contact3 = system1.add_contact_surface("contact3", system2, (1, 0, 0))  # 三维法线

    # 计算合力
    print(f"System1 net force: {system1.calculate_net_force()}")
    print(f"System2 net force: {system2.calculate_net_force()}")

    # 更新运动状态
    print("\nBefore update:")
    print(f"System1 position: {system1.position}")
    print(f"System2 velocity: {system2.velocity}")


    # 添加同一个
    try :
        system1.add_contact_surface(
            "contact1", system2,
            normal_direction=(1, 0, 0),  # 法线方向沿x轴
            friction_coeff=0.2
        )
        # 打印所有接触面
        print("\nAll contact surfaces:")
        for contact in system1.contact_surfaces:
            print(f"Contact {contact['id']} - {contact['system2'].id}")
    except ValueError as e:
        print(f"Error: {e}")

