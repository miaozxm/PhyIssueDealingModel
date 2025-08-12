import unittest
import math
import sys
from test1 import Dimension, Vector, Displacement, Velocity, Force, Acceleration
from test1 import PhysicalEntity, PhysicsManager, MasslessEntity


class TestDimension(unittest.TestCase):
    def test_init_and_attributes(self):
        dim = Dimension(length=1, mass=2, time=-3)
        self.assertEqual(dim.length, 1)
        self.assertEqual(dim.mass, 2)
        self.assertEqual(dim.time, -3)
        self.assertEqual(dim.current, 0)

    def test_equality(self):
        dim1 = Dimension(length=1, mass=2)
        dim2 = Dimension(length=1, mass=2)
        dim3 = Dimension(length=1, time=-1)
        self.assertEqual(dim1, dim2)
        self.assertNotEqual(dim1, dim3)

    def test_multiplication(self):
        dim1 = Dimension(length=1, mass=2)
        dim2 = Dimension(time=-1, current=1)
        result = dim1 * dim2
        self.assertEqual(result.length, 1)
        self.assertEqual(result.mass, 2)
        self.assertEqual(result.time, -1)
        self.assertEqual(result.current, 1)

    def test_division(self):
        dim1 = Dimension(length=2, mass=3)
        dim2 = Dimension(length=1, mass=1)
        result = dim1 / dim2
        self.assertEqual(result.length, 1)
        self.assertEqual(result.mass, 2)

    def test_repr(self):
        dim = Dimension(length=2, time=-1, current=0.5)
        self.assertEqual(repr(dim), "Dimension(length^2, time^-1, current^0.5)")
        self.assertEqual(repr(Dimension()), "Dimension()")

    def test_as_dict(self):
        dim = Dimension(length=1, temperature=2)
        self.assertEqual(dim.as_dict(), {
            'length': 1, 'mass': 0, 'time': 0,
            'current': 0, 'temperature': 2,
            'amount': 0, 'luminous_intensity': 0
        })
        self.assertEqual(dim.as_dict(compact=True), {'length': 1, 'temperature': 2})

    def test_common_quantities(self):
        quantities = Dimension.common_quantities()
        self.assertEqual(quantities['velocity'], Dimension(length=1, time=-1))
        self.assertEqual(quantities['force'], Dimension(mass=1, length=1, time=-2))


class TestVector(unittest.TestCase):
    def setUp(self):
        self.dim = Dimension(length=1, time=-1)  # 速度量纲
        self.v1 = Vector(3, 4, dimension=self.dim)
        self.v2 = Vector(1, 2, 3, dimension=self.dim)

    def test_init_and_properties(self):
        self.assertEqual(self.v1.x, 3.0)
        self.assertEqual(self.v1.y, 4.0)
        self.assertEqual(self.v1.z, 0.0)
        self.assertEqual(self.v1.dimension, self.dim)
        self.assertEqual(self.v1.data, (3.0, 4.0, 0.0))

    def test_addition(self):
        v3 = self.v1 + self.v2
        self.assertEqual(v3.x, 4.0)
        self.assertEqual(v3.y, 6.0)
        self.assertEqual(v3.z, 3.0)

        # 量纲不匹配测试
        v_dim = Dimension(length=1)
        with self.assertRaises(ValueError):
            self.v1 + Vector(1, 1, dimension=v_dim)

    def test_subtraction(self):
        v3 = self.v1 - self.v2
        self.assertEqual(v3.x, 2.0)
        self.assertEqual(v3.y, 2.0)
        self.assertEqual(v3.z, -3.0)

    def test_scalar_multiplication(self):
        v3 = self.v1 * 2
        self.assertEqual(v3.x, 6.0)
        self.assertEqual(v3.y, 8.0)
        v4 = 0.5 * self.v2
        self.assertEqual(v4.x, 0.5)
        self.assertEqual(v4.y, 1.0)

    def test_negation(self):
        v3 = -self.v1
        self.assertEqual(v3.x, -3.0)
        self.assertEqual(v3.y, -4.0)

    def test_magnitude(self):
        self.assertAlmostEqual(self.v1.magnitude(), 5.0)
        self.assertAlmostEqual(self.v2.magnitude(), math.sqrt(14))

    def test_normalized(self):
        v_norm = self.v1.normalized()
        self.assertAlmostEqual(v_norm.x, 0.6)
        self.assertAlmostEqual(v_norm.y, 0.8)
        self.assertAlmostEqual(v_norm.z, 0.0)
        self.assertEqual(v_norm.dimension, Dimension())

    def test_dot_product(self):
        v1 = Vector(1, 2, 3)
        v2 = Vector(4, 5, 6)
        self.assertEqual(v1.dot(v2), 32)

    def test_cross_product(self):
        v1 = Vector(1, 0, 0)
        v2 = Vector(0, 1, 0)
        cross = v1.cross(v2)
        self.assertEqual(cross.x, 0)
        self.assertEqual(cross.y, 0)
        self.assertEqual(cross.z, 1)

    def test_as_tuple(self):
        self.assertEqual(self.v1.as_tuple(), (3.0, 4.0, 0.0))

    def test_repr(self):
        self.assertTrue(repr(self.v1).startswith("Vector(3.00, 4.00, 0.00)"))


class TestSpecialVectors(unittest.TestCase):
    def test_displacement(self):
        d = Displacement(1, 2, 3)
        self.assertEqual(d.dimension, Dimension(length=1))

    def test_velocity(self):
        v = Velocity(4, 5)
        self.assertEqual(v.dimension, Dimension(length=1, time=-1))

    def test_acceleration(self):
        a = Acceleration(0, -9.8)
        self.assertEqual(a.dimension, Dimension(length=1, time=-2))

    def test_force(self):
        f = Force(10, 0)
        self.assertEqual(f.dimension, Dimension(length=1, mass=1, time=-2))


class TestPhysicalEntity(unittest.TestCase):
    def setUp(self):
        self.entity = PhysicalEntity(
            entity_id="ball",
            mass=1.0,
            position=Displacement(0, 0, 0),
            velocity=Velocity(2, 0, 0),
            acceleration=Acceleration(0, -9.8, 0)
        )

    def test_initialization(self):
        self.assertEqual(self.entity.id, "ball")
        self.assertEqual(self.entity.mass, 1.0)
        self.assertEqual(self.entity.position.as_tuple(), (0, 0, 0))
        self.assertEqual(self.entity.velocity.as_tuple(), (2, 0, 0))
        self.assertEqual(self.entity.acceleration.as_tuple(), (0, -9.8, 0))

    def test_position_processing(self):
        # 测试不同类型的position输入
        entities = [
            PhysicalEntity("e1", 1, (1, 2, 3)),
            PhysicalEntity("e2", 1, Displacement(4, 5, 6)),
            PhysicalEntity("e3", 1, Vector(7, 8, 9))
        ]
        self.assertEqual(entities[0].position.as_tuple(), (1, 2, 3))
        self.assertEqual(entities[1].position.as_tuple(), (4, 5, 6))
        self.assertEqual(entities[2].position.as_tuple(), (7, 8, 9))

    def test_force_management(self):
        self.assertEqual(len(self.entity.forces), 0)
        self.entity.forces.append(('push', Force(5, 0)))
        self.assertEqual(len(self.entity.forces), 1)

    def test_repr(self):
        self.assertTrue(repr(self.entity).startswith("PhysicalEntity(ball, mass=1.0kg"))


class TestMasslessEntity(unittest.TestCase):
    def test_massless_properties(self):
        ml_entity = MasslessEntity("rope", (0, 0, 0))
        self.assertEqual(ml_entity.mass, 0.0)
        self.assertTrue(repr(ml_entity).startswith("MasslessEntity(rope)"))

    def test_position_handling(self):
        ml_entity = MasslessEntity("wire", Displacement(1, 2, 3))
        self.assertEqual(ml_entity.position.as_tuple(), (1, 2, 3))


class TestPhysicsManager(unittest.TestCase):
    def setUp(self):
        self.manager = PhysicsManager()
        self.entity1 = PhysicalEntity("ball1", 1.0, (0, 0, 0))
        self.entity2 = PhysicalEntity("ball2", 2.0, (5, 0, 0))

    def test_entity_management(self):
        self.manager.add_entity(self.entity1)
        self.manager.add_entity(self.entity2)

        self.assertEqual(len(self.manager.entities), 2)
        self.assertEqual(self.manager.get_entity("ball1"), self.entity1)

        with self.assertRaises(ValueError):
            self.manager.add_entity(PhysicalEntity("ball1", 1.5, (10, 0, 0)))

    def test_gravity_application(self):
        self.manager.add_entity(self.entity1)
        gravity = self.manager.apply_gravity("ball1")

        self.assertAlmostEqual(gravity.x, 0)
        self.assertAlmostEqual(gravity.y, -9.8)
        self.assertEqual(len(self.entity1.forces), 1)

        # 测试质量为零的物体
        massless = MasslessEntity("light", (0, 0, 0))
        self.manager.add_entity(massless)
        gravity = self.manager.apply_gravity("light")
        self.assertEqual(gravity.magnitude(), 0)

    def test_external_force(self):
        self.manager.add_entity(self.entity1)

        # 角度格式
        force1 = self.manager.apply_external_force(
            "ball1", "wind", 5, 30
        )
        self.assertAlmostEqual(force1.x, 5 * math.cos(math.radians(30)))
        self.assertAlmostEqual(force1.y, 5 * math.sin(math.radians(30)))

        # 矢量格式
        force2 = self.manager.apply_external_force(
            "ball1", "thrust", 10, Vector(0, 1, 0)
        )
        self.assertAlmostEqual(force2.x, 0)
        self.assertAlmostEqual(force2.y, 10)
        self.assertAlmostEqual(force2.z, 0)

        # 方向元组
        force3 = self.manager.apply_external_force(
            "ball1", "magnetic", 3, (0, 0, 1)
        )
        self.assertAlmostEqual(force3.z, 3)

    def test_net_force_calculation(self):
        self.manager.add_entity(self.entity1)
        self.manager.add_entity(self.entity2)
        self.manager.apply_gravity("ball1")
        self.manager.apply_external_force("ball1", "push", 5, 0)

        net_force = self.manager.calculate_net_force("ball1")
        self.assertAlmostEqual(net_force.x, 5)
        self.assertAlmostEqual(net_force.y, -9.8)

        # 测试接触面力（将创建虚拟接触面）
        self.manager.connect_entities("contact1", "ball1", "ball2", (1, 0, 0))
        net_force = self.manager.calculate_net_force("ball1")
        self.assertTrue(net_force.x != 5)  # 因为接触面会贡献力

    def test_entity_kinematics_update(self):
        self.manager.add_entity(self.entity1)
        self.manager.apply_gravity("ball1")

        # 初始状态检查
        self.assertEqual(self.entity1.position.as_tuple(), (0, 0, 0))
        self.assertEqual(self.entity1.velocity.as_tuple(), (2, 0, 0))

        # 更新时间
        self.manager.update_entity_kinematics("ball1", 0.1)

        # 验证位置更新
        new_pos = self.entity1.position
        expected_x = 2 * 0.1
        expected_y = 0.5 * (-9.8) * (0.1 ** 2)
        self.assertAlmostEqual(new_pos.x, expected_x)
        self.assertAlmostEqual(new_pos.y, expected_y)

        # 验证速度更新
        new_vel = self.entity1.velocity
        expected_vy = -9.8 * 0.1
        self.assertAlmostEqual(new_vel.x, 2)
        self.assertAlmostEqual(new_vel.y, expected_vy)

    def test_euler_to_vector(self):
        v1 = PhysicsManager._euler_to_vector(0, 0)
        self.assertAlmostEqual(v1.x, 1)
        self.assertAlmostEqual(v1.y, 0)
        self.assertAlmostEqual(v1.z, 0)

        v2 = PhysicsManager._euler_to_vector(90, 0)
        self.assertAlmostEqual(v2.x, 0)
        self.assertAlmostEqual(v2.y, 1)
        self.assertAlmostEqual(v2.z, 0)


class TestContactSurface(unittest.TestCase):
    def setUp(self):
        self.manager = PhysicsManager()
        self.entity1 = PhysicalEntity("block1", 1.0, (0, 0, 0))
        self.entity2 = PhysicalEntity("block2", 1.0, (0, 5, 0))
        self.manager.add_entity(self.entity1)
        self.manager.add_entity(self.entity2)
        self.surface = self.manager.connect_entities(
            "contact1", "block1", "block2",
            normal_direction=(0, 1, 0), friction_coeff=0.2
        )

    def test_contact_initialization(self):
        self.assertEqual(self.surface.id, "contact1")
        self.assertEqual(self.surface.entity1.id, "block1")
        self.assertEqual(self.surface.entity2.id, "block2")
        self.assertEqual(self.surface.normal_direction.as_tuple(), (0, 1, 0))
        self.assertEqual(self.surface.friction_coeff, 0.2)

    def test_friction_calculation(self):
        # 设置弹性力
        self.surface.elastic_force = Force(0, 10, 0)  # 10N向正y方向

        # 当没有相对运动时（静摩擦）
        self.entity1.velocity = Velocity(0, 0, 0)
        self.entity2.velocity = Velocity(0, 0, 0)
        self.surface.update()
        self.surface.calculate_force()

        self.assertEqual(self.surface.friction_force.x, 0)
        self.assertEqual(self.surface.friction_force.y, 0)

        # 当有相对运动时（动摩擦）
        self.entity1.velocity = Velocity(1, 0, 0)
        self.entity2.velocity = Velocity(0, 0, 0)
        self.surface.update()
        self.surface.calculate_force()

        self.assertAlmostEqual(self.surface.friction_force.x, -2)  # 0.2 * 10
        self.assertEqual(self.surface.friction_force.y, 0)


# 运行所有测试
if __name__ == '__main__':
    # 配置测试运行器以使用标准输出
    runner = unittest.TextTestRunner(stream=sys.stdout)
    unittest.main(testRunner=runner, exit=False)
