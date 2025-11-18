"""
NPC Enemy AI System
Enemies with combat behaviors: guns, fists, dodging, hiding
"""
import pygame
import random
import math
from utils.load_image import load_image


class EnemyAI(pygame.sprite.Sprite):
    """Base AI for enemy NPCs"""

    def __init__(self, x, y, enemy_type='guard', platforms=None):
        """
        Initialize enemy AI

        Args:
            x, y: Starting position
            enemy_type: Type of enemy ('guard', 'melee', 'ranged')
            platforms: Sprite group of platforms for pathfinding
        """
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.enemy_type = enemy_type
        self.platforms = platforms or pygame.sprite.Group()

        # Load sprite
        self._load_sprite()

        # Physics
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.3
        self.max_fall_speed = 10
        self.move_speed = 2
        self.run_speed = 4

        # AI State
        self.state = 'idle'  # idle, patrol, chase, attack, dodge, hide
        self.target = None  # Target to attack (usually the player)
        self.last_known_target_pos = None

        # Combat
        self.health = 100
        self.max_health = 100
        self.damage = 10
        self.attack_range = 50
        self.detection_range = 300
        self.attack_cooldown = 0
        self.max_attack_cooldown = 2.0  # seconds

        # Weapons
        self.weapon_type = 'fist'  # 'fist', 'gun'
        if enemy_type == 'ranged':
            self.weapon_type = 'gun'
            self.attack_range = 400

        # Dodging
        self.dodge_chance = 0.3
        self.dodge_cooldown = 0
        self.max_dodge_cooldown = 3.0
        self.is_dodging = False
        self.dodge_direction = 0

        # Hiding/Cover
        self.cover_position = None
        self.is_in_cover = False
        self.cover_search_range = 200

        # Patrol
        self.patrol_points = [(x - 100, y), (x + 100, y)]
        self.current_patrol_index = 0
        self.patrol_wait_time = 0

        # Animation
        self.direction = 1  # 1 = right, -1 = left
        self.animation_timer = 0

    def _load_sprite(self):
        """Load enemy sprite"""
        try:
            # Try to load enemy sprite
            sheet = load_image('enemy_guard_common.png')
            # Simple placeholder: extract first frame
            self.width = 60
            self.height = 80
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((200, 50, 50))  # Red placeholder
            self.rect = self.image.get_rect(topleft=(int(self.x), int(self.y)))
        except:
            # Fallback to simple rectangle
            self.width = 60
            self.height = 80
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((200, 50, 50))
            self.rect = self.image.get_rect(topleft=(int(self.x), int(self.y)))

    def update(self, delta_time=1/120):
        """Update AI behavior"""
        if self.health <= 0:
            self.state = 'dead'
            return

        # Update cooldowns
        self.attack_cooldown = max(0, self.attack_cooldown - delta_time)
        self.dodge_cooldown = max(0, self.dodge_cooldown - delta_time)

        # AI decision making
        self._update_ai_state(delta_time)

        # Execute current state behavior
        if self.state == 'idle':
            self._behavior_idle(delta_time)
        elif self.state == 'patrol':
            self._behavior_patrol(delta_time)
        elif self.state == 'chase':
            self._behavior_chase(delta_time)
        elif self.state == 'attack':
            self._behavior_attack(delta_time)
        elif self.state == 'dodge':
            self._behavior_dodge(delta_time)
        elif self.state == 'hide':
            self._behavior_hide(delta_time)

        # Apply physics
        self._apply_physics()

        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def _update_ai_state(self, delta_time):
        """Update AI state based on conditions"""
        if not self.target:
            # No target, patrol or idle
            if self.state not in ['patrol', 'idle']:
                self.state = 'patrol'
            return

        # Check if target is in range
        distance_to_target = self._distance_to(self.target.rect.centerx, self.target.rect.centery)

        # Detection
        if distance_to_target > self.detection_range:
            # Lost target
            self.target = None
            self.state = 'patrol'
            return

        # Update last known position
        self.last_known_target_pos = (self.target.rect.centerx, self.target.rect.centery)

        # Decide on action
        if distance_to_target <= self.attack_range:
            # In attack range
            if self.attack_cooldown <= 0:
                self.state = 'attack'
            else:
                # Can't attack yet, maybe dodge or hide
                if self.weapon_type == 'gun' and not self.is_in_cover:
                    # Ranged enemies seek cover
                    self.state = 'hide'
                else:
                    self.state = 'chase'
        else:
            # Not in range, chase
            self.state = 'chase'

    def _behavior_idle(self, delta_time):
        """Idle behavior - stand still"""
        self.velocity_x = 0

    def _behavior_patrol(self, delta_time):
        """Patrol behavior - move between patrol points"""
        if self.patrol_wait_time > 0:
            self.patrol_wait_time -= delta_time
            self.velocity_x = 0
            return

        # Move toward current patrol point
        target_x, target_y = self.patrol_points[self.current_patrol_index]
        distance = abs(self.x - target_x)

        if distance < 10:
            # Reached patrol point
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
            self.patrol_wait_time = 1.0  # Wait 1 second
            self.velocity_x = 0
        else:
            # Move toward patrol point
            if self.x < target_x:
                self.velocity_x = self.move_speed
                self.direction = 1
            else:
                self.velocity_x = -self.move_speed
                self.direction = -1

    def _behavior_chase(self, delta_time):
        """Chase behavior - move toward target"""
        if not self.target:
            self.state = 'patrol'
            return

        target_x = self.target.rect.centerx

        # Move toward target
        if self.x < target_x - 20:
            self.velocity_x = self.run_speed
            self.direction = 1
        elif self.x > target_x + 20:
            self.velocity_x = -self.run_speed
            self.direction = -1
        else:
            self.velocity_x = 0

    def _behavior_attack(self, delta_time):
        """Attack behavior"""
        if self.attack_cooldown > 0:
            return

        # Face target
        if self.target:
            if self.target.rect.centerx > self.x:
                self.direction = 1
            else:
                self.direction = -1

        # Perform attack
        self.attack_cooldown = self.max_attack_cooldown
        return self._create_attack()

    def _behavior_dodge(self, delta_time):
        """Dodge behavior - quick movement to evade"""
        if not self.is_dodging:
            # Start dodge
            self.is_dodging = True
            self.dodge_direction = random.choice([-1, 1])
            self.dodge_cooldown = self.max_dodge_cooldown

        # Perform dodge movement
        self.velocity_x = self.dodge_direction * self.run_speed * 1.5

        # Check if dodge is complete
        if self.animation_timer > 0.3:  # Dodge duration
            self.is_dodging = False
            self.state = 'chase'
            self.animation_timer = 0
        else:
            self.animation_timer += delta_time

    def _behavior_hide(self, delta_time):
        """Hide behavior - seek cover"""
        if self.is_in_cover:
            # Already in cover, stay put
            self.velocity_x = 0
            # Occasionally peek and attack
            if self.attack_cooldown <= 0 and random.random() < 0.3:
                self.state = 'attack'
            return

        # Find cover (simplified: move away from target)
        if self.target:
            if self.target.rect.centerx > self.x:
                # Target is to the right, move left
                self.velocity_x = -self.run_speed
                self.direction = -1
            else:
                # Target is to the left, move right
                self.velocity_x = self.run_speed
                self.direction = 1

            # Check if we've moved far enough
            distance = self._distance_to(self.target.rect.centerx, self.target.rect.centery)
            if distance > self.attack_range * 0.8:
                self.is_in_cover = True
                self.velocity_x = 0

    def _apply_physics(self):
        """Apply gravity and physics"""
        # Gravity
        self.velocity_y += self.gravity
        if self.velocity_y > self.max_fall_speed:
            self.velocity_y = self.max_fall_speed

    def _distance_to(self, x, y):
        """Calculate distance to a point"""
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx * dx + dy * dy)

    def _create_attack(self):
        """Create an attack (returns attack data for processing)"""
        if self.weapon_type == 'gun':
            # Ranged attack
            return {
                'type': 'projectile',
                'attacker': self,
                'damage': self.damage,
                'position': (self.rect.centerx, self.rect.centery),
                'direction': self.direction
            }
        else:
            # Melee attack
            return {
                'type': 'melee',
                'attacker': self,
                'damage': self.damage,
                'range': self.attack_range,
                'position': (self.rect.centerx, self.rect.centery)
            }

    def take_damage(self, amount):
        """Take damage"""
        self.health -= amount

        # Chance to dodge next attack
        if self.dodge_cooldown <= 0 and random.random() < self.dodge_chance:
            self.state = 'dodge'
            self.is_dodging = False
            self.animation_timer = 0

        return self.health <= 0  # Returns True if dead

    def set_target(self, target):
        """Set the target to attack"""
        self.target = target

    def draw_health_bar(self, screen):
        """Draw health bar above enemy"""
        if self.health <= 0:
            return

        bar_width = self.width
        bar_height = 5
        bar_x = self.rect.x
        bar_y = self.rect.y - 10

        # Background
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

        # Health
        health_width = int(bar_width * (self.health / self.max_health))
        health_color = (0, 255, 0) if self.health > 50 else (255, 255, 0) if self.health > 25 else (255, 0, 0)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))


class EnemyProjectile(pygame.sprite.Sprite):
    """Projectile fired by enemies"""

    def __init__(self, x, y, direction, damage, speed=8):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.damage = damage
        self.velocity_x = direction * speed
        self.velocity_y = 0

        # Visual
        self.image = pygame.Surface((10, 5))
        self.image.fill((255, 200, 0))
        self.rect = self.image.get_rect(center=(int(x), int(y)))

        # Lifetime
        self.lifetime = 5.0
        self.alive_time = 0

    def update(self, delta_time=1/120):
        """Update projectile"""
        self.alive_time += delta_time
        if self.alive_time >= self.lifetime:
            self.kill()
            return

        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.center = (int(self.x), int(self.y))

    def check_collision(self, target_rect):
        """Check collision with target"""
        return self.rect.colliderect(target_rect)
