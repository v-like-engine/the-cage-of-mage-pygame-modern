"""
Skill Tree UI
Interactive skill tree interface
"""
import pygame
from core.magic.magic_system import MagicType, get_magic_manager
from core.magic.skill_tree import get_skill_tree
from core.magic.spell_slots import get_spell_slots


class SkillNodeUI:
    """Visual representation of a skill node"""

    def __init__(self, skill, x, y, size=60):
        self.skill = skill
        self.x = x
        self.y = y
        self.size = size
        self.rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
        self.hovered = False

    def draw(self, screen, font, small_font):
        """Draw the skill node"""
        # Determine color based on state
        if self.skill.learned:
            # Learned - bright color
            color = MagicType.COLORS[self.skill.magic_type]
            border_color = (255, 255, 255)
        else:
            # Not learned - dark color
            r, g, b = MagicType.COLORS[self.skill.magic_type]
            color = (r // 3, g // 3, b // 3)
            border_color = (100, 100, 100)

        # Draw node circle
        pygame.draw.circle(screen, color, (self.x, self.y), self.size // 2)
        border_width = 3 if not self.hovered else 5
        pygame.draw.circle(screen, border_color, (self.x, self.y), self.size // 2, border_width)

        # Draw skill name (abbreviated)
        if self.size >= 50:
            text = small_font.render(self.skill.name[:8], True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.x, self.y))
            screen.blit(text, text_rect)

        # Draw cost if not learned
        if not self.skill.learned:
            cost_text = small_font.render(str(self.skill.cost), True, (255, 200, 0))
            cost_rect = cost_text.get_rect(center=(self.x, self.y + self.size // 2 + 12))
            screen.blit(cost_text, cost_rect)

    def check_hover(self, mouse_pos):
        """Check if mouse is hovering over this node"""
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        distance = (dx * dx + dy * dy) ** 0.5
        self.hovered = distance <= self.size // 2
        return self.hovered

    def is_clicked(self, mouse_pos):
        """Check if node was clicked"""
        return self.hovered


class SkillTreeUI:
    """Full skill tree interface"""

    def __init__(self, screen, font_path, return_callback):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.font_path = font_path
        self.return_callback = return_callback

        # Fonts
        self.title_font = pygame.font.Font(font_path, 48)
        self.font = pygame.font.Font(font_path, 24)
        self.small_font = pygame.font.Font(font_path, 16)
        self.tiny_font = pygame.font.Font(font_path, 12)

        # Background
        self.background = pygame.Surface((self.width, self.height))
        self.background.fill((20, 20, 30))

        # Skill tree instance
        self.skill_tree = get_skill_tree()
        self.magic_manager = get_magic_manager()
        self.spell_slots = get_spell_slots()

        # Create node UI elements
        self.node_uis = {}
        self.create_node_layout()

        # Selected node for details
        self.selected_node = None

        # Scrolling
        self.scroll_offset_y = 0
        self.scroll_speed = 20

        self.active = False

    def create_node_layout(self):
        """Create the layout of skill nodes"""
        # Define positions for each magic type tree
        # We'll arrange them in columns

        trees = [
            (MagicType.FIRE, 150),
            (MagicType.WATER, 300),
            (MagicType.AIR, 450),
            (MagicType.EARTH, 600),
            (MagicType.ELECTRICITY, 750),
            (MagicType.LIFE, 900),
            (MagicType.LIGHT, 1050),
            (MagicType.DARKNESS, 1200),
        ]

        # Layout each tree vertically
        for magic_type, column_x in trees:
            skills = self.skill_tree.get_skills_by_type(magic_type)

            # Sort by prerequisites to get tree order
            sorted_skills = self._sort_skills_by_tier(skills)

            # Position nodes vertically
            start_y = 150
            y_spacing = 120

            for i, skill in enumerate(sorted_skills):
                y = start_y + i * y_spacing
                node_ui = SkillNodeUI(skill, column_x, y)
                self.node_uis[skill.skill_id] = node_ui

    def _sort_skills_by_tier(self, skills):
        """Sort skills by their tier (number of prerequisites)"""
        def get_tier(skill):
            if not skill.prerequisites:
                return 0
            return 1 + max((get_tier(self.skill_tree.get_skill(prereq_id))
                           for prereq_id in skill.prerequisites), default=0)

        return sorted(skills, key=get_tier)

    def handle_event(self, event):
        """Handle input events"""
        if not self.active:
            return None

        # ESC to close
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active = False
                if self.return_callback:
                    self.return_callback()
                return 'close'

        # Mouse wheel for scrolling
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset_y += event.y * self.scroll_speed

        # Mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Check if clicking on a node
            for skill_id, node_ui in self.node_uis.items():
                adjusted_pos = (mouse_pos[0], mouse_pos[1] - self.scroll_offset_y)
                if node_ui.is_clicked(adjusted_pos):
                    # Try to learn skill
                    if not node_ui.skill.learned:
                        if self.skill_tree.learn_skill(skill_id):
                            # Successfully learned
                            self.selected_node = node_ui
                    else:
                        # Already learned, select for details
                        self.selected_node = node_ui
                    return 'skill_clicked'

        return None

    def update(self):
        """Update UI state"""
        if not self.active:
            return

        # Update hover states
        mouse_pos = pygame.mouse.get_pos()
        for node_ui in self.node_uis.values():
            adjusted_pos = (mouse_pos[0], mouse_pos[1] - self.scroll_offset_y)
            node_ui.check_hover(adjusted_pos)

    def draw(self):
        """Draw the skill tree UI"""
        if not self.active:
            return

        # Draw background
        self.screen.blit(self.background, (0, 0))

        # Create scrollable surface
        scroll_surface = pygame.Surface((self.width, 2000))
        scroll_surface.fill((20, 20, 30))

        # Draw connection lines between prerequisites
        for skill_id, node_ui in self.node_uis.items():
            skill = node_ui.skill
            for prereq_id in skill.prerequisites:
                if prereq_id in self.node_uis:
                    prereq_ui = self.node_uis[prereq_id]
                    # Draw line
                    color = (100, 100, 100) if not skill.learned else (200, 200, 200)
                    pygame.draw.line(scroll_surface, color,
                                   (prereq_ui.x, prereq_ui.y),
                                   (node_ui.x, node_ui.y), 2)

        # Draw skill nodes
        for node_ui in self.node_uis.values():
            node_ui.draw(scroll_surface, self.font, self.tiny_font)

        # Blit scrollable surface
        visible_rect = pygame.Rect(0, -self.scroll_offset_y, self.width, self.height - 200)
        self.screen.blit(scroll_surface, (0, 0), visible_rect)

        # Draw fixed UI elements on top
        self._draw_header()
        self._draw_magic_power_display()
        self._draw_skill_details()

    def _draw_header(self):
        """Draw header with title"""
        header_height = 100
        header_surf = pygame.Surface((self.width, header_height))
        header_surf.fill((10, 10, 20))

        title = self.title_font.render('SKILL TREE', True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, header_height // 2))
        header_surf.blit(title, title_rect)

        # Instructions
        instructions = self.small_font.render('Click to learn skills | ESC to close | Scroll to navigate',
                                              True, (200, 200, 200))
        inst_rect = instructions.get_rect(center=(self.width // 2, header_height - 20))
        header_surf.blit(instructions, inst_rect)

        self.screen.blit(header_surf, (0, 0))

    def _draw_magic_power_display(self):
        """Draw current magic power points"""
        panel_y = self.height - 150
        panel_height = 150
        panel_surf = pygame.Surface((self.width, panel_height))
        panel_surf.fill((10, 10, 20))

        title = self.font.render('Magic Power:', True, (255, 255, 255))
        panel_surf.blit(title, (20, 10))

        # Display power for each type
        x_start = 20
        y_start = 45
        col_width = 150

        for i, magic_type in enumerate(MagicType.ALL_TYPES):
            x = x_start + (i % 4) * col_width
            y = y_start + (i // 4) * 35

            color = MagicType.COLORS[magic_type]
            power = self.magic_manager.get_power(magic_type)

            # Draw colored square
            pygame.draw.rect(panel_surf, color, (x, y, 20, 20))

            # Draw type name and power
            text = self.small_font.render(f'{magic_type.capitalize()}: {power}',
                                          True, (255, 255, 255))
            panel_surf.blit(text, (x + 25, y))

        self.screen.blit(panel_surf, (0, panel_y))

    def _draw_skill_details(self):
        """Draw details of selected/hovered skill"""
        # Find hovered node
        hovered_node = None
        for node_ui in self.node_uis.values():
            if node_ui.hovered:
                hovered_node = node_ui
                break

        if not hovered_node and not self.selected_node:
            return

        node = hovered_node or self.selected_node
        skill = node.skill

        # Draw details panel
        panel_width = 400
        panel_height = 300
        panel_x = self.width - panel_width - 20
        panel_y = 120

        panel_surf = pygame.Surface((panel_width, panel_height))
        panel_surf.fill((30, 30, 40))
        pygame.draw.rect(panel_surf, (100, 100, 100), (0, 0, panel_width, panel_height), 2)

        y_offset = 10

        # Skill name
        name_text = self.font.render(skill.name, True, MagicType.COLORS[skill.magic_type])
        panel_surf.blit(name_text, (10, y_offset))
        y_offset += 35

        # Magic type
        type_text = self.small_font.render(f'Type: {skill.magic_type.capitalize()}',
                                           True, (200, 200, 200))
        panel_surf.blit(type_text, (10, y_offset))
        y_offset += 25

        # Cost
        cost_color = (0, 255, 0) if skill.learned else (255, 200, 0)
        cost_text = self.small_font.render(f'Cost: {skill.cost} {skill.magic_type}',
                                           True, cost_color)
        panel_surf.blit(cost_text, (10, y_offset))
        y_offset += 25

        # Status
        if skill.learned:
            status_text = self.small_font.render('LEARNED', True, (0, 255, 0))
        elif self.skill_tree.can_learn_skill(skill.skill_id):
            status_text = self.small_font.render('AVAILABLE', True, (255, 255, 0))
        else:
            status_text = self.small_font.render('LOCKED', True, (255, 0, 0))
        panel_surf.blit(status_text, (10, y_offset))
        y_offset += 30

        # Description (word wrap)
        self._draw_wrapped_text(panel_surf, skill.description, 10, y_offset,
                                panel_width - 20, self.small_font, (220, 220, 220))
        y_offset += 60

        # Prerequisites
        if skill.prerequisites:
            prereq_text = self.tiny_font.render('Requires:', True, (180, 180, 180))
            panel_surf.blit(prereq_text, (10, y_offset))
            y_offset += 20

            for prereq_id in skill.prerequisites:
                prereq_skill = self.skill_tree.get_skill(prereq_id)
                if prereq_skill:
                    prereq_color = (0, 255, 0) if prereq_skill.learned else (255, 100, 100)
                    prereq_name = self.tiny_font.render(f'  - {prereq_skill.name}',
                                                        True, prereq_color)
                    panel_surf.blit(prereq_name, (10, y_offset))
                    y_offset += 18

        self.screen.blit(panel_surf, (panel_x, panel_y))

    def _draw_wrapped_text(self, surface, text, x, y, max_width, font, color):
        """Draw text with word wrapping"""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            test_surf = font.render(test_line, True, color)

            if test_surf.get_width() > max_width:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []

        if current_line:
            lines.append(' '.join(current_line))

        for i, line in enumerate(lines):
            line_surf = font.render(line, True, color)
            surface.blit(line_surf, (x, y + i * 20))

    def show(self):
        """Show the skill tree UI"""
        self.active = True
        pygame.mouse.set_visible(True)
        # Reload data in case it changed
        self.skill_tree.load_from_file()
        self.magic_manager.load_from_file()

    def hide(self):
        """Hide the skill tree UI"""
        self.active = False
        pygame.mouse.set_visible(False)
