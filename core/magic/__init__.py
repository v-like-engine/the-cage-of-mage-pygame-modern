"""
Magic System Package
"""
from core.magic.magic_system import (
    MagicType,
    ShardSize,
    MagicPowerManager,
    get_magic_manager
)
from core.magic.magic_shards import MagicShard, ShardSpawner
from core.magic.skill_tree import SkillNode, SkillTree, get_skill_tree
from core.magic.spell_slots import SpellSlots, get_spell_slots, SpellSlotsUI
from core.magic.spells import (
    Particle,
    SpellProjectile,
    FireballProjectile,
    WaterProjectile,
    AirProjectile,
    EarthProjectile,
    LightningProjectile,
    LightBeamProjectile,
    DarkBoltProjectile,
    SpellCaster
)

__all__ = [
    'MagicType',
    'ShardSize',
    'MagicPowerManager',
    'get_magic_manager',
    'MagicShard',
    'ShardSpawner',
    'SkillNode',
    'SkillTree',
    'get_skill_tree',
    'SpellSlots',
    'get_spell_slots',
    'SpellSlotsUI',
    'Particle',
    'SpellProjectile',
    'FireballProjectile',
    'WaterProjectile',
    'AirProjectile',
    'EarthProjectile',
    'LightningProjectile',
    'LightBeamProjectile',
    'DarkBoltProjectile',
    'SpellCaster',
]
