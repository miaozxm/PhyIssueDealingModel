import math





class PhysicalSystem:
    """
    表示物理系统中的单个物体，封装其力学属性和与其他系统的接触关系
    """

    def __init__(self, system_id: str, mass: float, position: tuple):
        """
        初始化物理系统
        :param system_id: 系统唯一标识符
        :param mass: 质量(kg)
        :param position: 位置坐标(x, y, z)
        """
        self.id = system_id
        self.mass = mass
        self.position = position if len(position) == 3 else (position[0], position[1], 0)  # 兼容二维输入
        self.forces = []  # 物体所受力的列表
        self.contact_surfaces = []  # 接触面对象列表
        self.acceleration = (0, 0, 0)  # 加速度向量(m/s²)
        self.velocity = (0, 0, 0)  # 速度向量(m/s)


    def add_gravity(self, g=9.8, direction=(0, -1, 0)):
        """
        添加重力
        :param g: 重力加速度大小，默认9.8m/s²
        :param direction: 重力方向向量，默认(0,-1,0)表示向下
        """
        # 归一化方向向量
        dir_x, dir_y, dir_z = direction
        magnitude = math.sqrt(dir_x**2 + dir_y**2 + dir_z**2)
        if magnitude > 0:
            dir_x, dir_y, dir_z = dir_x/magnitude, dir_y/magnitude, dir_z/magnitude
        
        gravity_force = ('gravity', 
                        self.mass * g * dir_x,
                        self.mass * g * dir_y,
                        self.mass * g * dir_z)
        self.forces.append(gravity_force)
        return gravity_force

    def add_external_force(self, force_name: str, magnitude: float, direction):
        """
        添加外部力
        :param force_name: 力的名称(如"拉力", "推力")
        :param magnitude: 力的大小(N)
        :param direction: 力的方向
            二维情况: 与水平正方向的夹角(度)
            三维情况: (x,y,z)方向向量或欧拉角(alpha,beta)
        """
        if isinstance(direction, (int, float)):
            # 二维情况: 角度输入
            rad = direction * (3.14159 / 180)
            force = (force_name, magnitude, math.cos(rad), math.sin(rad), 0)
        else:
            # 三维情况: 方向向量或欧拉角
            if len(direction) == 2:
                # 欧拉角(alpha,beta)
                alpha, beta = direction
                alpha_rad = alpha * (3.14159 / 180)
                beta_rad = beta * (3.14159 / 180)
                x = math.cos(alpha_rad) * math.cos(beta_rad)
                y = math.sin(alpha_rad) * math.cos(beta_rad)
                z = math.sin(beta_rad)
            else:
                # 方向向量(x,y,z)
                x, y, z = direction
                # 归一化
                mag = math.sqrt(x**2 + y**2 + z**2)
                if mag > 0:
                    x, y, z = x/mag, y/mag, z/mag
            
            force = (force_name, magnitude, x, y, z)
        
        self.forces.append(force)
        return force

    def add_contact_surface(self, surface_id: str, other_system, normal_direction, friction_coeff=0):
        """
        添加与其他系统的接触面
        :param surface_id: 接触面唯一标识符
        :param other_system: 接触的另一系统对象
        :param normal_direction: 接触面法线方向
            二维情况: 法线角度(度)
            三维情况: (x,y,z)法线向量
        :param friction_coeff: 摩擦系数(0表示光滑)
        """
        # 处理法线方向
        if isinstance(normal_direction, (int, float)):
            # 二维情况: 角度转向量
            rad = normal_direction * (3.14159 / 180)
            normal_vec = (math.cos(rad), math.sin(rad), 0)
        else:
            # 三维情况: 归一化向量
            x, y, z = normal_direction
            mag = math.sqrt(x**2 + y**2 + z**2)
            normal_vec = (x/mag, y/mag, z/mag) if mag > 0 else (0, 0, 1)

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
        计算物体所受合力的分量
        :return: (F_net_x, F_net_y, F_net_z)合力在x,y,z方向的分量
        :raises: ZeroDivisionError 当物体质量为0时
        """
        if self.mass == 0:
            raise ZeroDivisionError("Cannot calculate net force for zero mass object")
            
        F_net_x, F_net_y, F_net_z = 0, 0, 0

        for force in self.forces:
            if force[0] == 'gravity':
                # 重力可能有x,y,z分量
                if len(force) == 2:  # 旧版二维重力
                    F_net_y += force[1]
                else:  # 新版三维重力
                    F_net_x += force[1]
                    F_net_y += force[2]
                    F_net_z += force[3]
            else:
                # 外部力分解
                if len(force) == 3:  # 旧版二维力
                    magnitude, angle = force[1], force[2]
                    rad = angle * (3.14159 / 180)
                    F_net_x += magnitude * math.cos(rad)
                    F_net_y += magnitude * math.sin(rad)
                else:  # 新版三维力
                    magnitude, x, y, z = force[1], force[2], force[3], force[4]
                    F_net_x += magnitude * x
                    F_net_y += magnitude * y
                    F_net_z += magnitude * z

        # 处理接触力（后续与SystemManager配合实现）
        return (F_net_x, F_net_y, F_net_z)

    def update_kinematics(self, time_delta=0.1):
        """
        根据当前合力更新运动状态（牛顿第二定律）
        :param time_delta: 时间间隔(s)
        """
        F_net_x, F_net_y, F_net_z = self.calculate_net_force()
        ax = F_net_x / self.mass
        ay = F_net_y / self.mass
        az = F_net_z / self.mass
        self.acceleration = (ax, ay, az)

        # 更新速度和位置（欧拉法）
        vx, vy, vz = self.velocity
        px, py, pz = self.position

        new_vx = vx + ax * time_delta
        new_vy = vy + ay * time_delta
        new_vz = vz + az * time_delta
        new_px = px + vx * time_delta + 0.5 * ax * time_delta**2
        new_py = py + vy * time_delta + 0.5 * ay * time_delta**2
        new_pz = pz + vz * time_delta + 0.5 * az * time_delta**2

        self.velocity = (new_vx, new_vy, new_vz)
        self.position = (new_px, new_py, new_pz)

    def to_dict(self):
        """将系统状态转为字典格式，便于JSON序列化"""
        # 处理力数据以保持兼容性
        serialized_forces = []
        for force in self.forces:
            if force[0] == 'gravity':
                if len(force) == 2:  # 旧版二维重力
                    serialized_forces.append(('gravity', force[1]))
                else:  # 新版三维重力
                    serialized_forces.append(('gravity', force[1], force[2], force[3]))
            else:
                if len(force) == 3:  # 旧版二维力
                    serialized_forces.append((force[0], force[1], force[2]))
                else:  # 新版三维力
                    serialized_forces.append((force[0], force[1], force[2], force[3], force[4]))

        return {
            'id': self.id,
            'mass': self.mass,
            'position': self.position,
            'velocity': self.velocity,
            'acceleration': self.acceleration,
            'forces': serialized_forces,
            'contact_surfaces': [
                {
                    'id': cs['id'],
                    'other_system': cs['system2'].id,
                    'normal_direction': cs['normal_direction'],
                    'friction_coeff': cs['friction_coeff']
                }
                for cs in self.contact_surfaces
            ]
        }


