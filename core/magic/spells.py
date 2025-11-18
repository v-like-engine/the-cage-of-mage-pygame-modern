"""
Spell Effects and Projectiles
Visual and functional spell implementations
"""
import pygame
import math
from core.magic.magic_system import MagicType


class Particle(pygame.sprite.Sprite):
    """A single particle for visual effects"""

    def __init__(self, x, y, velocity_x, velocity_y, color, size, lifetime):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.image = pygame.Surface((int(size * 2), int(size * 2)))
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def update(self, delta_time=1/120):
        """Update particle position and lifetime"""
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            self.kill()
            return

        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Apply gravity/fade
        self.velocity_y += 0.1

        # Update rect
        self.rect.center = (int(self.x), int(self.y))

        # Draw particle with fade
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        self.image.fill((0, 0, 0))
        pygame.draw.circle(self.image, self.color, (int(self.size), int(self.size)), int(self.size))
        self.image.set_alpha(alpha)


class SpellProjectile(pygame.sprite.Sprite):
    """Base class for spell projectiles"""

    def __init__(self, x, y, target_x, target_y, spell_data, magic_type):
        super().__init__()
        self.start_x = float(x)
        self.start_y = float(y)
        self.x = float(x)
        self.y = float(y)
        self.spell_data = spell_data
        self.magic_type = magic_type
        self.damage = spell_data.get('damage', 10)

        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            self.velocity_x = 0
            self.velocity_y = 0
        else:
            speed = spell_data.get('speed', 5)
            self.velocity_x = (dx / distance) * speed
            self.velocity_y = (dy / distance) * speed

        # Visual properties
        self.color = MagicType.COLORS[magic_type]
        self.size = 10
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(int(x), int(y)))

        # Lifetime
        self.lifetime = 10.0  # seconds
        self.alive_time = 0

        # Particle trail
        self.particles = pygame.sprite.Group()
        self.particle_timer = 0

    def _create_image(self):
        """Create the projectile image"""
        img = pygame.Surface((self.size * 2, self.size * 2))
        img.set_colorkey((0, 0, 0))
        pygame.draw.circle(img, self.color, (self.size, self.size), self.size)

        # Add glow effect
        glow_size = self.size + 5
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2))
        glow_surf.set_colorkey((0, 0, 0))
        glow_surf.set_alpha(100)
        pygame.draw.circle(glow_surf, self.color, (glow_size, glow_size), glow_size)

        # Combine
        final = pygame.Surface((glow_size * 2, glow_size * 2))
        final.set_colorkey((0, 0, 0))
        final.blit(glow_surf, (0, 0))
        final.blit(img, ((glow_size - self.size), (glow_size - self.size)))

        return final

    def update(self, delta_time=1/120):
        """Update projectile position"""
        self.alive_time += delta_time

        if self.alive_time >= self.lifetime:
            self.kill()
            return

        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rect.center = (int(self.x), int(self.y))

        # Create particle trail
        self.particle_timer += delta_time
        if self.particle_timer >= 0.05:  # Spawn particle every 0.05s
            self.particle_timer = 0
            particle = Particle(
                self.x, self.y,
                self.velocity_x * -0.3,
                self.velocity_y * -0.3,
                self.color,
                3,
                0.5
            )
            self.particles.add(particle)

        # Update particles
        self.particles.update(delta_time)

    def draw_particles(self, screen):
        """Draw particle trail"""
        self.particles.draw(screen)

    def check_collision(self, target_rect):
        """Check if projectile hits a target"""
        return self.rect.colliderect(target_rect)

    def check_wall_collision(self, borders):
        """Check if projectile hits a wall"""
        return pygame.sprite.spritecollideany(self, borders)

    def get_damage(self):
        """Get the damage this projectile deals"""
        return self.damage


class FireballProjectile(SpellProjectile):
    """Fireball spell projectile"""

    def __init__(self, x, y, target_x, target_y, spell_data):
        super().__init__(x, y, target_x, target_y, spell_data, MagicType.FIRE)
        self.size = 15
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(int(x), int(y)))


class WaterProjectile(SpellProjectile):
    """Water spell projectile"""

    def __init__(self, x, y, target_x, target_y, spell_data):
        super().__init__(x, y, target_x, target_y, spell_data, MagicType.WATER)
        self.size = 12
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(int(x), int(y)))


class AirProjectile(SpellProjectile):
    """Air/Wind spell projectile"""

    def __init__(self, x, y, target_x, target_y, spell_data):
        super().__init__(x, y, target_x, target_y, spell_data, MagicType.AIR)
        self.size = 8
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(int(x), int(y)))


class EarthProjectile(SpellProjectile):
    """Earth/Rock spell projectile"""

    def __init__(self, x, y, target_x, target_y, spell_data):
        super().__init__(x, y, target_x, target_y, spell_data, MagicType.EARTH)
        self.size = 18
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(int(x), int(y)))

    def update(self, delta_time=1/120):
        """Earth projectiles have gravity"""
        super().update(delta_time)
        self.velocity_y += 0.15  # Gravity effect


class LightningProjectile(SpellProjectile):
    """Lightning spell projectile"""

    def __init__(self, x, y, target_x, target_y, spell_data):
        super().__init__(x, y, target_x, target_y, spell_data, MagicType.ELECTRICITY)
        self.size = 10
        # Lightning is instant, so very fast
        speed = spell_data.get('speed', 20)
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            self.velocity_x = (dx / distance) * speed
            self.velocity_y = (dy / distance) * speed
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(int(x), int(y)))


class LightBeamProjectile(SpellProjectile):
    """Light beam spell projectile"""

    def __init__(self, x, y, target_x, target_y, spell_data):
        super().__init__(x, y, target_x, target_y, spell_data, MagicType.LIGHT)
        self.size = 8
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(int(x), int(y)))


class DarkBoltProjectile(SpellProjectile):
    """Dark energy spell projectile"""

    def __init__(self, x, y, target_x, target_y, spell_data):
        super().__init__(x, y, target_x, target_y, spell_data, MagicType.DARKNESS)
        self.size = 12
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(int(x), int(y)))


class SpellCaster:
    """Handles spell casting logic"""

    PROJECTILE_CLASSES = {
        # Fire spells
        'fire_spark': FireballProjectile,
        'fire_fireball': FireballProjectile,

        # Water spells
        'water_splash': WaterProjectile,

        # Air spells
        'air_gust': AirProjectile,

        # Earth spells
        'earth_rock': EarthProjectile,

        # Electricity spells
        'elec_shock': LightningProjectile,
        'elec_lightning': LightningProjectile,

        # Light spells
        'light_beam': LightBeamProjectile,

        # Darkness spells
        'dark_bolt': DarkBoltProjectile,
    }

    @staticmethod
    def cast_projectile_spell(skill, caster_x, caster_y, target_x, target_y):
        """
        Cast a projectile spell

        Args:
            skill: The skill being cast
            caster_x, caster_y: Position of the caster
            target_x, target_y: Target position

        Returns:
            SpellProjectile instance or None
        """
        projectile_class = SpellCaster.PROJECTILE_CLASSES.get(skill.skill_id)

        if projectile_class:
            return projectile_class(caster_x, caster_y, target_x, target_y, skill.spell_data)

        return None

    @staticmethod
    def cast_area_spell(skill, caster_x, caster_y):
        """
        Cast an area effect spell

        Returns:
            Area effect data dictionary
        """
        return {
            'type': 'area',
            'skill': skill,
            'x': caster_x,
            'y': caster_y,
            'radius': skill.spell_data.get('aoe_radius', 50),
            'damage': skill.spell_data.get('damage', 20),
            'duration': skill.spell_data.get('duration', 1.0)
        }

    @staticmethod
    def cast_utility_spell(skill, caster):
        """
        Cast a utility spell (heal, shield, etc.)

        Returns:
            Utility effect data dictionary
        """
        return {
            'type': 'utility',
            'skill': skill,
            'caster': caster
        }
