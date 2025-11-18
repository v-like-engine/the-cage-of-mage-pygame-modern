"""
Magic Shards - Collectible items that give magic power
"""
import pygame
from core.magic.magic_system import MagicType, ShardSize, get_magic_manager
from utils.load_image import load_image


class MagicShard(pygame.sprite.Sprite):
    """A collectible magic shard that gives magic power"""

    def __init__(self, x, y, magic_type, size):
        """
        Initialize a magic shard

        Args:
            x, y: Position coordinates
            magic_type: Type of magic (from MagicType)
            size: Size of shard (from ShardSize)
        """
        super().__init__()
        self.x = x
        self.y = y
        self.magic_type = magic_type
        self.size = size
        self.power_value = ShardSize.POWER_POINTS[size]

        # Load base image based on size
        self.base_image = self._load_shard_image()

        # Apply color tint based on magic type
        self.image = self._apply_color_tint()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Animation properties
        self.float_offset = 0
        self.float_speed = 0.05
        self.rotation = 0
        self.rotation_speed = 2

        # Particle effect
        self.glow_radius = 0
        self.glow_growing = True

        # Collection flag
        self.collected = False

    def _load_shard_image(self):
        """Load the base shard image based on size"""
        size_to_file = {
            ShardSize.SMALL: 'items/mana_small.png',
            ShardSize.MEDIUM: 'items/mana_medium.png',
            ShardSize.LARGE: 'items/mana_large.png'
        }
        return load_image(size_to_file[self.size])

    def _apply_color_tint(self):
        """Apply color tint to the shard based on magic type"""
        # Create a copy of the base image
        tinted_image = self.base_image.copy()

        # Get the color for this magic type
        color = MagicType.COLORS[self.magic_type]

        # Create a surface with the tint color
        tint_surface = pygame.Surface(tinted_image.get_size()).convert_alpha()
        tint_surface.fill((*color, 128))  # Semi-transparent tint

        # Blend the tint with the original image
        tinted_image.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        return tinted_image

    def update(self):
        """Update shard animation"""
        if self.collected:
            return

        # Floating animation
        self.float_offset += self.float_speed
        float_y = int(5 * pygame.math.Vector2(0, 1).rotate(self.float_offset * 10).y)
        self.rect.y = self.y + float_y

        # Glow pulsing effect
        if self.glow_growing:
            self.glow_radius += 0.5
            if self.glow_radius >= 10:
                self.glow_growing = False
        else:
            self.glow_radius -= 0.5
            if self.glow_radius <= 0:
                self.glow_growing = True

    def draw_glow(self, surface):
        """Draw a glow effect around the shard"""
        if self.collected:
            return

        color = MagicType.COLORS[self.magic_type]
        glow_surface = pygame.Surface((int(self.glow_radius * 2), int(self.glow_radius * 2)))
        glow_surface.set_colorkey((0, 0, 0))
        glow_surface.set_alpha(50)

        center = (int(self.glow_radius), int(self.glow_radius))
        pygame.draw.circle(glow_surface, color, center, int(self.glow_radius))

        glow_pos = (
            self.rect.centerx - int(self.glow_radius),
            self.rect.centery - int(self.glow_radius)
        )
        surface.blit(glow_surface, glow_pos)

    def collect(self):
        """Collect this shard and add power to the magic manager"""
        if not self.collected:
            self.collected = True
            manager = get_magic_manager()
            manager.add_power(self.magic_type, self.power_value)
            manager.save_to_file()
            return True
        return False

    def check_collection(self, mage_rect):
        """Check if the mage is close enough to collect this shard"""
        if not self.collected:
            # Check collision with mage
            if self.rect.colliderect(mage_rect):
                return self.collect()
        return False


class ShardSpawner:
    """Helper class to easily spawn shards in levels"""

    @staticmethod
    def create_shard(x, y, magic_type, size='small'):
        """
        Create a magic shard

        Args:
            x, y: Position
            magic_type: Type from MagicType (e.g., MagicType.FIRE)
            size: Size from ShardSize (default: 'small')
        """
        return MagicShard(x, y, magic_type, size)

    @staticmethod
    def create_fire_shard(x, y, size='small'):
        return MagicShard(x, y, MagicType.FIRE, size)

    @staticmethod
    def create_water_shard(x, y, size='small'):
        return MagicShard(x, y, MagicType.WATER, size)

    @staticmethod
    def create_air_shard(x, y, size='small'):
        return MagicShard(x, y, MagicType.AIR, size)

    @staticmethod
    def create_earth_shard(x, y, size='small'):
        return MagicShard(x, y, MagicType.EARTH, size)

    @staticmethod
    def create_electricity_shard(x, y, size='small'):
        return MagicShard(x, y, MagicType.ELECTRICITY, size)

    @staticmethod
    def create_life_shard(x, y, size='small'):
        return MagicShard(x, y, MagicType.LIFE, size)

    @staticmethod
    def create_light_shard(x, y, size='small'):
        return MagicShard(x, y, MagicType.LIGHT, size)

    @staticmethod
    def create_darkness_shard(x, y, size='small'):
        return MagicShard(x, y, MagicType.DARKNESS, size)
