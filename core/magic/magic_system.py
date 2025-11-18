"""
Core Magic System for The Cage of Mage
Handles magic types, power points, and player magic state
"""
import json
import os


class MagicType:
    """Enum-like class for magic types"""
    FIRE = 'fire'
    WATER = 'water'
    AIR = 'air'
    EARTH = 'earth'
    ELECTRICITY = 'electricity'
    LIFE = 'life'
    LIGHT = 'light'
    DARKNESS = 'darkness'

    ALL_TYPES = [FIRE, WATER, AIR, EARTH, ELECTRICITY, LIFE, LIGHT, DARKNESS]

    # Color mapping for visual representation
    COLORS = {
        FIRE: (255, 69, 0),
        WATER: (30, 144, 255),
        AIR: (173, 216, 230),
        EARTH: (139, 69, 19),
        ELECTRICITY: (255, 255, 0),
        LIFE: (0, 255, 0),
        LIGHT: (255, 255, 255),
        DARKNESS: (75, 0, 130)
    }


class ShardSize:
    """Enum-like class for shard sizes"""
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'

    # Power points awarded by each size
    POWER_POINTS = {
        SMALL: 1,
        MEDIUM: 5,
        LARGE: 10
    }


class MagicPowerManager:
    """Manages the player's magic power points for all types"""

    def __init__(self):
        self.power_points = {magic_type: 0 for magic_type in MagicType.ALL_TYPES}
        self.save_file = 'data/magic_power.json'

    def add_power(self, magic_type, amount):
        """Add magic power points of a specific type"""
        if magic_type in self.power_points:
            self.power_points[magic_type] += amount
            return True
        return False

    def spend_power(self, magic_type, amount):
        """Spend magic power points if available"""
        if magic_type in self.power_points and self.power_points[magic_type] >= amount:
            self.power_points[magic_type] -= amount
            return True
        return False

    def get_power(self, magic_type):
        """Get current power points for a specific type"""
        return self.power_points.get(magic_type, 0)

    def has_enough_power(self, magic_type, amount):
        """Check if player has enough power of a specific type"""
        return self.get_power(magic_type) >= amount

    def save_to_file(self):
        """Save magic power to file"""
        try:
            os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
            with open(self.save_file, 'w') as f:
                json.dump(self.power_points, f, indent=2)
        except Exception as e:
            print(f"Error saving magic power: {e}")

    def load_from_file(self):
        """Load magic power from file"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    loaded_data = json.load(f)
                    # Merge loaded data with default structure
                    for magic_type in MagicType.ALL_TYPES:
                        if magic_type in loaded_data:
                            self.power_points[magic_type] = loaded_data[magic_type]
        except Exception as e:
            print(f"Error loading magic power: {e}")

    def reset(self):
        """Reset all magic power to 0"""
        self.power_points = {magic_type: 0 for magic_type in MagicType.ALL_TYPES}


# Global instance for easy access throughout the game
_magic_power_manager = None


def get_magic_manager():
    """Get the global magic power manager instance"""
    global _magic_power_manager
    if _magic_power_manager is None:
        _magic_power_manager = MagicPowerManager()
        _magic_power_manager.load_from_file()
    return _magic_power_manager
