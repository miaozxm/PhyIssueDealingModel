from vector import *


class PhysicalEntity:
    """物理实体基类，表示参与物理模拟的物体。

    属性：
        id (str): 实体唯一标识符
        mass (float): 质量(kg)
        position (Displacement): 位置矢量
        velocity (Velocity): 速度矢量
        acceleration (Acceleration): 加速度矢量
        forces (list): 作用在实体上的力列表，每个元素为(force_name, force)元组
    """

    def __init__(self, entity_id: str, mass: float, position, velocity=(0, 0, 0), acceleration=(0, 0, 0)):
        """初始化物理实体。

        Args:
            entity_id: 实体唯一标识符
            mass: 质量(kg)
            position: 位置，可以是元组、Vector或Displacement对象
            velocity: 速度，可以是元组、Vector或Velocity对象，默认为(0,0,0)
            acceleration: 加速度，可以是元组、Vector或Acceleration对象，默认为(0,0,0)
        """
        self.id = entity_id
        self.mass = mass
        self.position = self._process_vector(position, Displacement)
        self.velocity = self._process_vector(velocity, Velocity)
        self.acceleration = self._process_vector(acceleration, Acceleration)
        self.forces = []  # 存储(force_name, force)元组

    @staticmethod
    def _process_vector(input_data, vector_class):
        """将输入数据转换为指定类型的矢量对象。

        支持多种输入格式：
        - 已经是目标矢量类实例
        - Vector对象
        - 元组(2或3个元素)

        Args:
            input_data: 输入数据
            vector_class: 目标矢量类(Displacement/Velocity/Acceleration)

        Returns:
            转换后的矢量对象

        Raises:
            TypeError: 当输入类型不支持时
        """
        if isinstance(input_data, vector_class):
            return input_data
        elif isinstance(input_data, Vector):
            return vector_class(input_data.x, input_data.y, input_data.z)
        elif isinstance(input_data, (tuple, list)) and len(input_data) in (2, 3):
            if len(input_data) == 3:
                return vector_class(input_data[0], input_data[1], input_data[2])
            else:
                return vector_class(input_data[0], input_data[1], 0)
        else:
            raise TypeError(f"不支持的向量输入类型: {type(input_data)}")

    def __repr__(self):
        """生成实体的字符串表示。

        Returns:
            str: 包含ID、质量和位置、速度的字符串
        """
        return (f"PhysicalEntity({self.id}, mass={self.mass}kg, "
                f"position={self.position.as_tuple()}, "
                f"velocity={self.velocity.as_tuple()})")


class MasslessEntity(PhysicalEntity):
    """质量为零的物理实体，如轻杆、轻绳等理想模型。

    特性：
    - 质量固定为0
    - 不受重力影响
    - 合力必须为零(物理约束)
    """

    def __init__(self, entity_id: str, position, **kwargs):
        """初始化质量为零的实体。

        Args:
            entity_id: 实体唯一标识符
            position: 位置
            **kwargs: 其他传递给PhysicalEntity的参数（不能包含mass）
        """
        # 明确移除mass参数以避免冲突
        kwargs.pop('mass', None)
        super().__init__(entity_id, 0.0, position, **kwargs)

    def __repr__(self):
        """生成质量为零实体的字符串表示。

        Returns:
            str: 包含ID的字符串
        """
        return f"MasslessEntity({self.id})"


class RigidBody(PhysicalEntity):
    """刚体（有质量）"""
    pass


class ElectricallyChargedEntity(PhysicalEntity):
    """带电体"""

    def __init__(self, entity_id: str, charge: float, mass, position,**kwargs):
        """
        Args:
            entity_id: 实体唯一标识符
            charge: 电荷量(库仑)
            **kwargs: 传递给PhysicalEntity的初始化参数
        """
        super().__init__(entity_id, mass, position, **kwargs)
        self.charge = charge

    def __repr__(self):
        return f"ElectricallyChargedEntity({self.id}, charge={self.charge}C)"
