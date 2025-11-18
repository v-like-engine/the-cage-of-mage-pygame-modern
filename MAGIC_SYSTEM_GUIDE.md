# The Cage of Mage - Magic System Guide

## Overview

This guide explains all the new magic system features that have been added to The Cage of Mage.

## Table of Contents
1. [Magic Shards](#magic-shards)
2. [Skill Tree](#skill-tree)
3. [Spell Slots](#spell-slots)
4. [Pause Menu](#pause-menu)
5. [NPC Combat AI](#npc-combat-ai)
6. [Sandbox Mode](#sandbox-mode)
7. [Developer Guide](#developer-guide)

---

## Magic Shards

### Overview
Magic shards are collectible items scattered throughout levels that give the mage magical power points.

### Types of Magic
There are **8 types** of magic:
- 🔥 **Fire** - Offensive, high damage spells
- 💧 **Water** - Control and slowing effects
- 💨 **Air** - Fast, mobility-based spells
- 🌍 **Earth** - Defensive and heavy damage
- ⚡ **Electricity** - Chain damage and stuns
- 💚 **Life** - Healing and regeneration
- ✨ **Light** - Holy damage, shields
- 🌑 **Darkness** - Life steal and curses

### Shard Sizes
- **Small** - Awards 1 power point
- **Medium** - Awards 5 power points
- **Large** - Awards 10 power points

### Collection
Walk over a magic shard to collect it automatically. The power points are saved to your profile.

---

## Skill Tree

### Accessing the Skill Tree
- **From Main Menu**: Click "Skill Tree" button
- **During Gameplay**: Press `T` or open Pause Menu and select "Skill Tree"
- **From Pause Menu**: Select "Skill Tree"

### How Skills Work

#### Learning Skills
1. Each skill requires a specific amount of magic power points of its type
2. Some skills have prerequisites (must learn earlier skills first)
3. Click on a skill node to learn it if you have enough power points

#### Skill Categories

**Active Spells** - Cast using spell slots (1-6 keys):
- Fire: Spark → Fireball → Meteor → Inferno
- Water: Splash → Stream → Tsunami
- Air: Gust → Tornado, Air Dash
- Earth: Rock Throw → Wall → Earthquake
- Electricity: Shock → Lightning → Storm
- Life: Heal → Regeneration → Sanctuary
- Light: Beam → Shield → Smite
- Darkness: Bolt → Curse → Void

**Passive Upgrades**:
- Additional Spell Slots (4th, 5th, 6th)
- Various skill enhancements

### UI Navigation
- **Mouse Wheel**: Scroll through the skill tree
- **Click**: Learn a skill
- **Hover**: View skill details
- **ESC**: Close skill tree

---

## Spell Slots

### Overview
You have **3-6 spell slots** (expandable through skill tree) where you can equip learned spells for quick access in combat.

### Equipping Spells
1. Learn a skill from the skill tree
2. The spell becomes available for equipping
3. Assign it to a slot (1-6) for quick casting

### Casting Spells
- Press keys **1-6** to cast equipped spells
- Aim with your **mouse cursor**
- Each spell has a **cooldown** shown on the slot UI

### Spell Slots UI
Located at the bottom left of the screen:
- **Bright blue**: Spell ready to cast
- **Dark blue**: Spell on cooldown
- **Gray**: Empty slot
- **Numbers**: Show cooldown time remaining

---

## Pause Menu

### Accessing Pause Menu
Press **ESC** during gameplay to open the pause menu.

### Options
- **Resume**: Return to game
- **Skill Tree**: Open skill tree (progress is saved)
- **Main Menu**: Return to main menu

### Important Notes
- Game progress is NOT lost when accessing the skill tree from pause menu
- All learned skills and collected shards are saved automatically
- Cooldowns are paused while in menu

---

## NPC Combat AI

### Enemy Types

#### Guards (Melee)
- Use fists or melee weapons
- Will chase the player when detected
- Attack range: 50 pixels
- Can dodge incoming attacks

#### Ranged Enemies
- Use guns/ranged weapons
- Seek cover when under fire
- Attack range: 400 pixels
- Will peek from cover to attack

### AI Behaviors

**Patrol**: Enemies walk between patrol points when idle
**Chase**: Pursue the player when detected (300 pixel detection range)
**Attack**: Engage when in range
**Dodge**: 30% chance to dodge when taking damage
**Hide**: Ranged enemies seek cover behind obstacles

### Combat Tips
- Use ranged spells against melee enemies
- Flank ranged enemies in cover
- Area spells can hit multiple enemies
- Watch enemy health bars above their heads

---

## Sandbox Mode

### Overview
Practice combat against customizable enemy waves after completing the main story.

### Accessing Sandbox
From the **Main Menu**, click **"Sandbox"**

### Controls
- **1-6**: Cast equipped spells
- **Mouse**: Aim spells
- **Arrow Keys**: Move
- **ESC**: Pause menu
- **R**: Restart current wave
- **N**: Next wave (after completing current)

### Wave System
- Waves spawn increasing numbers of enemies
- Defeat all enemies to complete a wave
- Configure custom waves by modifying `wave_config` parameter

### HUD Elements
- **Health Bar** (top left): Player health
- **Wave Counter** (top right): Current wave / total waves
- **Enemy Count**: Remaining enemies
- **Spell Slots** (bottom): Your equipped spells with cooldowns

---

## Developer Guide

### Adding Magic Shards to Your Level

```python
from core.levels.enhanced_level_mask import EnhancedLevelMask
from core.magic import ShardSpawner, MagicType, ShardSize

class MyLevel(EnhancedLevelMask):
    def __init__(self, width, height):
        super().__init__(width, height, 0.0, mage_prefs, False, 'background.jpg')

        # Add fire shard
        fire_shard = ShardSpawner.create_fire_shard(100, 200, ShardSize.MEDIUM)
        self.add_magic_shard(fire_shard)

        # Add water shard
        water_shard = ShardSpawner.create_water_shard(300, 250, ShardSize.LARGE)
        self.add_magic_shard(water_shard)
```

### Creating Custom Magic Shards

```python
from core.magic import MagicShard, MagicType, ShardSize

# Create a custom shard
shard = MagicShard(x, y, MagicType.ELECTRICITY, ShardSize.LARGE)
self.add_magic_shard(shard)
```

### Adding Enemies to Your Level

```python
from core.classes.enemy_ai import EnemyAI

# Create a guard enemy
guard = EnemyAI(x, y, 'guard', self.platforms)
guard.set_target(self.mage)  # Set player as target
self.enemies.add(guard)

# Create a ranged enemy
ranged_enemy = EnemyAI(x, y, 'ranged', self.platforms)
ranged_enemy.set_target(self.mage)
self.enemies.add(ranged_enemy)
```

### Integrating Magic System in Your Level

1. **Extend EnhancedLevelMask** instead of LevelMask
2. **Add magic shards** using `self.add_magic_shard(shard)`
3. **Update game logic** by calling `self.update_game_logic(delta_time)` in your game loop
4. **Draw enhanced elements** by calling `self.draw_enhanced_elements()` in your render method

### Example Level Template

```python
from core.levels.enhanced_level_mask import EnhancedLevelMask
from core.magic import ShardSpawner, ShardSize

class MyLevel(EnhancedLevelMask):
    def __init__(self, width, height):
        super().__init__(width, height, 0.0, (50, 456, 240, 360, 240),
                        False, 'training.jpg')

        # Add shards
        self._spawn_shards()

        self.execute()

    def _spawn_shards(self):
        shard = ShardSpawner.create_fire_shard(200, 500, ShardSize.SMALL)
        self.add_magic_shard(shard)

    def execute(self):
        while self.running:
            delta_time = 1 / self.FPS

            for event in pygame.event.get():
                self.handle_event(event)

            if not self.game_paused and not self.skill_tree_open:
                self.loop()
                self.update_game_logic(delta_time)
                self.check_movement()

            # Render
            self.all_sprites.draw(self.screen)
            self.mage_group.draw(self.screen)
            self.draw_enhanced_elements()

            pygame.display.flip()
            self.clock.tick(self.FPS)
```

### Customizing the Skill Tree

Edit `core/magic/skill_tree.py` to add new skills:

```python
self.add_skill(SkillNode(
    'my_custom_spell',           # Unique ID
    'Custom Spell',              # Display name
    'Does something awesome',    # Description
    MagicType.FIRE,             # Magic type
    10,                         # Cost in power points
    prerequisites=['fire_spark'], # Required skills
    spell_data={                # Spell parameters
        'damage': 30,
        'speed': 8,
        'cooldown': 3.0
    }
))
```

### Save Files

The magic system uses JSON files to save progress:
- `data/magic_power.json` - Magic power points
- `data/skill_tree.json` - Learned skills
- `data/spell_slots.json` - Equipped spells

---

## Tips and Tricks

1. **Collect all shards** in each level before progressing
2. **Balance your skill tree** - Don't focus on just one magic type
3. **Unlock spell slots early** - More spells = more versatility
4. **Experiment in Sandbox mode** - Perfect for testing builds
5. **Use cover against ranged enemies** - Hide behind obstacles
6. **Combo spells** - Some spell combinations are very effective
7. **Watch cooldowns** - Don't spam, time your casts

---

## Keyboard Reference

| Key | Action |
|-----|--------|
| Arrow Keys | Move mage |
| 1-6 | Cast spell from slot |
| T | Open skill tree (in game) |
| ESC | Pause menu |
| R | Restart wave/level |
| N | Next wave (Sandbox) |
| E | Interact (doors, etc.) |
| ENTER | Progress to next level |

---

## Troubleshooting

**Q: My spells aren't casting**
- Check if spell is equipped in a slot
- Verify spell is not on cooldown
- Make sure game is not paused

**Q: Can't learn a skill**
- Check if you have enough power points
- Verify prerequisites are met
- Make sure you haven't already learned it

**Q: Shards not appearing**
- Shards must be added in level code
- Check if they've already been collected

**Q: Enemies not spawning**
- Verify enemy code is in level initialization
- Check that `set_target()` is called

---

## Credits

Magic System Implementation for The Cage of Mage
- 8 Magic Types with Color-Coded Shards
- Skill Tree with 30+ Skills
- Dynamic Spell Casting System
- NPC Combat AI
- Sandbox Practice Mode
- Fully Integrated Pause Menu & UI
