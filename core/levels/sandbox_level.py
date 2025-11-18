"""
Sandbox Level - Practice combat with customizable enemy waves
"""
import pygame
from core.levels.level_mask import LevelMask
from core.classes.enemy_ai import EnemyAI, EnemyProjectile
from core.magic.spell_slots import get_spell_slots, SpellSlotsUI
from core.magic.spells import SpellCaster
from core.ui.pause_menu import PauseMenu
from core.ui.skill_tree_ui import SkillTreeUI
from core.menu.main import TheCageOfMage


class SandboxLevel(LevelMask):
    """Sandbox mode for practicing combat"""

    def __init__(self, width, height, wave_config=None):
        """
        Initialize sandbox level

        Args:
            width, height: Screen dimensions
            wave_config: Configuration for enemy waves
                         Format: [(enemy_count, enemy_type), ...]
        """
        super().__init__(width, height, 0.0, (50, 456, 240, 360, 240), False, 'hall.jpg')

        # Wave configuration
        self.wave_config = wave_config or self._default_wave_config()
        self.current_wave = 0
        self.waves_completed = 0

        # Enemy management
        self.enemies = pygame.sprite.Group()
        self.enemy_projectiles = pygame.sprite.Group()

        # Player spell management
        self.spell_slots = get_spell_slots()
        self.spell_slots_ui = SpellSlotsUI(10, height - 80, self.font)
        self.active_spells = pygame.sprite.Group()

        # UI
        self.pause_menu = PauseMenu(
            self.screen, self.font,
            self.resume_game,
            self.open_skill_tree,
            self.return_to_main_menu
        )
        self.skill_tree_ui = SkillTreeUI(
            self.screen, self.font,
            self.close_skill_tree
        )

        # Game state
        self.game_paused = False
        self.skill_tree_open = False
        self.wave_in_progress = False
        self.wave_complete_timer = 0

        # HUD font
        self.hud_font = pygame.font.Font(self.font, 32)
        self.small_hud_font = pygame.font.Font(self.font, 20)

        # Player stats
        self.player_health = 100
        self.player_max_health = 100

        # Start first wave
        self._spawn_wave()

        self.execute()

    def _default_wave_config(self):
        """Default wave configuration"""
        return [
            [(3, 'guard')],  # Wave 1: 3 guards
            [(5, 'guard')],  # Wave 2: 5 guards
            [(2, 'ranged'), (3, 'guard')],  # Wave 3: 2 ranged + 3 guards
            [(4, 'ranged'), (4, 'guard')],  # Wave 4: Mixed
            [(10, 'guard')],  # Wave 5: Horde
        ]

    def _spawn_wave(self):
        """Spawn the current wave of enemies"""
        if self.current_wave >= len(self.wave_config):
            # All waves complete
            self.wave_in_progress = False
            return

        wave = self.wave_config[self.current_wave]
        self.wave_in_progress = True

        # Spawn enemies
        spawn_x_positions = [200, 400, 600, 800, 1000]
        spawn_index = 0

        for enemy_count, enemy_type in wave:
            for i in range(enemy_count):
                x = spawn_x_positions[spawn_index % len(spawn_x_positions)]
                enemy = EnemyAI(x, 500, enemy_type, self.platforms)
                enemy.set_target(self.mage)
                self.enemies.add(enemy)
                spawn_index += 1

    def execute(self):
        """Main game loop"""
        while self.running:
            delta_time = 1 / self.FPS

            # Event handling
            for event in pygame.event.get():
                self.handle_event(event)

            if self.stop:
                return

            # Update game state
            if not self.game_paused and not self.skill_tree_open:
                self.loop()
                self._update_game_logic(delta_time)

            # Update UI
            if self.game_paused:
                self.pause_menu.update()
            if self.skill_tree_open:
                self.skill_tree_ui.update()

            # Rendering
            self._render_game()

            pygame.display.flip()
            self.clock.tick(self.FPS)
            self.render()

        self.terminate()

    def handle_event(self, event):
        """Handle input events"""
        # UI event handling
        if self.skill_tree_open:
            result = self.skill_tree_ui.handle_event(event)
            if result == 'close':
                self.close_skill_tree()
            return

        if self.game_paused:
            result = self.pause_menu.handle_event(event)
            return

        # Base class event handling
        super().handle_event(event)

        if event.type == pygame.KEYDOWN:
            # Pause menu
            if event.key == pygame.K_ESCAPE:
                self.pause_game()
                return

            # Spell casting (keys 1-6)
            if pygame.K_1 <= event.key <= pygame.K_6:
                slot_num = event.key - pygame.K_0
                self._cast_spell(slot_num)

            # Restart wave
            if event.key == pygame.K_r:
                self._restart_wave()

            # Next wave
            if event.key == pygame.K_n and not self.wave_in_progress:
                self._next_wave()

        # Mouse click for spell targeting
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Store mouse position for spell targeting
                self.last_mouse_pos = event.pos

    def _update_game_logic(self, delta_time):
        """Update game logic"""
        # Update spell slots cooldowns
        self.spell_slots.update(delta_time)

        # Update player
        self.check_movement()

        # Update enemies
        self.enemies.update(delta_time)

        # Update enemy projectiles
        self.enemy_projectiles.update(delta_time)

        # Check enemy projectile collisions with player
        for projectile in self.enemy_projectiles:
            if projectile.check_collision(self.mage.rect):
                self.player_health -= projectile.damage
                projectile.kill()

        # Update player spells
        self.active_spells.update(delta_time)

        # Check spell collisions with enemies
        for spell in self.active_spells:
            # Check wall collision
            if hasattr(spell, 'check_wall_collision'):
                if spell.check_wall_collision(self.borders):
                    spell.kill()
                    continue

            # Check enemy collisions
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

        # Check if wave is complete
        if self.wave_in_progress and len(self.enemies) == 0:
            self.wave_in_progress = False
            self.wave_complete_timer = 3.0
            self.waves_completed += 1

        # Wave complete timer
        if self.wave_complete_timer > 0:
            self.wave_complete_timer -= delta_time

        # Check player death
        if self.player_health <= 0:
            self._player_death()

    def _process_enemy_attack(self, attack_data):
        """Process an enemy attack"""
        if attack_data['type'] == 'projectile':
            # Create projectile
            projectile = EnemyProjectile(
                attack_data['position'][0],
                attack_data['position'][1],
                attack_data['direction'],
                attack_data['damage']
            )
            self.enemy_projectiles.add(projectile)

        elif attack_data['type'] == 'melee':
            # Check if player is in range
            attacker = attack_data['attacker']
            distance = abs(self.mage.rect.centerx - attacker.rect.centerx)
            if distance <= attack_data['range']:
                self.player_health -= attack_data['damage']

    def _cast_spell(self, slot_num):
        """Cast a spell from a slot"""
        skill = self.spell_slots.cast_spell(slot_num)
        if not skill:
            return

        # Get mouse position or use default target
        target_pos = getattr(self, 'last_mouse_pos', (self.mage.rect.centerx + 100, self.mage.rect.centery))

        # Cast projectile spell
        projectile = SpellCaster.cast_projectile_spell(
            skill,
            self.mage.rect.centerx,
            self.mage.rect.centery,
            target_pos[0],
            target_pos[1]
        )

        if projectile:
            self.active_spells.add(projectile)

    def _restart_wave(self):
        """Restart the current wave"""
        self.enemies.empty()
        self.enemy_projectiles.empty()
        self.active_spells.empty()
        self.player_health = self.player_max_health
        self._spawn_wave()

    def _next_wave(self):
        """Start the next wave"""
        self.current_wave += 1
        if self.current_wave < len(self.wave_config):
            self._spawn_wave()
        else:
            # All waves completed, loop back to first
            self.current_wave = 0
            self._spawn_wave()

    def _player_death(self):
        """Handle player death"""
        self._restart_wave()

    def _render_game(self):
        """Render the game"""
        # Draw background
        self.all_sprites.draw(self.screen)

        # Draw platforms
        self.platforms.draw(self.screen)

        # Draw enemies
        self.enemies.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw_health_bar(self.screen)

        # Draw enemy projectiles
        self.enemy_projectiles.draw(self.screen)

        # Draw player
        if self.visible:
            self.mage_group.draw(self.screen)

        # Draw player spells
        self.active_spells.draw(self.screen)
        for spell in self.active_spells:
            if hasattr(spell, 'draw_particles'):
                spell.draw_particles(self.screen)

        # Draw borders
        self.bottom_border.draw(self.screen)
        self.borders.draw(self.screen)

        # Draw HUD
        self._draw_hud()

        # Draw UI overlays
        if self.game_paused:
            self.pause_menu.draw()
        elif self.skill_tree_open:
            self.skill_tree_ui.draw()

    def _draw_hud(self):
        """Draw HUD elements"""
        # Player health bar
        health_bar_width = 300
        health_bar_height = 30
        health_bar_x = 10
        health_bar_y = 10

        # Background
        pygame.draw.rect(self.screen, (100, 0, 0),
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))

        # Health
        health_width = int(health_bar_width * (self.player_health / self.player_max_health))
        health_color = (0, 255, 0) if self.player_health > 50 else (255, 255, 0) if self.player_health > 25 else (255, 0, 0)
        pygame.draw.rect(self.screen, health_color,
                        (health_bar_x, health_bar_y, health_width, health_bar_height))

        # Border
        pygame.draw.rect(self.screen, (255, 255, 255),
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)

        # Health text
        health_text = self.small_hud_font.render(f'HP: {int(self.player_health)}/{self.player_max_health}',
                                                  True, (255, 255, 255))
        self.screen.blit(health_text, (health_bar_x + 10, health_bar_y + 5))

        # Wave info
        wave_text = self.hud_font.render(f'Wave: {self.current_wave + 1}/{len(self.wave_config)}',
                                         True, (255, 255, 255))
        self.screen.blit(wave_text, (self.width - 250, 10))

        # Enemy count
        enemy_text = self.small_hud_font.render(f'Enemies: {len(self.enemies)}',
                                                True, (255, 255, 255))
        self.screen.blit(enemy_text, (self.width - 250, 50))

        # Wave complete message
        if self.wave_complete_timer > 0:
            complete_text = self.hud_font.render('WAVE COMPLETE!', True, (0, 255, 0))
            complete_rect = complete_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(complete_text, complete_rect)

            next_text = self.small_hud_font.render('Press N for next wave', True, (255, 255, 255))
            next_rect = next_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
            self.screen.blit(next_text, next_rect)

        # Spell slots UI
        self.spell_slots_ui.draw(self.screen, self.spell_slots)

        # Controls hint
        hint_text = self.small_hud_font.render('1-6: Cast Spell | ESC: Pause | R: Restart Wave',
                                               True, (200, 200, 200))
        self.screen.blit(hint_text, (10, self.height - 30))

    def pause_game(self):
        """Pause the game"""
        self.game_paused = True
        self.pause_menu.show()

    def resume_game(self):
        """Resume the game"""
        self.game_paused = False
        self.pause_menu.hide()

    def open_skill_tree(self):
        """Open skill tree UI"""
        self.skill_tree_open = True
        self.game_paused = False
        self.pause_menu.hide()
        self.skill_tree_ui.show()

    def close_skill_tree(self):
        """Close skill tree UI"""
        self.skill_tree_open = False
        self.skill_tree_ui.hide()
        # Return to pause menu
        self.pause_game()

    def return_to_main_menu(self):
        """Return to main menu"""
        self.stop = True
        self.running = False
        TheCageOfMage(self.width, self.height)
