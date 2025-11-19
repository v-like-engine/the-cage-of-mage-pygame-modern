"""
Enhanced Level Mask with Magic System Integration
This extends LevelMask to add magic shards, spells, pause menu, and skill tree
"""
import pygame
from core.levels.level_mask import LevelMask
from core.magic import get_spell_slots, SpellSlotsUI, SpellCaster
from core.ui import PauseMenu, SkillTreeUI
from core.menu.main import TheCageOfMage


class EnhancedLevelMask(LevelMask):
    """Level base class with integrated magic system"""

    def __init__(self, width, height, mus, mage_prefs, chests, background_file, *camera_frames):
        super().__init__(width, height, mus, mage_prefs, chests, background_file, *camera_frames)

        # Magic shards in this level
        self.magic_shards = pygame.sprite.Group()

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

        # Enhanced game state
        self.game_paused = False
        self.skill_tree_open = False

        # Mouse position for spell targeting
        self.last_mouse_pos = (0, 0)

    def handle_event(self, event):
        """Enhanced event handling with magic system"""
        # UI event handling
        if self.skill_tree_open:
            result = self.skill_tree_ui.handle_event(event)
            if result == 'close':
                self.close_skill_tree()
            return

        if self.game_paused:
            result = self.pause_menu.handle_event(event)
            return

        # Intercept ESC key BEFORE calling super to prevent base class from quitting
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.pause_game()
            return

        # Intercept K_1 for spell casting to avoid conflict with invisibility
        if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
            # Only use for spell if invisibility is already used
            if self.used_invisible:
                self._cast_spell(1)
                return
            # Otherwise let base class handle it for invisibility

        # Base class event handling (won't see ESC anymore)
        super().handle_event(event)

        if event.type == pygame.KEYDOWN:
            # Spell casting (keys 2-6, and 1 if invisibility not used)
            if pygame.K_2 <= event.key <= pygame.K_6:
                slot_num = event.key - pygame.K_0
                self._cast_spell(slot_num)

            # Open skill tree directly with T key
            if event.key == pygame.K_t:
                self.open_skill_tree()

        # Mouse position tracking for spell targeting
        if event.type == pygame.MOUSEMOTION:
            self.last_mouse_pos = event.pos

    def update_game_logic(self, delta_time=1/120):
        """Update magic system and spells"""
        # Update spell slots cooldowns
        self.spell_slots.update(delta_time)

        # Update active spells
        self.active_spells.update(delta_time)

        # Check spell collisions with walls
        for spell in list(self.active_spells):
            if hasattr(spell, 'check_wall_collision'):
                if spell.check_wall_collision(self.borders):
                    spell.kill()

        # Check magic shard collection
        for shard in list(self.magic_shards):
            shard.update()
            if shard.check_collection(self.mage.rect):
                shard.kill()

    def draw_enhanced_elements(self):
        """Draw magic-related elements"""
        # Draw magic shards with glow
        for shard in self.magic_shards:
            shard.draw_glow(self.screen)
        self.magic_shards.draw(self.screen)

        # Draw active spells
        self.active_spells.draw(self.screen)
        for spell in self.active_spells:
            if hasattr(spell, 'draw_particles'):
                spell.draw_particles(self.screen)

        # Draw spell slots UI
        self.spell_slots_ui.draw(self.screen, self.spell_slots)

        # Draw UI overlays
        if self.game_paused:
            self.pause_menu.draw()
        elif self.skill_tree_open:
            self.skill_tree_ui.draw()

    def _cast_spell(self, slot_num):
        """Cast a spell from a slot"""
        if self.game_paused or self.skill_tree_open:
            return

        skill = self.spell_slots.cast_spell(slot_num)
        if not skill:
            return

        # Use current mouse position or last known position as target
        target_pos = pygame.mouse.get_pos()
        if target_pos == (0, 0) and self.last_mouse_pos != (0, 0):
            target_pos = self.last_mouse_pos
        elif target_pos == (0, 0):
            # Default to right of player if no mouse position
            target_pos = (self.mage.rect.centerx + 100, self.mage.rect.centery)

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
        # Return to pause menu if it was open
        if hasattr(self, 'pause_menu'):
            self.pause_game()

    def return_to_main_menu(self):
        """Return to main menu"""
        self.stop = True
        self.running = False
        TheCageOfMage(self.width, self.height)

    def add_magic_shard(self, shard):
        """Add a magic shard to the level"""
        self.magic_shards.add(shard)
