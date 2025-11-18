"""
Magic Skill Tree System
Manages learnable skills with dependencies and costs
"""
import json
import os
from core.magic.magic_system import MagicType, get_magic_manager


class SkillNode:
    """Represents a single skill in the skill tree"""

    def __init__(self, skill_id, name, description, magic_type, cost,
                 prerequisites=None, spell_data=None, is_passive=False):
        """
        Initialize a skill node

        Args:
            skill_id: Unique identifier
            name: Display name
            description: Skill description
            magic_type: Type of magic required
            cost: Power points cost to learn
            prerequisites: List of skill_ids that must be learned first
            spell_data: Dictionary with spell parameters
            is_passive: Whether this is a passive upgrade
        """
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.magic_type = magic_type
        self.cost = cost
        self.prerequisites = prerequisites or []
        self.spell_data = spell_data or {}
        self.is_passive = is_passive
        self.learned = False

    def can_learn(self, learned_skills, magic_manager):
        """Check if this skill can be learned"""
        # Check if already learned
        if self.learned:
            return False

        # Check prerequisites
        for prereq_id in self.prerequisites:
            if prereq_id not in learned_skills:
                return False

        # Check if player has enough magic power
        if not magic_manager.has_enough_power(self.magic_type, self.cost):
            return False

        return True

    def learn(self, magic_manager):
        """Learn this skill (spend power points)"""
        if magic_manager.spend_power(self.magic_type, self.cost):
            self.learned = True
            return True
        return False

    def to_dict(self):
        """Convert to dictionary for saving"""
        return {
            'skill_id': self.skill_id,
            'learned': self.learned
        }


class SkillTree:
    """Manages the entire skill tree"""

    def __init__(self):
        self.skills = {}
        self.learned_skills = set()
        self.save_file = 'data/skill_tree.json'
        self._initialize_default_skills()

    def _initialize_default_skills(self):
        """Initialize the default skill tree structure"""

        # FIRE TREE
        self.add_skill(SkillNode(
            'fire_spark', 'Spark',
            'Basic fire attack. Shoots a small fireball.',
            MagicType.FIRE, 0,  # Free starter skill
            spell_data={'damage': 10, 'speed': 5, 'cooldown': 1.0}
        ))

        self.add_skill(SkillNode(
            'fire_fireball', 'Fireball',
            'Powerful fire projectile with area damage.',
            MagicType.FIRE, 5,
            prerequisites=['fire_spark'],
            spell_data={'damage': 25, 'speed': 6, 'cooldown': 2.0, 'aoe_radius': 30}
        ))

        self.add_skill(SkillNode(
            'fire_meteor', 'Meteor',
            'Summon a devastating meteor from the sky.',
            MagicType.FIRE, 15,
            prerequisites=['fire_fireball'],
            spell_data={'damage': 50, 'speed': 3, 'cooldown': 5.0, 'aoe_radius': 60}
        ))

        self.add_skill(SkillNode(
            'fire_inferno', 'Inferno',
            'Create a massive explosion around you.',
            MagicType.FIRE, 25,
            prerequisites=['fire_meteor'],
            spell_data={'damage': 80, 'cooldown': 10.0, 'aoe_radius': 120}
        ))

        # WATER TREE
        self.add_skill(SkillNode(
            'water_splash', 'Water Splash',
            'Basic water attack. Slows enemies.',
            MagicType.WATER, 0,
            spell_data={'damage': 8, 'speed': 4, 'cooldown': 1.0, 'slow_effect': 0.5}
        ))

        self.add_skill(SkillNode(
            'water_stream', 'Water Stream',
            'Continuous water beam that pushes enemies.',
            MagicType.WATER, 5,
            prerequisites=['water_splash'],
            spell_data={'damage': 15, 'range': 200, 'cooldown': 3.0, 'knockback': 5}
        ))

        self.add_skill(SkillNode(
            'water_tsunami', 'Tsunami',
            'Massive wave that sweeps across the battlefield.',
            MagicType.WATER, 20,
            prerequisites=['water_stream'],
            spell_data={'damage': 40, 'width': 300, 'cooldown': 8.0, 'knockback': 10}
        ))

        # AIR TREE
        self.add_skill(SkillNode(
            'air_gust', 'Gust',
            'Quick wind blast. High speed, low damage.',
            MagicType.AIR, 0,
            spell_data={'damage': 5, 'speed': 10, 'cooldown': 0.5}
        ))

        self.add_skill(SkillNode(
            'air_tornado', 'Tornado',
            'Create a tornado that pulls in enemies.',
            MagicType.AIR, 10,
            prerequisites=['air_gust'],
            spell_data={'damage': 30, 'duration': 5.0, 'cooldown': 6.0, 'pull_strength': 3}
        ))

        self.add_skill(SkillNode(
            'air_dash', 'Air Dash',
            'Quick dash movement ability.',
            MagicType.AIR, 5,
            prerequisites=['air_gust'],
            spell_data={'distance': 150, 'cooldown': 2.0},
            is_passive=False
        ))

        # EARTH TREE
        self.add_skill(SkillNode(
            'earth_rock', 'Rock Throw',
            'Throw a heavy rock. High damage, low speed.',
            MagicType.EARTH, 0,
            spell_data={'damage': 20, 'speed': 2, 'cooldown': 2.0}
        ))

        self.add_skill(SkillNode(
            'earth_wall', 'Earth Wall',
            'Create a protective wall of stone.',
            MagicType.EARTH, 8,
            prerequisites=['earth_rock'],
            spell_data={'health': 100, 'duration': 10.0, 'cooldown': 8.0}
        ))

        self.add_skill(SkillNode(
            'earth_earthquake', 'Earthquake',
            'Shake the ground, damaging all grounded enemies.',
            MagicType.EARTH, 18,
            prerequisites=['earth_wall'],
            spell_data={'damage': 45, 'radius': 250, 'cooldown': 12.0, 'stun_duration': 2.0}
        ))

        # ELECTRICITY TREE
        self.add_skill(SkillNode(
            'elec_shock', 'Shock',
            'Quick electric jolt. Can chain to nearby enemies.',
            MagicType.ELECTRICITY, 0,
            spell_data={'damage': 12, 'chain_range': 50, 'max_chains': 1, 'cooldown': 1.5}
        ))

        self.add_skill(SkillNode(
            'elec_lightning', 'Lightning Bolt',
            'Instant lightning strike from above.',
            MagicType.ELECTRICITY, 10,
            prerequisites=['elec_shock'],
            spell_data={'damage': 35, 'cooldown': 3.0, 'stun_duration': 1.0}
        ))

        self.add_skill(SkillNode(
            'elec_storm', 'Lightning Storm',
            'Multiple lightning strikes in an area.',
            MagicType.ELECTRICITY, 20,
            prerequisites=['elec_lightning'],
            spell_data={'damage': 25, 'strikes': 8, 'radius': 150, 'cooldown': 10.0}
        ))

        # LIFE TREE
        self.add_skill(SkillNode(
            'life_heal', 'Minor Heal',
            'Restore a small amount of health.',
            MagicType.LIFE, 0,
            spell_data={'heal_amount': 20, 'cooldown': 5.0}
        ))

        self.add_skill(SkillNode(
            'life_regen', 'Regeneration',
            'Passive health regeneration over time.',
            MagicType.LIFE, 10,
            prerequisites=['life_heal'],
            spell_data={'regen_rate': 1, 'duration': 10.0, 'cooldown': 15.0},
            is_passive=True
        ))

        self.add_skill(SkillNode(
            'life_sanctuary', 'Sanctuary',
            'Create a healing zone.',
            MagicType.LIFE, 20,
            prerequisites=['life_regen'],
            spell_data={'heal_per_second': 5, 'radius': 100, 'duration': 8.0, 'cooldown': 20.0}
        ))

        # LIGHT TREE
        self.add_skill(SkillNode(
            'light_beam', 'Light Beam',
            'Focused beam of holy light.',
            MagicType.LIGHT, 0,
            spell_data={'damage': 15, 'range': 300, 'cooldown': 2.0, 'bonus_vs_darkness': 2.0}
        ))

        self.add_skill(SkillNode(
            'light_shield', 'Light Shield',
            'Create a protective barrier of light.',
            MagicType.LIGHT, 12,
            prerequisites=['light_beam'],
            spell_data={'shield_amount': 50, 'duration': 6.0, 'cooldown': 10.0}
        ))

        self.add_skill(SkillNode(
            'light_smite', 'Divine Smite',
            'Powerful holy attack from above.',
            MagicType.LIGHT, 22,
            prerequisites=['light_shield'],
            spell_data={'damage': 60, 'aoe_radius': 80, 'cooldown': 8.0, 'bonus_vs_darkness': 3.0}
        ))

        # DARKNESS TREE
        self.add_skill(SkillNode(
            'dark_bolt', 'Shadow Bolt',
            'Dark energy projectile that drains life.',
            MagicType.DARKNESS, 0,
            spell_data={'damage': 12, 'speed': 6, 'cooldown': 1.5, 'life_steal': 0.3}
        ))

        self.add_skill(SkillNode(
            'dark_curse', 'Curse',
            'Weaken enemies, reducing their damage.',
            MagicType.DARKNESS, 8,
            prerequisites=['dark_bolt'],
            spell_data={'damage_reduction': 0.5, 'duration': 6.0, 'cooldown': 8.0}
        ))

        self.add_skill(SkillNode(
            'dark_void', 'Void',
            'Create a zone of darkness that damages enemies.',
            MagicType.DARKNESS, 18,
            prerequisites=['dark_curse'],
            spell_data={'damage_per_second': 10, 'radius': 100, 'duration': 8.0, 'cooldown': 12.0}
        ))

        # PASSIVE UPGRADES
        self.add_skill(SkillNode(
            'passive_spell_slot_4', 'Additional Spell Slot (4th)',
            'Unlock the 4th spell slot.',
            MagicType.FIRE, 10,  # Can be unlocked with any magic type combination
            spell_data={'slot_number': 4},
            is_passive=True
        ))

        self.add_skill(SkillNode(
            'passive_spell_slot_5', 'Additional Spell Slot (5th)',
            'Unlock the 5th spell slot.',
            MagicType.WATER, 15,
            prerequisites=['passive_spell_slot_4'],
            spell_data={'slot_number': 5},
            is_passive=True
        ))

        self.add_skill(SkillNode(
            'passive_spell_slot_6', 'Additional Spell Slot (6th)',
            'Unlock the 6th spell slot.',
            MagicType.AIR, 20,
            prerequisites=['passive_spell_slot_5'],
            spell_data={'slot_number': 6},
            is_passive=True
        ))

    def add_skill(self, skill):
        """Add a skill to the tree"""
        self.skills[skill.skill_id] = skill

    def get_skill(self, skill_id):
        """Get a skill by ID"""
        return self.skills.get(skill_id)

    def can_learn_skill(self, skill_id):
        """Check if a skill can be learned"""
        skill = self.get_skill(skill_id)
        if not skill:
            return False

        magic_manager = get_magic_manager()
        return skill.can_learn(self.learned_skills, magic_manager)

    def learn_skill(self, skill_id):
        """Learn a skill"""
        skill = self.get_skill(skill_id)
        if not skill:
            return False

        if self.can_learn_skill(skill_id):
            magic_manager = get_magic_manager()
            if skill.learn(magic_manager):
                self.learned_skills.add(skill_id)
                self.save_to_file()
                magic_manager.save_to_file()
                return True

        return False

    def is_skill_learned(self, skill_id):
        """Check if a skill is learned"""
        return skill_id in self.learned_skills

    def get_learned_skills(self):
        """Get list of all learned skills"""
        return [self.skills[skill_id] for skill_id in self.learned_skills]

    def get_skills_by_type(self, magic_type):
        """Get all skills of a specific magic type"""
        return [skill for skill in self.skills.values() if skill.magic_type == magic_type]

    def get_available_skills(self):
        """Get all skills that can currently be learned"""
        available = []
        for skill_id, skill in self.skills.items():
            if self.can_learn_skill(skill_id):
                available.append(skill)
        return available

    def save_to_file(self):
        """Save learned skills to file"""
        try:
            os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
            save_data = {
                'learned_skills': list(self.learned_skills)
            }
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f, indent=2)
        except Exception as e:
            print(f"Error saving skill tree: {e}")

    def load_from_file(self):
        """Load learned skills from file"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    save_data = json.load(f)
                    self.learned_skills = set(save_data.get('learned_skills', []))

                    # Mark skills as learned
                    for skill_id in self.learned_skills:
                        if skill_id in self.skills:
                            self.skills[skill_id].learned = True
        except Exception as e:
            print(f"Error loading skill tree: {e}")

    def reset(self):
        """Reset all learned skills"""
        self.learned_skills.clear()
        for skill in self.skills.values():
            skill.learned = False

    def get_max_spell_slots(self):
        """Get the maximum number of spell slots based on learned skills"""
        base_slots = 3

        if 'passive_spell_slot_6' in self.learned_skills:
            return 6
        elif 'passive_spell_slot_5' in self.learned_skills:
            return 5
        elif 'passive_spell_slot_4' in self.learned_skills:
            return 4

        return base_slots


# Global instance
_skill_tree = None


def get_skill_tree():
    """Get the global skill tree instance"""
    global _skill_tree
    if _skill_tree is None:
        _skill_tree = SkillTree()
        _skill_tree.load_from_file()
    return _skill_tree
