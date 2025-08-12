import math


class Dimension:
    """量纲类，表示物理量的七个基本量纲"""

    def __init__(self,
                 length: float = 0.0,  # 长度 (L)
                 mass: float = 0.0,  # 质量 (M)
                 time: float = 0.0,  # 时间 (T)
                 current: float = 0.0,  # 电流 (I)
                 temperature: float = 0.0,  # 热力学温度 (Θ)
                 amount: float = 0.0,  # 物质的量 (N)
                 luminous_intensity: float = 0.0  # 发光强度 (J)
                 ):
        self.exponents = {
            'length': length,
            'mass': mass,
            'time': time,
            'current': current,
            'temperature': temperature,
            'amount': amount,
            'luminous_intensity': luminous_intensity
        }

    def __getattr__(self, name):
        if name in self.exponents:
            return self.exponents[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __eq__(self, other):
        return all(self.exponents[k] == other.exponents[k] for k in self.exponents)

    def __mul__(self, other):
        return Dimension(**{
            k: self.exponents[k] + other.exponents[k] for k in self.exponents
        })

    def __truediv__(self, other):
        return Dimension(**{
            k: self.exponents[k] - other.exponents[k] for k in self.exponents
        })

    def __repr__(self):
        parts = [f"{k}^{v}" for k, v in self.exponents.items() if v != 0]
        return f"Dimension({', '.join(parts)})" if parts else "Dimension()"

    def as_dict(self, compact=False):
        if compact:
            return {k: v for k, v in self.exponents.items() if v != 0}
        return self.exponents.copy()

    @classmethod
    def common_quantities(cls):
        return {
            'length': Dimension(length=1),
            'mass': Dimension(mass=1),
            'time': Dimension(time=1),
            'current': Dimension(current=1),
            'temperature': Dimension(temperature=1),
            'amount': Dimension(amount=1),
            'luminous_intensity': Dimension(luminous_intensity=1),
            'velocity': Dimension(length=1, time=-1),
            'acceleration': Dimension(length=1, time=-2),
            'force': Dimension(mass=1, length=1, time=-2),
            'energy': Dimension(mass=1, length=2, time=-2),
            'power': Dimension(mass=1, length=2, time=-3),
            'pressure': Dimension(mass=1, length=-1, time=-2),
            'frequency': Dimension(time=-1),
            'electric_charge': Dimension(current=1, time=1),
            'voltage': Dimension(mass=1, length=2, current=-1, time=-3),
            'resistance': Dimension(mass=1, length=2, current=-2, time=-3),
            'capacitance': Dimension(current=2, length=-2, mass=-1, time=4),
            'inductance': Dimension(mass=1, length=2, current=-2, time=-2),
            'magnetic_flux': Dimension(mass=1, length=2, current=-1, time=-2),
            'magnetic_field': Dimension(mass=1, current=-1, time=-2),
            'luminous_flux': Dimension(luminous_intensity=1),
            'illuminance': Dimension(luminous_intensity=1, length=-2)
        }


class Vector:
    """三维矢量类，支持量纲管理"""

    def __init__(self, x, y, z=0.0, dimension=Dimension()):
        # 确保所有分量都是float类型
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.dimension = dimension

    @property
    def data(self):
        """返回分量的元组"""
        return self.x, self.y, self.z

    def __add__(self, other):
        if self.dimension != other.dimension:
            raise ValueError("矢量量纲不匹配，无法相加")
        return Vector(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
            dimension=self.dimension
        )

    def __sub__(self, other):
        if self.dimension != other.dimension:
            raise ValueError("矢量量纲不匹配，无法相减")
        return Vector(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
            dimension=self.dimension
        )

    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            raise TypeError("标量必须是数值类型")
        return Vector(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar,
            dimension=self.dimension
        )

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __neg__(self):
        """支持一元负号操作"""
        return Vector(-self.x, -self.y, -self.z, dimension=self.dimension)

    def magnitude(self):
        """计算矢量大小"""
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalized(self):
        """返回归一化后的矢量（无量纲）"""
        mag = self.magnitude()
        if mag > 0:
            return Vector(
                self.x / mag,
                self.y / mag,
                self.z / mag,
                dimension=Dimension()
            )
        return Vector(0, 0, 0, dimension=Dimension())

    def dot(self, other):
        """点积（返回无量纲数值）"""
        if self.dimension != other.dimension:
            raise ValueError("矢量量纲不匹配，无法计算点积")
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        """叉积（量纲为两个矢量量纲之和）"""
        new_dimension = Dimension(
            self.dimension.length + other.dimension.length,
            self.dimension.mass + other.dimension.mass,
            self.dimension.time + other.dimension.time,
            self.dimension.current + other.dimension.current,
            self.dimension.temperature + other.dimension.temperature,
            self.dimension.amount + other.dimension.amount,
            self.dimension.luminous_intensity + other.dimension.luminous_intensity
        )
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
            dimension=new_dimension
        )

    def as_tuple(self):
        """转换为元组"""
        return self.x, self.y, self.z

    def __repr__(self):
        return (f"Vector({self.x:.2f}, {self.y:.2f}, {self.z:.2f}) "
                f"with {self.dimension}")


class Displacement(Vector):
    """位移矢量类"""

    def __init__(self, x, y, z=0.0):
        super().__init__(x, y, z, dimension=Dimension(length=1))


class Velocity(Vector):
    """速度矢量类"""

    def __init__(self, x, y, z=0.0):
        super().__init__(x, y, z, dimension=Dimension(length=1, time=-1))


class Force(Vector):
    """力矢量类"""

    def __init__(self, x, y, z=0.0):
        super().__init__(x, y, z, dimension=Dimension(length=1, mass=1, time=-2))


class Acceleration(Vector):
    """加速度矢量类"""

    def __init__(self, x, y, z=0.0):
        super().__init__(x, y, z, dimension=Dimension(length=1, time=-2))


class PhysicalEntity:
    """物理实体基类（纯数据类）"""

    def __init__(self, entity_id: str, mass: float, position, velocity=(0, 0, 0), acceleration=(0, 0, 0)):
        self.id = entity_id
        self.mass = mass
        self.position = self._process_vector(position, Displacement)
        self.velocity = self._process_vector(velocity, Velocity)
        self.acceleration = self._process_vector(acceleration, Acceleration)
        self.forces = []

    @staticmethod
    def _process_vector(input_data, vector_class):
        if isinstance(input_data, vector_class):
            return input_data
        elif isinstance(input_data, Vector):
            return vector_class(input_data.x, input_data.y, input_data.z)
        else:
            if len(input_data) == 3:
                return vector_class(input_data[0], input_data[1], input_data[2])
            else:
                return vector_class(input_data[0], input_data[1], 0)

    def __repr__(self):
        return (f"PhysicalEntity({self.id}, mass={self.mass}kg, "
                f"position={self.position.as_tuple()}, "
                f"velocity={self.velocity.as_tuple()})")


class PhysicsManager:
    """物理系统管理类"""

    def __init__(self):
        self.entities = {}
        self.contact_surfaces = {}
        self.time = 0.0

    def add_entity(self, entity: PhysicalEntity):
        if entity.id in self.entities:
            raise ValueError(f"实体 {entity.id} 已存在")
        self.entities[entity.id] = entity

    def add_contact_surface(self, surface: 'ContactSurface'):
        if surface.id in self.contact_surfaces:
            raise ValueError(f"接触面 {surface.id} 已存在")
        self.contact_surfaces[surface.id] = surface

    def apply_gravity(self, entity_id: str, g=9.8, direction=(0, -1, 0)):
        entity = self.get_entity(entity_id)

        # 质量为零的物体不受重力
        if entity.mass == 0:
            return Force(0, 0, 0)

        if not isinstance(direction, Vector):
            direction = Vector(*direction)
        direction_vec = direction.normalized()

        gravity = Force(
            direction_vec.x * entity.mass * g,
            direction_vec.y * entity.mass * g,
            direction_vec.z * entity.mass * g
        )
        entity.forces.append(('gravity', gravity))
        return gravity

    def apply_external_force(self, entity_id: str, force_name: str, magnitude: float, direction):
        entity = self.get_entity(entity_id)

        if isinstance(direction, (int, float)):
            rad = math.radians(direction)
            direction_vec = Vector(math.cos(rad), math.sin(rad), 0).normalized()
        elif isinstance(direction, Vector):
            direction_vec = direction.normalized()
        elif hasattr(direction, "__len__"):
            if len(direction) == 1:
                rad = math.radians(direction[0])
                direction_vec = Vector(math.cos(rad), math.sin(rad), 0).normalized()
            elif len(direction) == 2:
                direction_vec = self._euler_to_vector(*direction)
            else:
                direction_vec = Vector(*direction[:3]).normalized()
        else:
            raise TypeError(f"不支持的方向类型: {type(direction)}")

        force = Force(
            direction_vec.x * magnitude,
            direction_vec.y * magnitude,
            direction_vec.z * magnitude
        )
        entity.forces.append((force_name, force))
        return force

    @staticmethod
    def _euler_to_vector(alpha, beta):
        alpha_rad = math.radians(alpha)
        beta_rad = math.radians(beta)
        x = math.cos(alpha_rad) * math.cos(beta_rad)
        y = math.sin(alpha_rad) * math.cos(beta_rad)
        z = math.sin(beta_rad)
        return Vector(x, y, z).normalized()

    def connect_entities(self, surface_id: str, entity1_id: str, entity2_id: str,
                         normal_direction, friction_coeff=0.0,friction_force=Force(1, 0, 0)):
        entity1 = self.get_entity(entity1_id)
        entity2 = self.get_entity(entity2_id)

        if isinstance(normal_direction, (int, float)):
            rad = math.radians(normal_direction)
            normal_vec = Vector(math.cos(rad), math.sin(rad), 0).normalized()
        elif isinstance(normal_direction, Vector):
            normal_vec = normal_direction.normalized()
        elif hasattr(normal_direction, "__len__"):
            if len(normal_direction) == 1:
                rad = math.radians(normal_direction[0])
                normal_vec = Vector(math.cos(rad), math.sin(rad), 0).normalized()
            else:
                normal_vec = Vector(*normal_direction[:3]).normalized()
        else:
            raise TypeError(f"不支持的法线方向类型: {type(normal_direction)}")

        contact = ContactSurface(
            surface_id=surface_id,
            entity1=entity1,
            entity2=entity2,
            normal_direction=normal_vec,
            friction_coeff=friction_coeff,
            friction_force=friction_force
        )
        self.contact_surfaces[surface_id] = contact
        return contact

    def calculate_net_force(self, entity_id: str):
        entity = self.get_entity(entity_id)

        net_force = Force(0, 0, 0)
        for _, force in entity.forces:
            net_force += force

        for surface in self.contact_surfaces.values():
            if surface.entity1.id == entity_id or surface.entity2.id == entity_id:
                net_force += surface.calculate_force()

        # 质量为零的物体合力必须为零
        if entity.mass == 0 and net_force.magnitude() > 1e-5:
            raise RuntimeError(f"质量为零的物体 '{entity.id}' 受到的合力不为零: {net_force}")

        return net_force

    def update_physics(self, time_delta=0.1):
        for surface in self.contact_surfaces.values():
            surface.update(Force(5, 0, 0))

        for entity_id in self.entities:
            self.update_entity_kinematics(entity_id, time_delta)

        self.time += time_delta

    def update_entity_kinematics(self, entity_id: str, time_delta=0.1):
        entity = self.get_entity(entity_id)

        net_force = self.calculate_net_force(entity_id)

        # 质量为零的物体不受加速度影响
        if entity.mass == 0:
            # 只更新位置（基于速度）
            displacement = Displacement(
                entity.velocity.x * time_delta,
                entity.velocity.y * time_delta,
                entity.velocity.z * time_delta
            )
            entity.position += displacement
            return

        # 计算加速度
        acceleration_data = (net_force.x / entity.mass,
                             net_force.y / entity.mass,
                             net_force.z / entity.mass)
        entity.acceleration = Acceleration(*acceleration_data)

        # 更新位置
        displacement_from_velocity = Displacement(
            entity.velocity.x * time_delta,
            entity.velocity.y * time_delta,
            entity.velocity.z * time_delta
        )

        displacement_from_acceleration = Displacement(
            0.5 * entity.acceleration.x * (time_delta ** 2),
            0.5 * entity.acceleration.y * (time_delta ** 2),
            0.5 * entity.acceleration.z * (time_delta ** 2)
        )

        entity.position += displacement_from_velocity
        entity.position += displacement_from_acceleration

        # 更新速度
        velocity_change = Velocity(
            entity.acceleration.x * time_delta,
            entity.acceleration.y * time_delta,
            entity.acceleration.z * time_delta
        )
        entity.velocity += velocity_change

    def get_entity(self, entity_id: str) -> PhysicalEntity:
        if entity_id not in self.entities:
            raise KeyError(f"实体 {entity_id} 不存在")
        return self.entities[entity_id]


class ContactSurface:
    """接触面类"""

    def __init__(self, surface_id: str, entity1: PhysicalEntity, entity2: PhysicalEntity,
                 normal_direction, friction_coeff: float = 0.0, elastic_force=Force(0, 0, 0),
                 friction_force=Force(0, 0, 0),friction_type="static"):
        """
        初始化接触面
        :param surface_id: 接触面唯一标识符
        :param entity1: 第一个物理系统
        :param entity2: 第二个物理系统
        :param normal_direction: 接触面法线方向
        :param friction_coeff: 摩擦系数
        :param elastic_force: 弹力
        :param friction_force: 摩擦力
        :param friction_type: 摩擦类型 “static” or “kinetic”
        """

        self.id = surface_id
        self.entity1 = entity1
        self.entity2 = entity2
        self.normal_direction = normal_direction.normalized()
        self.friction_coeff = friction_coeff

        self.elastic_force = elastic_force
        self.friction_type = friction_type

        self.friction_force = friction_force

    def update(self, elastic_force=None):
        relative_velocity = self.entity1.velocity - self.entity2.velocity

        # 使用容差值判断相对速度是否为零
        if relative_velocity.magnitude() < 1e-5:
            self.friction_type = "static"
        else:
            self.friction_type = "kinetic"

        # 更新弹力
        if elastic_force is not None:
            self.elastic_force = elastic_force


    def calculate_force(self):
        # 计算摩擦力
        if self.friction_coeff > 0:
            relative_velocity = self.entity1.velocity - self.entity2.velocity
            relative_velocity_magnitude = relative_velocity.magnitude()

            # 避免除以零错误
            if relative_velocity_magnitude > 1e-5:
                friction_direction = -(relative_velocity.normalized())
            else:
                # 如果相对速度为零，摩擦力方向设为0
                friction_direction = Vector(0, 0, 0)

            friction_magnitude = self.friction_coeff * self.elastic_force.magnitude()
            self.friction_force = Force(
                friction_direction.x * friction_magnitude,
                friction_direction.y * friction_magnitude,
                friction_direction.z * friction_magnitude
            )
        return self.friction_force



    def __repr__(self):
        return f"ContactSurface({self.id}, entities=({self.entity1.id},{self.entity2.id})"


class MasslessEntity(PhysicalEntity):
    """质量为零的物理实体（如轻杆、轻绳）"""

    def __init__(self, entity_id: str, position, **kwargs):
        super().__init__(entity_id, 0.0, position, **kwargs)

    def __repr__(self):
        return f"MasslessEntity({self.id})"


class RigidBody(PhysicalEntity):
    """刚体（有质量）"""
    pass


class ElectricallyChargedEntity(PhysicalEntity):
    """带电体"""

    def __init__(self, entity_id: str, charge: float, **kwargs):
        super().__init__(entity_id, **kwargs)
        self.charge = charge

    def __repr__(self):
        return f"ElectricallyChargedEntity({self.id}, charge={self.charge}C)"


# 测试用例
if __name__ == "__main__":
    # 创建物理管理器
    manager = PhysicsManager()

    # 创建物理实体
    box1 = RigidBody("box1", 5.0, position=(0, 0, 0))
    box2 = RigidBody("box2", 3.0, position=(2, 0, 0))
    rope = MasslessEntity("rope", position=(1, 1, 0))

    # 添加实体到管理器
    manager.add_entity(box1)
    manager.add_entity(box2)
    manager.add_entity(rope)

    # 为实体添加重力（绳子质量为零，不受重力）
    manager.apply_gravity("box1")
    manager.apply_gravity("box2")
    # 绳子质量为零，不受重力
    # manager.apply_gravity("rope")

    # 连接两个盒子并创建接触面，设置穿透深度为0.1米
    manager.connect_entities("contact1", "box1", "box2",
                             normal_direction=(1, 0, 0),
                             friction_coeff=0.2,
                             )  # 设置穿透深度

    # 输出初始状态
    print("初始状态:")
    print(f"box1位置: {box1.position.as_tuple()}")
    print(f"box2位置: {box2.position.as_tuple()}")
    print(f"接触面状态: {manager.contact_surfaces['contact1']}")

    # 更新物理系统
    print("\n更新物理系统...")
    try:
        manager.update_physics(time_delta=0.1)
    except RuntimeError as e:
        print(f"正确捕获异常: {e}")

    # 输出更新后的状态
    print("\n更新后状态:")
    print(f"box1位置: {box1.position.as_tuple()}")
    print(f"box2位置: {box2.position.as_tuple()}")
    print(f"box1速度: {box1.velocity.as_tuple()}")
    print(f"box1加速度: {box1.acceleration.as_tuple()}")

    # 测试质量为零实体的限制
    try:
        print("\n尝试计算绳子的合力...")
        force_on_rope = manager.calculate_net_force("rope")
        print(f"绳子合力: {force_on_rope}")
    except RuntimeError as e:
        print(f"正确捕获异常: {e}")