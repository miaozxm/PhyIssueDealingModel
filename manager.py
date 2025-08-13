# manager.py
from physical_entity import *


class BasePhysicsManager:
    """基础物理系统管理类，提供实体和时间的通用管理"""
    
    def __init__(self):
        self.entities = {}
        self.time = 0.0
    
    def add_entity(self, entity: PhysicalEntity):
        """添加物理实体到系统
        
        Args:
            entity: 要添加的物理实体
            
        Raises:
            ValueError: 当实体ID已存在时
        """
        if entity.id in self.entities:
            raise ValueError(f"实体ID '{entity.id}' 已存在")
        self.entities[entity.id] = entity


class MechanicsManager(BasePhysicsManager):
    """力学系统管理类，处理力学相关物理模拟"""
    
    def __init__(self):
        super().__init__()
        self.contact_surfaces = {}  # 接触面字典
        self.gravity = (0, -9.8, 0)  # 默认重力加速度(m/s²)

    def add_contact_surface(self, surface_id: str, normal, offset=0.0):
        """添加接触面
        
        Args:
            surface_id: 接触面ID
            normal: 法线向量
            offset: 接触面偏移量
        """
        self.contact_surfaces[surface_id] = {
            'normal': Vector(normal[0], normal[1], normal[2]).normalize(),
            'offset': offset
        }

    def apply_force(self, entity_id: str, force_name: str, force):
        """对实体施加力
        
        Args:
            entity_id: 实体ID
            force_name: 力名称(如'gravity', 'friction')
            force: 力向量或Force对象
        """
        entity = self.entities[entity_id]
        if isinstance(force, Force):
            force_vec = force
        else:
            force_vec = Force(force[0], force[1], force[2])
        entity.forces.append((force_name, force_vec))

    def update_kinematics(self, dt: float):
        """更新所有实体的运动学状态
        
        Args:
            dt: 时间步长(秒)
        """
        for entity in self.entities.values():
            # 计算合力
            total_force = Vector(0, 0, 0)
            for name, force in entity.forces:
                if name == 'gravity' and isinstance(entity, MasslessEntity):
                    continue  # 质量为零物体不受重力
                total_force += force
            
            # 计算加速度 F=ma
            if entity.mass > 0:
                entity.acceleration = Acceleration(
                    total_force.x / entity.mass,
                    total_force.y / entity.mass,
                    total_force.z / entity.mass
                )
            
            # 更新速度和位置
            entity.velocity += entity.acceleration * dt
            entity.position += entity.velocity * dt
            
            # 清空力列表
            entity.forces.clear()

    def step(self, dt: float):
        """执行一个时间步长的物理模拟
        
        Args:
            dt: 时间步长(秒)
        """
        self.update_kinematics(dt)
        self.time += dt

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





# 测试用例
if __name__ == "__main__":
    # 创建物理管理器
    manager = MechanicsManager()

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