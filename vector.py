import numpy as np


class Dimension:
    """量纲类，表示物理量的七个基本量纲"""

    def __init__(self,
                 length: int = 0,  # 长度 (L)
                 mass: int = 0,  # 质量 (M)
                 time: int = 0,  # 时间 (T)
                 current: int = 0,  # 电流 (I)
                 temperature: int = 0,  # 热力学温度 (Θ)
                 amount: int = 0,  # 物质的量 (N)
                 luminous_intensity: int = 0  # 发光强度 (J)
                 ):
        """
        初始化量纲
        :param length: 长度量纲指数
        :param mass: 质量量纲指数
        :param time: 时间量纲指数
        :param current: 电流量纲指数
        :param temperature: 温度量纲指数
        :param amount: 物质量量纲指数
        :param luminous_intensity: 发光强度量纲指数
        """
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
        """提供属性访问支持"""
        if name in self.exponents:
            return self.exponents[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __eq__(self, other):
        """检查两个量纲是否相同"""
        return all(self.exponents[k] == other.exponents[k] for k in self.exponents)

    def __mul__(self, other):
        """量纲乘法（用于标量乘法）"""
        return Dimension(**{
            k: self.exponents[k] + other.exponents[k] for k in self.exponents
        })

    def __truediv__(self, other):
        """量纲除法（用于标量除法）"""
        return Dimension(**{
            k: self.exponents[k] - other.exponents[k] for k in self.exponents
        })

    def __repr__(self):
        """简洁表示量纲，省略零次项"""
        parts = [f"{k}^{v}" for k, v in self.exponents.items() if v != 0]
        return f"Dimension({', '.join(parts)})" if parts else "Dimension()"

    def as_dict(self, compact=False):
        """
        返回量纲的字典表示
        :param compact: 是否压缩表示（省略零指数项）
        """
        if compact:
            return {k: v for k, v in self.exponents.items() if v != 0}
        return self.exponents.copy()

    @classmethod
    def common_quantities(cls):
        """返回常见物理量的量纲"""
        return {
            # 基本量
            'length': Dimension(length=1),
            'mass': Dimension(mass=1),
            'time': Dimension(time=1),
            'current': Dimension(current=1),
            'temperature': Dimension(temperature=1),
            'amount': Dimension(amount=1),
            'luminous_intensity': Dimension(luminous_intensity=1),

            # 导出量
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
        """
        初始化矢量
        :param x: x分量
        :param y: y分量
        :param z: z分量（默认为0）
        :param dimension: 量纲对象
        """
        self.data = np.array([x, y, z], dtype=float)
        self.dimension = dimension

    def __add__(self, other):
        """矢量加法（要求量纲相同）"""
        if self.dimension != other.dimension:
            raise ValueError("矢量量纲不匹配，无法相加")
        return Vector(*(self.data + other.data), dimension=self.dimension)

    def __sub__(self, other):
        """矢量减法（要求量纲相同）"""
        if self.dimension != other.dimension:
            raise ValueError("矢量量纲不匹配，无法相减")
        return Vector(*(self.data - other.data), dimension=self.dimension)

    def __mul__(self, scalar):
        """标量乘法（标量需无量纲）"""
        if not isinstance(scalar, (int, float)):
            raise TypeError("标量必须是数值类型")
        return Vector(*(self.data * scalar), dimension=self.dimension)

    def __rmul__(self, scalar):
        """标量乘法（右侧）"""
        return self.__mul__(scalar)

    def magnitude(self):
        """计算矢量大小（返回无量纲数值）"""
        return np.linalg.norm(self.data)

    def normalized(self):
        """返回归一化后的矢量（无量纲）"""
        mag = self.magnitude()
        if mag > 0:
            return Vector(*(self.data / mag), dimension=Dimension())
        return Vector(0, 0, 0, dimension=Dimension())  # 零矢量

    def dot(self, other):
        """点积（返回无量纲数值）"""
        if self.dimension != other.dimension:
            raise ValueError("矢量量纲不匹配，无法计算点积")
        return np.dot(self.data, other.data)

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
        return Vector(*np.cross(self.data, other.data), dimension=new_dimension)

    def as_tuple(self):
        """转换为元组"""
        return tuple(self.data)

    def __repr__(self):
        return (f"Vector({self.data[0]:.2f}, {self.data[1]:.2f}, {self.data[2]:.2f}) "
                f"with {self.dimension}")


# 位移矢量类（长度量纲）
class Displacement(Vector):
    """位移矢量类，继承Vector类"""

    def __init__(self, x, y, z=0.0):
        super().__init__(x, y, z, dimension=Dimension(length=1))


# 速度矢量类（长度/时间量纲）
class Velocity(Vector):
    """速度矢量类"""

    def __init__(self, x, y, z=0.0):
        super().__init__(x, y, z, dimension=Dimension(length=1, time=-1))


# 力矢量类（质量*长度/时间²量纲）
class Force(Vector):
    """力矢量类"""

    def __init__(self, x, y, z=0.0):
        super().__init__(x, y, z, dimension=Dimension(length=1, mass=1, time=-2))

# 加速度矢量类（长度/时间²量纲）
class Acceleration(Vector):
    """加速度矢量类"""

    def __init__(self, x, y, z=0.0):
        super().__init__(x, y, z, dimension=Dimension(length=1, time=-2))



# 测试用例
if __name__ == "__main__":
    # 创建基本量纲
    length_dim = Dimension(length=1)
    time_dim = Dimension(time=1)

    # 测试乘法运算 - 速度量纲 (L/T)
    velocity_dim = length_dim / time_dim
    print(f"Velocity dimension: {velocity_dim}")

    # 测试电流量纲
    current_dim = Dimension(current=1)
    charge_dim = current_dim * time_dim  # 电荷量纲 (I·T)
    print(f"Electric charge dimension: {charge_dim}")

    # 测试常见物理量库
    common = Dimension.common_quantities()
    print("\nCommon physical quantities:")
    for name, dim in common.items():
        print(f"{name}: {dim}")

    # 测试相等性
    print("\nTesting equality:")
    force_dim1 = Dimension(mass=1, length=1, time=-2)
    force_dim2 = common['force']
    print(f"Force dimensions equal: {force_dim1 == force_dim2}")  # 应该为True

    # 测试量纲字典表示
    print("\nForce dimension as dict:", force_dim1.as_dict(compact=False))

    # 创建位移矢量
    d1 = Displacement(3, 4, 0)
    d2 = Displacement(1, 2, 3)
    print("位移矢量 d1:", d1)
    print("位移矢量 d2:", d2)

    # 矢量加法
    d_sum = d1 + d2
    print("位移和:", d_sum)

    # 创建速度矢量
    v = Velocity(5, 0, 0)
    print("速度矢量 v:", v)

    # 尝试不同量纲的矢量相加（应报错）
    try:
        invalid = d1 + v
    except ValueError as e:
        print("错误捕获:", e)

    # 尝试矢量相除
    try:
        print(type(d1))
        print(type(d1.dot(d1)))
    except TypeError as e:
        print("错误捕获:", e)



