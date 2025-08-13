import math
import pygame
import sys
from manager import MechanicsManager
from physical_entity import RigidBody, MasslessEntity
from vector import Vector, Force, Displacement, Velocity, Acceleration


class PhysicsSimulation:
    """重构后的物理模拟演示类，采用更美观的架构设计"""

    def __init__(self):
        # 初始化Pygame
        pygame.init()
        self.width, self.height = 1200, 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("物理教学演示系统")

        # 创建物理管理器
        self.manager = MechanicsManager()
        self.time_step = 0.05

        # 主题颜色配置
        self.theme = {
            "background": (245, 245, 250),
            "ground": (120, 170, 120),
            "panel": (60, 70, 90, 200),
            "text": (40, 40, 60),
            "highlight": (80, 120, 200),
            "entities": {
                "ball": (100, 160, 220),
                "box": (220, 140, 120),
                "ramp": (180, 140, 100),
                "rope": (200, 200, 200)
            },
            "vectors": {
                "velocity": (50, 150, 220),
                "acceleration": (220, 80, 80),
                "force": (80, 180, 100)
            }
        }

        # 字体系统
        self.fonts = {
            "title": pygame.font.SysFont("Arial", 32, bold=True),
            "subtitle": pygame.font.SysFont("Arial", 24),
            "regular": pygame.font.SysFont("Arial", 18),
            "small": pygame.font.SysFont("Arial", 14)
        }

        # 场景管理
        self.scenes = {}
        self.current_scene = "freefall"
        self.create_scenes()

        # 控制状态
        self.paused = False
        self.show_data = True
        self.show_vectors = True
        self.show_grid = True

        # UI元素位置
        self.ui_positions = {
            "panel": pygame.Rect(20, 20, 300, 200),
            "scene_buttons": [
                pygame.Rect(40, 60, 120, 40),
                pygame.Rect(40, 110, 120, 40),
                pygame.Rect(40, 160, 120, 40)
            ],
            "toggle_buttons": [
                pygame.Rect(180, 60, 120, 30),
                pygame.Rect(180, 100, 120, 30),
                pygame.Rect(180, 140, 120, 30)
            ]
        }

    def create_scenes(self):
        """创建多个物理教学场景"""
        # 自由落体场景
        self.scenes["freefall"] = {
            "name": "自由落体",
            "description": "演示物体在重力作用下的自由落体运动",
            "entities": [
                RigidBody("freefall_ball", 5.0, position=(600, 100), velocity=(0, 0))
            ],
            "setup": self.setup_freefall
        }

        # 斜面上的滑块
        self.scenes["inclined_plane"] = {
            "name": "斜面滑块",
            "description": "演示斜面上物体的运动及力的分解",
            "entities": [
                RigidBody("inclined_ramp", 0, position=(0, 600), velocity=(0, 0)),
                RigidBody("inclined_box", 3.0, position=(400, 400)),
                MasslessEntity("inclined_rope", position=(450, 450))
            ],
            "setup": self.setup_inclined_plane
        }

        # 碰撞场景
        self.scenes["collision"] = {
            "name": "弹性碰撞",
            "description": "演示两个物体间的弹性碰撞及动量守恒",
            "entities": [
                RigidBody("collision_ball1", 2.0, position=(300, 400), velocity=(50, 0)),
                RigidBody("collision_ball2", 3.0, position=(700, 400), velocity=(-30, 0))
            ],
            "setup": self.setup_collision
        }

        # 初始化当前场景
        self.setup_current_scene()

    def setup_current_scene(self):
        """设置当前场景的物理环境"""
        # 清空管理器
        self.manager.entities.clear()
        self.manager.contact_surfaces.clear()

        # 添加场景实体
        for entity in self.scenes[self.current_scene]["entities"]:
            try:
                self.manager.add_entity(entity)
            except ValueError as e:
                print(f"添加实体错误: {e}")

        # 调用场景特定的设置方法
        self.scenes[self.current_scene]["setup"]()

    def setup_freefall(self):
        """设置自由落体场景的物理力"""
        self.manager.apply_gravity("freefall_ball", g=9.8)

    def setup_inclined_plane(self):
        """设置斜面场景的物理力"""
        # 施加重力
        self.manager.apply_gravity("inclined_box")

        # 施加斜面支撑力
        normal_force = Force(-100, 50)
        self.manager.apply_force("inclined_box", "斜面支撑", normal_force)

        # 施加摩擦力
        friction_force = Force(-20, 0)
        self.manager.apply_force("inclined_box", "摩擦力", friction_force)

    def setup_collision(self):
        """设置碰撞场景的物理力"""
        # 施加重力
        self.manager.apply_gravity("collision_ball1")
        self.manager.apply_gravity("collision_ball2")

        # 施加空气阻力
        self.manager.apply_external_force("collision_ball1", "空气阻力", -1, (1, 0))
        self.manager.apply_external_force("collision_ball2", "空气阻力", -1, (1, 0))

    def draw_background(self):
        """绘制背景和网格"""
        # 绘制背景
        self.screen.fill(self.theme["background"])

        # 绘制网格
        if self.show_grid:
            grid_color = (230, 230, 235)
            for x in range(0, self.width, 50):
                pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.height), 1)
            for y in range(0, self.height, 50):
                pygame.draw.line(self.screen, grid_color, (0, y), (self.width, y), 1)

    def draw_ground(self):
        """绘制地面"""
        pygame.draw.rect(self.screen, self.theme["ground"],
                         (0, self.height - 50, self.width, 50))

        # 添加地面纹理
        for x in range(0, self.width, 40):
            pygame.draw.line(self.screen, (100, 150, 100),
                             (x, self.height - 50), (x + 20, self.height - 30), 2)

    def draw_ramp(self, height=300):
        """绘制斜面"""
        start_pos = (200, self.height - 50)
        end_pos = (self.width - 200, self.height - height - 50)

        # 绘制斜面主体
        pygame.draw.line(self.screen, self.theme["entities"]["ramp"],
                         start_pos, end_pos, 25)

        # 添加斜面纹理
        for i in range(0, int(self.width - 400), 30):
            pos_x = 200 + i
            pos_y = self.height - 50 - (i / (self.width - 400)) * height
            pygame.draw.line(self.screen, (150, 110, 90),
                             (pos_x, pos_y), (pos_x + 15, pos_y - 15), 2)

    def draw_entity(self, entity):
        """绘制物理实体"""
        # 确定实体类型和颜色
        if "ball" in entity.id:
            entity_type = "ball"
            color = self.theme["entities"]["ball"]
        elif "box" in entity.id:
            entity_type = "box"
            color = self.theme["entities"]["box"]
        elif "rope" in entity.id:
            entity_type = "rope"
            color = self.theme["entities"]["rope"]
        else:
            entity_type = "object"
            color = (180, 180, 180)

        # 转换物理坐标到屏幕坐标
        screen_x = entity.position.x
        screen_y = self.height - 50 - entity.position.y

        # 根据实体类型绘制
        if entity_type == "ball":
            radius = 20
            # 绘制球体
            pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), radius)
            # 添加高光效果
            pygame.draw.circle(self.screen, (255, 255, 255, 100),
                               (int(screen_x - radius / 3), int(screen_y - radius / 3)), radius / 3)

        elif entity_type == "box":
            size = 40
            # 绘制立方体
            pygame.draw.rect(self.screen, color,
                             (screen_x - size / 2, screen_y - size / 2, size, size))
            # 添加阴影效果
            pygame.draw.polygon(self.screen, (0, 0, 0, 50), [
                (screen_x + size / 2, screen_y + size / 2),
                (screen_x + size / 2 + 5, screen_y + size / 2 + 5),
                (screen_x - size / 2 + 5, screen_y + size / 2 + 5),
                (screen_x - size / 2, screen_y + size / 2)
            ])

        elif entity_type == "rope":
            # 绘制绳索（简化表示）
            pygame.draw.line(self.screen, color,
                             (screen_x - 10, screen_y), (screen_x + 10, screen_y), 3)

        # 绘制物理数据
        if self.show_data:
            self.draw_entity_data(entity, screen_x, screen_y)

        # 绘制矢量
        if self.show_vectors:
            self.draw_entity_vectors(entity, screen_x, screen_y)

    def draw_entity_data(self, entity, x, y):
        """绘制实体的物理数据"""
        # 创建数据面板
        panel_rect = pygame.Rect(x - 80, y - 120, 160, 100)
        pygame.draw.rect(self.screen, (255, 255, 255, 180), panel_rect, border_radius=5)
        pygame.draw.rect(self.screen, self.theme["highlight"], panel_rect, 2, border_radius=5)

        # 实体ID
        id_text = self.fonts["small"].render(f"ID: {entity.id}", True, self.theme["text"])
        self.screen.blit(id_text, (x - 75, y - 115))

        # 质量
        mass_text = self.fonts["small"].render(f"质量: {entity.mass:.1f} kg", True, self.theme["text"])
        self.screen.blit(mass_text, (x - 75, y - 95))

        # 位置
        pos_text = self.fonts["small"].render(f"位置: ({entity.position.x:.1f}, {entity.position.y:.1f})",
                                              True, self.theme["text"])
        self.screen.blit(pos_text, (x - 75, y - 75))

        # 速度
        vel_text = self.fonts["small"].render(f"速度: ({entity.velocity.x:.1f}, {entity.velocity.y:.1f})",
                                              True, self.theme["text"])
        self.screen.blit(vel_text, (x - 75, y - 55))

    def draw_entity_vectors(self, entity, x, y):
        """绘制实体的物理矢量"""
        # 绘制速度矢量
        self.draw_vector(x, y, entity.velocity,
                         self.theme["vectors"]["velocity"], "速度")

        # 绘制加速度矢量
        self.draw_vector(x, y, entity.acceleration,
                         self.theme["vectors"]["acceleration"], "加速度")

        # 绘制所有力
        for name, force in entity.forces:
            self.draw_vector(x, y, force,
                             self.theme["vectors"]["force"], name)

    def draw_vector(self, x, y, vector, color, label):
        """绘制带标签的物理矢量箭头"""
        if vector.magnitude() < 0.1:
            return

        # 缩放矢量便于可视化
        scale = 0.2
        end_x = x + vector.x * scale
        end_y = y - vector.y * scale

        # 绘制矢量线
        pygame.draw.line(self.screen, color, (x, y), (end_x, end_y), 3)

        # 绘制箭头
        angle = math.atan2(y - end_y, end_x - x)
        arrow_size = 12
        arrow_points = [
            (end_x, end_y),
            (end_x - arrow_size * math.cos(angle - math.pi / 6),
             end_y + arrow_size * math.sin(angle - math.pi / 6)),
            (end_x - arrow_size * math.cos(angle + math.pi / 6),
             end_y + arrow_size * math.sin(angle + math.pi / 6))
        ]
        pygame.draw.polygon(self.screen, color, arrow_points)

        # 绘制标签
        if label:
            label_surface = self.fonts["small"].render(label, True, color)
            self.screen.blit(label_surface, (end_x + 5, end_y))

    def draw_ui_panel(self):
        """绘制UI控制面板"""
        # 绘制面板背景
        pygame.draw.rect(self.screen, self.theme["panel"],
                         self.ui_positions["panel"], border_radius=10)
        pygame.draw.rect(self.screen, self.theme["highlight"],
                         self.ui_positions["panel"], 2, border_radius=10)

        # 标题
        title = self.fonts["subtitle"].render("控制面板", True, (255, 255, 255))
        self.screen.blit(title, (self.ui_positions["panel"].x + 20, self.ui_positions["panel"].y + 10))

        # 场景按钮
        scenes = [
            ("自由落体", "freefall"),
            ("斜面滑块", "inclined_plane"),
            ("弹性碰撞", "collision")
        ]

        for i, (name, key) in enumerate(scenes):
            btn_rect = self.ui_positions["scene_buttons"][i]
            # 绘制按钮
            btn_color = self.theme["highlight"] if self.current_scene == key else (100, 110, 130)
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=5)
            pygame.draw.rect(self.screen, (255, 255, 255), btn_rect, 2, border_radius=5)

            # 按钮文字
            btn_text = self.fonts["regular"].render(name, True, (255, 255, 255))
            self.screen.blit(btn_text, (btn_rect.x + (btn_rect.width - btn_text.get_width()) // 2,
                                        btn_rect.y + (btn_rect.height - btn_text.get_height()) // 2))

        # 切换按钮
        toggles = [
            ("数据显示", self.show_data),
            ("矢量显示", self.show_vectors),
            ("网格显示", self.show_grid)
        ]

        for i, (name, state) in enumerate(toggles):
            btn_rect = self.ui_positions["toggle_buttons"][i]
            # 绘制按钮
            btn_color = self.theme["highlight"] if state else (100, 110, 130)
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=5)
            pygame.draw.rect(self.screen, (255, 255, 255), btn_rect, 2, border_radius=5)

            # 按钮文字
            btn_text = self.fonts["small"].render(f"{name}: {'开' if state else '关'}", True, (255, 255, 255))
            self.screen.blit(btn_text, (btn_rect.x + (btn_rect.width - btn_text.get_width()) // 2,
                                        btn_rect.y + (btn_rect.height - btn_text.get_height()) // 2))

        # 暂停状态
        pause_text = self.fonts["regular"].render(f"状态: {'暂停' if self.paused else '运行'}", True, (255, 255, 255))
        self.screen.blit(pause_text, (self.ui_positions["panel"].x + 20, self.ui_positions["panel"].y + 180))

    def draw_scene_title(self):
        """绘制场景标题和描述"""
        scene_info = self.scenes[self.current_scene]

        # 标题
        title = self.fonts["title"].render(scene_info["name"], True, self.theme["text"])
        self.screen.blit(title, (self.width - title.get_width() - 30, 30))

        # 描述
        desc = self.fonts["regular"].render(scene_info["description"], True, self.theme["text"])
        self.screen.blit(desc, (self.width - desc.get_width() - 30, 70))

    def draw_current_scene(self):
        """绘制当前场景"""
        self.draw_background()
        self.draw_ground()

        if self.current_scene == "freefall":
            for entity in self.scenes["freefall"]["entities"]:
                self.draw_entity(entity)

        elif self.current_scene == "inclined_plane":
            self.draw_ramp()
            for entity in self.scenes["inclined_plane"]["entities"]:
                self.draw_entity(entity)

        elif self.current_scene == "collision":
            for entity in self.scenes["collision"]["entities"]:
                self.draw_entity(entity)

        self.draw_ui_panel()
        self.draw_scene_title()

    def handle_mouse_events(self):
        """处理鼠标事件"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        # 检查场景按钮点击
        for i, rect in enumerate(self.ui_positions["scene_buttons"]):
            if rect.collidepoint(mouse_pos) and mouse_pressed[0]:
                scene_keys = ["freefall", "inclined_plane", "collision"]
                self.current_scene = scene_keys[i]
                self.setup_current_scene()
                pygame.time.delay(200)  # 防止多次点击

        # 检查切换按钮点击
        for i, rect in enumerate(self.ui_positions["toggle_buttons"]):
            if rect.collidepoint(mouse_pos) and mouse_pressed[0]:
                if i == 0:
                    self.show_data = not self.show_data
                elif i == 1:
                    self.show_vectors = not self.show_vectors
                elif i == 2:
                    self.show_grid = not self.show_grid
                pygame.time.delay(200)  # 防止多次点击

    def run(self):
        """运行主模拟循环"""
        clock = pygame.time.Clock()

        while True:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    # 暂停/继续
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused

                    # 场景切换
                    if event.key == pygame.K_1:
                        self.current_scene = "freefall"
                        self.setup_current_scene()
                    if event.key == pygame.K_2:
                        self.current_scene = "inclined_plane"
                        self.setup_current_scene()
                    if event.key == pygame.K_3:
                        self.current_scene = "collision"
                        self.setup_current_scene()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_events()

            # 更新物理状态
            if not self.paused:
                self.manager.update_physics(self.time_step)

            # 绘制场景
            self.draw_current_scene()
            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    simulator = PhysicsSimulation()
    simulator.run()
