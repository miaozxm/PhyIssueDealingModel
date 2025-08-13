import math
from dimension import Dimension

class Vector:
    """三维矢量类，支持量纲管理。

    该类实现了带量纲的三维矢量运算，包括：
    - 矢量加减法（要求量纲相同）
    - 矢量与标量乘法（保持原量纲）
    - 矢量归一化（结果无量纲）
    - 点积运算（结果无量纲）
    - 叉积运算（量纲为两个矢量量纲之和）

    属性：
        x (float): x分量
        y (float): y分量
        z (float): z分量
        dimension (Dimension): 矢量的量纲
    """

    def __init__(self, x, y, z=0.0, dimension=Dimension()):
        """初始化三维矢量。

        Args:
            x: x分量值
            y: y分量值
            z: z分量值，默认为0.0
            dimension: 矢量的量纲，默认为无量纲
        """
        # 确保所有分量都是float类型
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.dimension = dimension

    @property
    def data(self):
        """获取矢量分量的元组形式。

        Returns:
            tuple: (x, y, z)分量的元组
        """
        return self.x, self.y, self.z

    def __add__(self, other):
        """矢量加法运算。

        要求两个矢量量纲相同，否则抛出ValueError。

        Args:
            other: 另一个Vector对象

        Returns:
            Vector: 新的矢量，分量为两个矢量分量之和

        Raises:
            ValueError: 当量纲不匹配时
        """
        if self.dimension != other.dimension:
            raise ValueError("矢量量纲不匹配，无法相加")
        return Vector(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
            dimension=self.dimension
        )

    def __sub__(self, other):
        """矢量减法运算。

        要求两个矢量量纲相同，否则抛出ValueError。

        Args:
            other: 另一个Vector对象

        Returns:
            Vector: 新的矢量，分量为两个矢量分量之差

        Raises:
            ValueError: 当量纲不匹配时
        """
        if self.dimension != other.dimension:
            raise ValueError(self.dimension.__str__(),other.dimension.__str__(), "矢量量纲不匹配，无法相减")
        return Vector(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
            dimension=self.dimension
        )

    def __mul__(self, scalar):
        """矢量与标量乘法（右乘）。

        矢量与标量相乘时保持原量纲不变。

        Args:
            scalar: 标量值（int或float）

        Returns:
            Vector: 新的矢量，分量为原分量乘以标量

        Raises:
            TypeError: 当标量不是数值类型时
        """
        if not isinstance(scalar, (int, float)):
            raise TypeError("标量必须是数值类型")
        return Vector(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar,
            dimension=self.dimension
        )

    def __rmul__(self, scalar):
        """矢量与标量乘法（左乘）。

        与__mul__功能相同，支持标量在左侧的乘法。
        """
        return self.__mul__(scalar)

    def __neg__(self):
        """一元负号操作，返回矢量的负值。

        Returns:
            Vector: 新的矢量，分量为原分量的负值，量纲不变
        """
        return Vector(-self.x, -self.y, -self.z, dimension=self.dimension)

    def __eq__(self, other):
        """重载相等运算符，比较矢量的分量和量纲"""
        if not isinstance(other, Vector):
            return False

        # 比较分量（考虑浮点误差）
        tolerance = 1e-5
        components_equal = (abs(self.x - other.x) < tolerance and
                            abs(self.y - other.y) < tolerance and
                            abs(self.z - other.z) < tolerance)

        # 比较量纲
        dimension_equal = self.dimension == other.dimension

        return components_equal and dimension_equal

    def magnitude(self):
        """计算矢量的大小（模）。

        计算公式：sqrt(x² + y² + z²)

        Returns:
            float: 矢量的大小
        """
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalized(self):
        """返回归一化后的矢量（方向相同，大小为1）。

        归一化后的矢量无量纲。

        Returns:
            Vector: 归一化后的矢量
        """
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
        """计算两个矢量的点积（内积）。

        点积结果是一个标量，无量纲。
        计算公式：x1*x2 + y1*y2 + z1*z2

        Args:
            other: 另一个Vector对象

        Returns:
            float: 点积结果

        Raises:
            ValueError: 当量纲不匹配时
        """
        if self.dimension != other.dimension:
            raise ValueError("矢量量纲不匹配，无法计算点积")
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        """计算两个矢量的叉积（外积）。

        叉积结果是一个新矢量，其量纲为两个矢量量纲之和。
        计算公式：
        (y1*z2 - z1*y2, z1*x2 - x1*z2, x1*y2 - y1*x2)

        Args:
            other: 另一个Vector对象

        Returns:
            Vector: 叉积结果矢量
        """
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
        """将矢量转换为元组形式。

        Returns:
            tuple: (x, y, z)分量的元组
        """
        return self.x, self.y, self.z

    def __repr__(self):
        """生成矢量的字符串表示。

        格式示例：Vector(1.00, 2.00, 3.00) with Dimension(length^1, time^-1)

        Returns:
            str: 矢量的字符串表示
        """
        return (f"Vector({self.x:.2f}, {self.y:.2f}, {self.z:.2f}) "
                f"with {self.dimension}")


class Displacement(Vector):
    """位移矢量类，表示物体的位置变化。

    量纲：[长度]^1
    """

    def __init__(self, x, y, z=0.0):
        """初始化位移矢量。

        Args:
            x: x方向位移
            y: y方向位移
            z: z方向位移，默认为0.0
        """
        super().__init__(x, y, z, dimension=Dimension(length=1))


class Velocity(Vector):
    """速度矢量类，表示物体的运动速度。

    量纲：[长度]^1 [时间]^-1
    """

    def __init__(self, x, y, z=0.0):
        """初始化速度矢量。

        Args:
            x: x方向速度分量
            y: y方向速度分量
            z: z方向速度分量，默认为0.0
        """
        super().__init__(x, y, z, dimension=Dimension(length=1, time=-1))


class Force(Vector):
    """力矢量类，表示物体受到的力。

    量纲：[质量]^1 [长度]^1 [时间]^-2
    """

    def __init__(self, x, y, z=0.0):
        """初始化力矢量。

        Args:
            x: x方向力分量
            y: y方向力分量
            z: z方向力分量，默认为0.0
        """
        super().__init__(x, y, z, dimension=Dimension(length=1, mass=1, time=-2))


class Acceleration(Vector):
    """加速度矢量类，表示物体的加速度。

    量纲：[长度]^1 [时间]^-2
    """

    def __init__(self, x, y, z=0.0):
        """初始化加速度矢量。

        Args:
            x: x方向加速度分量
            y: y方向加速度分量
            z: z方向加速度分量，默认为0.0
        """
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



