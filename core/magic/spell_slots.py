"""
Spell Slots System
Manages equipped spells and casting
"""
import json
import os
import pygame
from core.magic.skill_tree import get_skill_tree


class SpellSlots:
    """Manages the player's equipped spell slots"""

    def __init__(self):
        self.slots = {}  # slot_number -> skill_id
        self.cooldowns = {}  # skill_id -> remaining cooldown time
        self.save_file = 'data/spell_slots.json'
        self.max_slots = 3  # Will be updated based on unlocked skills

    def update_max_slots(self):
        """Update max slots based on skill tree"""
        skill_tree = get_skill_tree()
        self.max_slots = skill_tree.get_max_spell_slots()

    def equip_spell(self, slot_number, skill_id):
        """
        Equip a spell to a slot

        Args:
            slot_number: 1-6
            skill_id: The skill to equip (must be learned)
        """
        self.update_max_slots()

        if slot_number < 1 or slot_number > self.max_slots:
            return False

        skill_tree = get_skill_tree()
        if not skill_tree.is_skill_learned(skill_id):
            return False

        self.slots[slot_number] = skill_id
        self.save_to_file()
        return True

    def unequip_spell(self, slot_number):
        """Remove a spell from a slot"""
        if slot_number in self.slots:
            del self.slots[slot_number]
            self.save_to_file()
            return True
        return False

    def get_equipped_spell(self, slot_number):
        """Get the skill equipped in a slot"""
        skill_id = self.slots.get(slot_number)
        if skill_id:
            skill_tree = get_skill_tree()
            return skill_tree.get_skill(skill_id)
        return None

    def can_cast(self, slot_number):
        """Check if a spell in a slot can be cast (not on cooldown)"""
        skill = self.get_equipped_spell(slot_number)
        if not skill:
            return False

        # Check cooldown
        if skill.skill_id in self.cooldowns:
            return self.cooldowns[skill.skill_id] <= 0

        return True

    def cast_spell(self, slot_number):
        """
        Cast a spell from a slot

        Returns:
            Skill object if successful, None otherwise
        """
        if not self.can_cast(slot_number):
            return None

        skill = self.get_equipped_spell(slot_number)
        if skill:
            # Start cooldown
            cooldown = skill.spell_data.get('cooldown', 0)
            self.cooldowns[skill.skill_id] = cooldown
            return skill

        return None

    def update(self, delta_time):
        """Update cooldowns"""
        for skill_id in list(self.cooldowns.keys()):
            self.cooldowns[skill_id] -= delta_time
            if self.cooldowns[skill_id] <= 0:
                self.cooldowns[skill_id] = 0

    def get_cooldown_remaining(self, slot_number):
        """Get remaining cooldown time for a slot"""
        skill = self.get_equipped_spell(slot_number)
        if skill and skill.skill_id in self.cooldowns:
            return max(0, self.cooldowns[skill.skill_id])
        return 0

    def get_cooldown_percentage(self, slot_number):
        """Get cooldown as a percentage (0-1)"""
        skill = self.get_equipped_spell(slot_number)
        if not skill:
            return 0

        max_cooldown = skill.spell_data.get('cooldown', 1)
        remaining = self.get_cooldown_remaining(slot_number)

        if max_cooldown <= 0:
            return 0

        return remaining / max_cooldown

    def get_all_equipped_spells(self):
        """Get all equipped spells as (slot_number, skill) pairs"""
        result = []
        for slot_num in range(1, self.max_slots + 1):
            skill = self.get_equipped_spell(slot_num)
            if skill:
                result.append((slot_num, skill))
        return result

    def save_to_file(self):
        """Save equipped spells to file"""
        try:
            os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
            save_data = {
                'slots': {str(k): v for k, v in self.slots.items()}
            }
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
        except Exception as e:
            print(f"Error saving spell slots: {e}")

    def load_from_file(self):
        """Load equipped spells from file"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    save_data = json.load(f)
                    loaded_slots = save_data.get('slots', {})
                    # Convert string keys back to int
                    self.slots = {int(k): v for k, v in loaded_slots.items()}
        except Exception as e:
            print(f"Error loading spell slots: {e}")

    def reset(self):
        """Clear all equipped spells"""
        self.slots.clear()
        self.cooldowns.clear()


# Global instance
_spell_slots = None


def get_spell_slots():
    """Get the global spell slots instance"""
    global _spell_slots
    if _spell_slots is None:
        _spell_slots = SpellSlots()
        _spell_slots.load_from_file()
        _spell_slots.update_max_slots()
    return _spell_slots


class SpellSlotsUI:
    """UI for displaying spell slots during gameplay"""

    def __init__(self, x, y, font_path):
        self.x = x
        self.y = y
        self.slot_width = 60
        self.slot_height = 60
        self.slot_spacing = 10
        self.font = pygame.font.Font(font_path, 20)
        self.small_font = pygame.font.Font(font_path, 14)

    def draw(self, screen, spell_slots):
        """Draw the spell slots UI"""
        spell_slots.update_max_slots()

        for slot_num in range(1, spell_slots.max_slots + 1):
            # Calculate position
            slot_x = self.x + (slot_num - 1) * (self.slot_width + self.slot_spacing)
            slot_y = self.y

            # Draw slot background
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_width, self.slot_height)

            # Different color based on state
            skill = spell_slots.get_equipped_spell(slot_num)
            if skill:
                # Has a spell equipped
                if spell_slots.can_cast(slot_num):
                    # Ready to cast - bright
                    color = (50, 50, 200)
                else:
                    # On cooldown - dark
                    color = (30, 30, 60)
            else:
                # Empty slot
                color = (40, 40, 40)

            pygame.draw.rect(screen, color, slot_rect)
            pygame.draw.rect(screen, (200, 200, 200), slot_rect, 2)

            # Draw cooldown overlay
            if skill and not spell_slots.can_cast(slot_num):
                cooldown_pct = spell_slots.get_cooldown_percentage(slot_num)
                overlay_height = int(self.slot_height * cooldown_pct)
                if overlay_height > 0:
                    overlay_rect = pygame.Rect(slot_x, slot_y, self.slot_width, overlay_height)
                    overlay = pygame.Surface((self.slot_width, overlay_height))
                    overlay.set_alpha(128)
                    overlay.fill((0, 0, 0))
                    screen.blit(overlay, overlay_rect)

            # Draw slot number
            key_text = self.font.render(str(slot_num), True, (255, 255, 255))
            key_rect = key_text.get_rect(topleft=(slot_x + 5, slot_y + 5))
            screen.blit(key_text, key_rect)

            # Draw spell name (abbreviated)
            if skill:
                # Get first letter or two of spell name
                spell_initial = skill.name[:2].upper()
                spell_text = self.small_font.render(spell_initial, True, (255, 255, 255))
                spell_rect = spell_text.get_rect(center=(slot_x + self.slot_width // 2,
                                                           slot_y + self.slot_height - 12))
                screen.blit(spell_text, spell_rect)

                # Draw cooldown time if on cooldown
                if not spell_slots.can_cast(slot_num):
                    cd_time = spell_slots.get_cooldown_remaining(slot_num)
                    cd_text = self.small_font.render(f"{cd_time:.1f}", True, (255, 100, 100))
                    cd_rect = cd_text.get_rect(center=(slot_x + self.slot_width // 2,
                                                         slot_y + self.slot_height // 2))
                    screen.blit(cd_text, cd_rect)
