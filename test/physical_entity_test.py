import unittest
import sys
from vector import Displacement, Velocity, Acceleration, Vector
from physical_entity import PhysicalEntity, MasslessEntity, RigidBody, ElectricallyChargedEntity


class TestPhysicalEntity(unittest.TestCase):
    def test_physical_entity_initialization(self):
        """测试物理实体基类的初始化"""
        # 使用不同格式初始化位置
        pos_tup = (1, 2, 3)
        pos_vec = Vector(4, 5, 6)
        pos_disp = Displacement(7, 8, 9)

        # 测试元组初始化
        ent1 = PhysicalEntity("obj1", 10.0, pos_tup)
        self.assertEqual(ent1.id, "obj1")
        self.assertEqual(ent1.mass, 10.0)
        self.assertEqual(ent1.position.as_tuple(), (1, 2, 3))
        self.assertEqual(ent1.velocity.as_tuple(), (0, 0, 0))
        self.assertEqual(ent1.acceleration.as_tuple(), (0, 0, 0))
        self.assertIsInstance(ent1.position, Displacement)
        self.assertEqual(len(ent1.forces), 0)

        # 测试Vector初始化
        ent2 = PhysicalEntity("obj2", 20.0, pos_vec)
        self.assertEqual(ent2.position.as_tuple(), (4, 5, 6))
        self.assertIsInstance(ent2.position, Displacement)

        # 测试Displacement初始化
        ent3 = PhysicalEntity("obj3", 30.0, pos_disp)
        self.assertEqual(ent3.position.as_tuple(), (7, 8, 9))
        self.assertIsInstance(ent3.position, Displacement)

        # 测试自定义速度和加速度
        vel = Velocity(1, 2, 3)
        acc = Acceleration(4, 5, 6)
        ent4 = PhysicalEntity("obj4", 40.0, (0, 0, 0), vel, acc)
        self.assertEqual(ent4.velocity.as_tuple(), (1, 2, 3))
        self.assertEqual(ent4.acceleration.as_tuple(), (4, 5, 6))
        self.assertIsInstance(ent4.velocity, Velocity)
        self.assertIsInstance(ent4.acceleration, Acceleration)

    def test_process_vector(self):
        """测试向量处理方法的正确性"""
        # 已经是目标矢量类
        disp = Displacement(1, 2, 3)
        result = PhysicalEntity._process_vector(disp, Displacement)
        self.assertIs(result, disp)

        # Vector对象转换
        vec = Vector(4, 5, 6)
        result = PhysicalEntity._process_vector(vec, Velocity)
        self.assertEqual(result.as_tuple(), (4, 5, 6))
        self.assertIsInstance(result, Velocity)

        # 3元组转换
        result = PhysicalEntity._process_vector((7, 8, 9), Acceleration)
        self.assertEqual(result.as_tuple(), (7, 8, 9))
        self.assertIsInstance(result, Acceleration)

        # 2元组转换（z默认为0）
        result = PhysicalEntity._process_vector((10, 11), Displacement)
        self.assertEqual(result.as_tuple(), (10, 11, 0))
        self.assertIsInstance(result, Displacement)

        # 无效类型
        with self.assertRaises(TypeError):
            PhysicalEntity._process_vector("invalid", Displacement)

    def test_representation(self):
        """测试实体的字符串表示"""
        ent = PhysicalEntity("test_obj", 5.0, (1, 2, 3), (4, 5, 6))
        expected_repr = ("PhysicalEntity(test_obj, mass=5.0kg, "
                         "position=(1.0, 2.0, 3.0), "
                         "velocity=(4.0, 5.0, 6.0))")
        self.assertEqual(repr(ent), expected_repr)


class TestMasslessEntity(unittest.TestCase):
    def test_massless_entity(self):
        """测试无质量实体"""
        # 创建无质量实体
        massless = MasslessEntity("light_rope", (1, 2, 3))

        # 验证属性
        self.assertEqual(massless.id, "light_rope")
        self.assertEqual(massless.mass, 0.0)
        self.assertEqual(massless.position.as_tuple(), (1, 2, 3))
        self.assertIsInstance(massless.position, Displacement)

        # 传递质量参数应被忽略
        with_custom_mass = MasslessEntity("ignore_mass", (0, 0, 0), mass=100.0)
        self.assertEqual(with_custom_mass.mass, 0.0)

        # 测试表示
        self.assertEqual(repr(massless), "MasslessEntity(light_rope)")


class TestRigidBody(unittest.TestCase):
    def test_rigid_body(self):
        """测试刚体"""
        # 刚体继承自物理实体
        rb = RigidBody("rigid1", 10.0, (1, 1, 1), (2, 2, 2), (3, 3, 3))

        # 验证属性
        self.assertEqual(rb.id, "rigid1")
        self.assertEqual(rb.mass, 10.0)
        self.assertEqual(rb.position.as_tuple(), (1, 1, 1))
        self.assertEqual(rb.velocity.as_tuple(), (2, 2, 2))
        self.assertEqual(rb.acceleration.as_tuple(), (3, 3, 3))
        self.assertIsInstance(rb.position, Displacement)
        self.assertIsInstance(rb.velocity, Velocity)
        self.assertIsInstance(rb.acceleration, Acceleration)

        # 刚体表示应使用基类表示
        expected_repr = ("PhysicalEntity(rigid1, mass=10.0kg, "
                         "position=(1.0, 1.0, 1.0), "
                         "velocity=(2.0, 2.0, 2.0))")
        self.assertEqual(repr(rb), expected_repr)


class TestElectricallyChargedEntity(unittest.TestCase):
    def test_charged_entity(self):
        """测试带电实体"""
        # 创建带电实体
        charged = ElectricallyChargedEntity("electron", charge=-1.6e-19,
                                            mass=9.1e-31, position=(0, 0, 0))

        # 验证属性
        self.assertEqual(charged.id, "electron")
        self.assertEqual(charged.charge, -1.6e-19)
        self.assertEqual(charged.mass, 9.1e-31)
        self.assertEqual(charged.position.as_tuple(), (0, 0, 0))
        self.assertIsInstance(charged.position, Displacement)

        # 测试表示
        expected_repr = "ElectricallyChargedEntity(electron, charge=-1.6e-19C)"
        self.assertEqual(repr(charged), expected_repr)

        # 测试基类属性仍可用
        charged.velocity = Velocity(0.5, 0, 0)
        self.assertEqual(charged.velocity.as_tuple(), (0.5, 0, 0))


if __name__ == "__main__":
    runner = unittest.TextTestRunner(stream=sys.stdout)
    unittest.main(testRunner=runner, argv=[''], exit=False)
