
from vector import Vector, Force, Displacement
from physical_entity import PhysicalEntity, ElectricallyChargedEntity


class PhysicsField:
    """物理场基类，表示空间中的物理场（如重力场、电场）"""

    def __init__(self, name, strength=1.0, direction=(0, -1, 0)):
        """
        初始化物理场

        Args:
            name: 场名称
            strength: 场强度
            direction: 场方向向量
        """
        self.name = name
        self.strength = strength
        self.direction = Vector(*direction).normalized()

    def calculate_force(self, entity, position):
        """
        计算场对实体施加的力

        Args:
            entity: 物理实体
            position: 实体位置

        Returns:
            Force: 施加在实体上的力
        """
        raise NotImplementedError("子类必须实现此方法")

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, strength={self.strength})"


class UniformGravityField(PhysicsField):
    """均匀重力场"""

    def calculate_force(self, entity, position):
        """
        计算重力：F = m * g * direction

        Args:
            entity: 物理实体
            position: 实体位置（忽略，因为均匀场）

        Returns:
            Force: 重力矢量
        """
        # 质量为零的物体不受重力
        if entity.mass == 0:
            return Force(0, 0, 0)

        magnitude = entity.mass * self.strength
        return Force(
            self.direction.x * magnitude,
            self.direction.y * magnitude,
            self.direction.z * magnitude
        )


class PointChargeField(PhysicsField):
    """点电荷电场"""

    def __init__(self, name, charge, position=(0, 0, 0)):
        """
        初始化点电荷电场

        Args:
            name: 场名称
            charge: 电荷量（库仑）
            position: 电荷位置
        """
        super().__init__(name)
        self.charge = charge
        self.position = Displacement(*position)
        # 库仑常数 (1/(4πε₀))
        self.k = 8.99e9  # N·m²/C²

    def calculate_force(self, entity, position):
        """
        计算电场力：F = k * (q1 * q2) / r² * direction

        Args:
            entity: 带电实体
            position: 实体位置

        Returns:
            Force: 电场力矢量
        """
        # 仅对带电实体施加力
        if not isinstance(entity, ElectricallyChargedEntity):
            return Force(0, 0, 0)

        # 计算位置向量
        # print(self.position, position)
        r_vec = position - self.position
        distance = r_vec.magnitude()

        # 避免除以零
        if distance < 1e-5:
            return Force(0, 0, 0)

        # 计算力的大小 (库仑定律)
        force_magnitude = self.k * abs(self.charge * entity.charge) / (distance ** 2)

        # 计算方向（同种电荷相斥，异种电荷相吸）
        direction = r_vec.normalized()
        if self.charge * entity.charge > 0:  # 同种电荷
            force = direction * force_magnitude
        else:  # 异种电荷
            force = direction * -force_magnitude

        return Force(force.x, force.y, force.z)


class FieldSystem:
    """物理场系统，管理多个物理场及其相互作用"""

    def __init__(self):
        self.fields = {}

    def add_field(self, field):
        """添加物理场到系统"""
        if field.name in self.fields:
            raise ValueError(f"场名称 '{field.name}' 已存在")
        self.fields[field.name] = field

    def remove_field(self, name):
        """从系统中移除物理场"""
        if name in self.fields:
            del self.fields[name]

    def calculate_total_force(self, entity, position):
        """
        计算所有场对实体施加的合力

        Args:
            entity: 物理实体
            position: 实体位置

        Returns:
            Force: 合力矢量
        """
        total_force = Force(0, 0, 0)
        for field in self.fields.values():

            total_force += field.calculate_force(entity, position)
        return total_force

    def visualize_field(self, entity_type, bounds, resolution=10):
        """
        可视化场在空间中的分布

        Args:
            entity_type: 用于探测场的实体类型（如质量、电荷）
            bounds: 空间边界 ((x_min, x_max), (y_min, y_max))
            resolution: 空间分辨率

        Returns:
            list: 场矢量列表 [(x, y, force_x, force_y), ...]
        """
        field_vectors = []
        x_step = (bounds[0][1] - bounds[0][0]) / resolution
        y_step = (bounds[1][1] - bounds[1][0]) / resolution

        # 创建探测实体
        if entity_type == "mass":
            probe = PhysicalEntity("field_probe", position=(0, 0, 0),mass=1.0)
        elif entity_type == "charge":
            probe = ElectricallyChargedEntity("field_probe", charge=1e-9, mass=1.0, position=(0, 0, 0))
        else:
            raise ValueError("不支持的实体类型")

        # 遍历空间点计算场强
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                x = bounds[0][0] + i * x_step
                y = bounds[1][0] + j * y_step
                position = Displacement(x, y, 0)

                force = self.calculate_total_force(probe, position)
                field_vectors.append((x, y, force.x, force.y))

        return field_vectors

    def __repr__(self):
        return f"FieldSystem({len(self.fields)} fields)"


# 测试用例
if __name__ == "__main__":
    # 创建场系统
    field_system = FieldSystem()

    # 添加重力场
    gravity = UniformGravityField("Earth Gravity", strength=9.8)
    field_system.add_field(gravity)

    # 添加点电荷
    positive_charge = PointChargeField("Positive Charge", charge=1e-6, position=(5, 0, 0))
    field_system.add_field(positive_charge)

    # 创建测试实体
    test_mass = PhysicalEntity("test_mass", mass=2.0, position=(0, 0, 0))
    test_charge = ElectricallyChargedEntity("test_charge",charge=1e-9, mass=1.0, position=(3, 0, 0))

    # 计算重力
    gravity_force = field_system.calculate_total_force(test_mass, test_mass.position)
    print(f"重力: {gravity_force}")

    # 计算电场力
    electric_force = field_system.calculate_total_force(test_charge, test_charge.position)
    print(f"电场力: {electric_force}")

    # 可视化场
    bounds = ((0, 10), (0, 5))
    field_vectors = field_system.visualize_field("charge", bounds, resolution=5)

    print("\n场可视化数据:")
    for vec in field_vectors[:5]:  # 只打印前5个点
        print(f"位置: ({vec[0]:.1f}, {vec[1]:.1f}), 场强: ({vec[2]:.2e}, {vec[3]:.2e})")
