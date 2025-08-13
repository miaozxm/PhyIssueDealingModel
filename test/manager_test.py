import unittest
import sys
import math
from vector import Vector, Displacement, Velocity, Acceleration, Force
from physical_entity import PhysicalEntity, RigidBody, MasslessEntity
from manager import BasePhysicsManager, MechanicsManager, ContactSurface


class TestBasePhysicsManager(unittest.TestCase):
    def setUp(self):
        self.manager = BasePhysicsManager()
        self.entity = RigidBody("test_entity", 10.0, (0, 0, 0))

    def test_add_entity(self):
        self.manager.add_entity(self.entity)
        self.assertIn("test_entity", self.manager.entities)

        # 测试重复添加
        with self.assertRaises(ValueError):
            self.manager.add_entity(self.entity)


class TestMechanicsManager(unittest.TestCase):
    def setUp(self):
        self.manager = MechanicsManager()
        self.box1 = RigidBody("box1", 5.0, (0, 0, 0))
        self.box2 = RigidBody("box2", 3.0, (2, 0, 0))
        self.rope = MasslessEntity("rope", (1, 1, 0))

        self.manager.add_entity(self.box1)
        self.manager.add_entity(self.box2)
        self.manager.add_entity(self.rope)

    def test_apply_gravity(self):
        # 测试对有质量物体施加重力
        gravity = self.manager.apply_gravity("box1")
        self.assertAlmostEqual(gravity.y, -5.0 * 9.8)
        self.assertEqual(len(self.box1.forces), 1)

        # 测试对质量为零物体施加重力
        gravity = self.manager.apply_gravity("rope")
        self.assertEqual(gravity.magnitude(), 0)
        self.assertEqual(len(self.rope.forces), 0)

    def test_apply_external_force(self):
        # 测试角度输入
        force = self.manager.apply_external_force("box1", "push", 100, 30)
        self.assertAlmostEqual(force.x, 100 * math.cos(math.radians(30)))
        self.assertAlmostEqual(force.y, 100 * math.sin(math.radians(30)))

        # 测试向量输入
        force = self.manager.apply_external_force("box1", "pull", 50, Vector(1, 1, 0))
        self.assertAlmostEqual(force.x, 50 / math.sqrt(2))
        self.assertAlmostEqual(force.y, 50 / math.sqrt(2))

        # 测试元组输入
        force = self.manager.apply_external_force("box1", "drag", 75, (0, -1, 0))
        self.assertEqual(force.x, 0)
        self.assertEqual(force.y, -75)

    def test_connect_entities(self):
        # 测试连接实体
        contact = self.manager.connect_entities(
            "contact1", "box1", "box2",
            normal_direction=(1, 0, 0),
            friction_coeff=0.2
        )

        self.assertIn("contact1", self.manager.contact_surfaces)
        self.assertEqual(contact.entity1.id, "box1")
        self.assertEqual(contact.entity2.id, "box2")
        self.assertAlmostEqual(contact.normal_direction.x, 1)

    def test_calculate_net_force(self):
        # 施加多个力
        self.manager.apply_gravity("box1")
        self.manager.apply_external_force("box1", "push", 100, 0)

        # 计算合力
        net_force = self.manager.calculate_net_force("box1")
        self.assertAlmostEqual(net_force.x, 100)
        self.assertAlmostEqual(net_force.y, -5.0 * 9.8)

        # 测试质量为零实体的约束
        with self.assertRaises(RuntimeError):
            self.manager.apply_external_force("rope", "pull", 10, (0, 1, 0))
            self.manager.calculate_net_force("rope")

    def test_update_entity_kinematics(self):
        # 施加力
        self.manager.apply_gravity("box1")
        self.manager.apply_external_force("box1", "push", 100, 0)

        # 初始状态检查
        self.assertEqual(self.box1.position.as_tuple(), (0, 0, 0))
        self.assertEqual(self.box1.velocity.as_tuple(), (0, 0, 0))

        # 更新物理状态
        self.manager.update_entity_kinematics("box1", 0.1)

        # 验证位置变化
        self.assertNotEqual(self.box1.position.as_tuple(), (0, 0, 0))
        self.assertNotEqual(self.box1.velocity.as_tuple(), (0, 0, 0))

        # 验证加速度计算
        expected_acc_x = 100 / 5.0
        expected_acc_y = -9.8
        self.assertAlmostEqual(self.box1.acceleration.x, expected_acc_x)
        self.assertAlmostEqual(self.box1.acceleration.y, expected_acc_y)

    def test_update_physics(self):
        # 施加力
        self.manager.apply_gravity("box1")
        self.manager.apply_gravity("box2")

        # 连接实体
        self.manager.connect_entities(
            "contact1", "box1", "box2",
            normal_direction=(1, 0, 0),
            friction_coeff=0.2
        )

        # 初始时间
        initial_time = self.manager.time

        # 更新物理系统
        self.manager.update_physics(0.1)

        # 验证时间更新
        self.assertAlmostEqual(self.manager.time, initial_time + 0.1)

        # 验证位置变化
        self.assertNotEqual(self.box1.position.as_tuple(), (0, 0, 0))
        self.assertNotEqual(self.box2.position.as_tuple(), (2, 0, 0))


class TestContactSurface(unittest.TestCase):
    def setUp(self):
        self.box1 = RigidBody("box1", 5.0, (0, 0, 0))
        self.box2 = RigidBody("box2", 3.0, (2, 0, 0))

        self.contact = ContactSurface(
            "contact1",
            self.box1,
            self.box2,
            normal_direction=Vector(1, 0, 0),
            friction_coeff=0.2
        )

    def test_update(self):
        # 初始状态应为静摩擦
        self.assertEqual(self.contact.friction_type, "static")

        # 设置相对速度
        self.box1.velocity = Velocity(1, 0, 0)
        self.contact.update()

        # 验证变为动摩擦
        self.assertEqual(self.contact.friction_type, "kinetic")

    def test_calculate_force(self):
        # 设置弹力
        self.contact.elastic_force = Force(10, 0, 0)

        # 计算摩擦力 - 静摩擦
        friction = self.contact.calculate_force()

        # 使用浮点数比较代替对象比较
        self.assertAlmostEqual(friction.x, 0.0, places=5)
        self.assertAlmostEqual(friction.y, 0.0, places=5)
        self.assertAlmostEqual(friction.z, 0.0, places=5)

        # 设置相对速度，使其变成动摩擦
        self.box1.velocity = Velocity(1, 0, 0)
        self.contact.update()

        # 重新设置弹力
        self.contact.elastic_force = Force(10, 0, 0)

        # 计算动摩擦力
        friction = self.contact.calculate_force()
        self.assertAlmostEqual(friction.x, -2.0, places=5)  # 0.2 * 10 = 2
        self.assertAlmostEqual(friction.y, 0.0, places=5)
        self.assertAlmostEqual(friction.z, 0.0, places=5)


if __name__ == "__main__":
    # 创建测试运行器，输出到标准输出
    runner = unittest.TextTestRunner(stream=sys.stdout)
    unittest.main(testRunner=runner)
