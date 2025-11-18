"""
Example Level with Magic Shards
This demonstrates how to use magic shards in a level
"""
import pygame
from core.levels.enhanced_level_mask import EnhancedLevelMask
from core.magic import ShardSpawner, MagicType, ShardSize
from core.classes.door_load import Door
from core.classes.key_load import Key
from core.classes.enemy_ai import EnemyAI, EnemyProjectile


class ExampleMagicLevel(EnhancedLevelMask):
    """Example level showcasing magic system integration"""

    def __init__(self, width, height, next_level_class=None):
        super().__init__(width, height, 0.0, (50, 456, 240, 360, 240), False, 'training.jpg')

        self.next_level_class = next_level_class
        self.ticks = 0

        # Add door
        self.door_group = pygame.sprite.Group()
        self.door = Door(self.door_group, self.screen, 1222, 340)
        self.door.simple_image = pygame.transform.flip(self.door.simple_image, True, False)
        self.door.opened = pygame.transform.flip(self.door.opened, True, False)
        self.opened_door = False

        # Add key
        self.key_group = pygame.sprite.Group()
        self.key = Key(self.key_group, self.screen, 500, 600)
        self.is_key = False

        # Add magic shards throughout the level
        self._spawn_magic_shards()

        # Add enemies (optional)
        self.enemies = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()
        self._spawn_enemies()

        # Player health
        self.player_health = 100
        self.player_max_health = 100

        self.execute()

    def _spawn_magic_shards(self):
        """Spawn magic shards in the level"""
        # Fire shards
        fire_small = ShardSpawner.create_fire_shard(200, 500, ShardSize.SMALL)
        self.add_magic_shard(fire_small)

        fire_medium = ShardSpawner.create_fire_shard(300, 450, ShardSize.MEDIUM)
        self.add_magic_shard(fire_medium)

        # Water shards
        water_small = ShardSpawner.create_water_shard(400, 500, ShardSize.SMALL)
        self.add_magic_shard(water_small)

        # Air shard
        air_large = ShardSpawner.create_air_shard(600, 400, ShardSize.LARGE)
        self.add_magic_shard(air_large)

        # Earth shard
        earth_medium = ShardSpawner.create_earth_shard(800, 500, ShardSize.MEDIUM)
        self.add_magic_shard(earth_medium)

        # Electricity shard
        elec_small = ShardSpawner.create_electricity_shard(900, 450, ShardSize.SMALL)
        self.add_magic_shard(elec_small)

        # Life shard
        life_small = ShardSpawner.create_life_shard(1000, 500, ShardSize.SMALL)
        self.add_magic_shard(life_small)

        # Light shard
        light_medium = ShardSpawner.create_light_shard(1100, 450, ShardSize.MEDIUM)
        self.add_magic_shard(light_medium)

        # Darkness shard
        dark_small = ShardSpawner.create_darkness_shard(700, 500, ShardSize.SMALL)
        self.add_magic_shard(dark_small)

    def _spawn_enemies(self):
        """Spawn example enemies"""
        # Guard enemy
        guard = EnemyAI(400, 500, 'guard', self.platforms)
        guard.set_target(self.mage)
        self.enemies.add(guard)

        # Ranged enemy
        ranged = EnemyAI(800, 500, 'ranged', self.platforms)
        ranged.set_target(self.mage)
        self.enemies.add(ranged)

    def execute(self):
        """Main game loop"""
        while self.running:
            delta_time = 1 / self.FPS

            for event in pygame.event.get():
                self.handle_event(event)

            if self.stop:
                return

            # Only update game logic if not paused
            if not self.game_paused and not self.skill_tree_open:
                self.loop()

                # Enhanced update
                self.update_game_logic(delta_time)

                # Check enemies
                self._update_enemies(delta_time)

                # Check for pass condition
                if not self.passed:
                    self.check_pass()

                # Check movement
                self.check_movement()

            # Update UI
            if self.game_paused:
                self.pause_menu.update()
            if self.skill_tree_open:
                self.skill_tree_ui.update()

            # Rendering
            self._render()

            pygame.display.flip()
            self.clock.tick(self.FPS)
            self.render()

        self.terminate()

    def handle_event(self, event):
        """Handle events"""
        # Call enhanced event handling
        super().handle_event(event)

        if self.game_paused or self.skill_tree_open:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.restart()
            if event.key == pygame.K_e and self.passed and not self.opened_door:
                self.door.open()
                self.opened_door = True
                self.door.rect.x -= self.door.image.get_width()
            if event.key == pygame.K_RETURN and self.passed and self.mage.x - 50 <= \
                    self.door.x and self.door.is_opened:
                if self.next_level_class:
                    self.next_level_class(self.width, self.height, 0.0)
                self.stop = True

    def _update_enemies(self, delta_time):
        """Update enemy AI and combat"""
        # Update enemies
        self.enemies.update(delta_time)

        # Update enemy projectiles
        self.enemy_projectiles.update(delta_time)

        # Check enemy projectile collisions with player
        for projectile in self.enemy_projectiles:
            if projectile.check_collision(self.mage.rect):
                self.player_health -= projectile.damage
                projectile.kill()

        # Check spell collisions with enemies
        for spell in self.active_spells:
            for enemy in self.enemies:
                if hasattr(spell, 'check_collision'):
                    if spell.check_collision(enemy.rect):
                        enemy.take_damage(spell.get_damage())
                        if enemy.health <= 0:
                            enemy.kill()
                        spell.kill()
                        break

        # Process enemy attacks
        for enemy in self.enemies:
            if enemy.state == 'attack':
                attack_data = enemy._create_attack()
                if attack_data:
                    self._process_enemy_attack(attack_data)

    def _process_enemy_attack(self, attack_data):
        """Process an enemy attack"""
        if attack_data['type'] == 'projectile':
            projectile = EnemyProjectile(
                attack_data['position'][0],
                attack_data['position'][1],
                attack_data['direction'],
                attack_data['damage']
            )
            self.enemy_projectiles.add(projectile)
        elif attack_data['type'] == 'melee':
            attacker = attack_data['attacker']
            distance = abs(self.mage.rect.centerx - attacker.rect.centerx)
            if distance <= attack_data['range']:
                self.player_health -= attack_data['damage']

    def _render(self):
        """Render the level"""
        # Draw background and base elements
        self.all_sprites.draw(self.screen)
        self.door_group.draw(self.screen)
        self.bottom_border.draw(self.screen)
        self.borders.draw(self.screen)

        # Draw key if not collected
        if not self.is_key:
            self.key_group.draw(self.screen)

        # Draw enemies
        self.enemies.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw_health_bar(self.screen)

        # Draw enemy projectiles
        self.enemy_projectiles.draw(self.screen)

        # Draw player
        if self.visible:
            self.mage_group.draw(self.screen)
        else:
            self.ticks += 1

        if self.ticks >= self.FPS * 3 and not self.visible:
            self.visible = True

        # Draw platforms
        self.platforms.draw(self.screen)

        # Draw enhanced magic elements
        self.draw_enhanced_elements()

        # Draw health bar
        self._draw_health_bar()

    def _draw_health_bar(self):
        """Draw player health bar"""
        bar_width = 200
        bar_height = 20
        bar_x = 10
        bar_y = 50

        # Background
        pygame.draw.rect(self.screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))

        # Health
        health_width = int(bar_width * (self.player_health / self.player_max_health))
        pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))

        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

    def restart(self):
        """Restart the level"""
        ExampleMagicLevel(self.width, self.height, self.next_level_class)
        self.stop = True

    def check_key(self):
        """Check if key is collected"""
        if self.mage.rect.x + 30 >= self.key.rect.x and self.mage.rect.x + 30 <= self.key.rect.x + self.key.w and \
                self.mage.rect.y <= self.key.rect.y:
            self.is_key = True

    def check_pass(self):
        """Check pass condition"""
        if not self.is_key:
            self.check_key()
        if self.is_key:
            self.passed = True
