"""
Pause Menu with Skill Tree Access
"""
import pygame
import sys


class PauseMenuButton(pygame.sprite.Sprite):
    """Button for pause menu"""

    def __init__(self, x, y, width, height, text, font_path, action):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.action = action
        self.font = pygame.font.Font(font_path, 36)

        # Create button surface
        self.image_normal = pygame.Surface((width, height))
        self.image_hover = pygame.Surface((width, height))

        # Normal state
        self.image_normal.fill((50, 50, 50))
        pygame.draw.rect(self.image_normal, (200, 200, 200), (0, 0, width, height), 3)
        text_surf = self.font.render(text, True, (200, 200, 200))
        text_rect = text_surf.get_rect(center=(width // 2, height // 2))
        self.image_normal.blit(text_surf, text_rect)

        # Hover state
        self.image_hover.fill((80, 80, 80))
        pygame.draw.rect(self.image_hover, (255, 255, 255), (0, 0, width, height), 3)
        text_surf_hover = self.font.render(text, True, (255, 255, 255))
        self.image_hover.blit(text_surf_hover, text_rect)

        self.image = self.image_normal
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hovered = False

    def update(self):
        """Update button state based on mouse position"""
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            self.image = self.image_hover
            self.hovered = True
        else:
            self.image = self.image_normal
            self.hovered = False

    def is_clicked(self, event):
        """Check if button was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                return True
        return False


class PauseMenu:
    """Pause menu overlay"""

    def __init__(self, screen, font_path, on_resume, on_skill_tree, on_main_menu):
        self.screen = screen
        self.font_path = font_path
        self.width = screen.get_width()
        self.height = screen.get_height()

        # Callbacks
        self.on_resume = on_resume
        self.on_skill_tree = on_skill_tree
        self.on_main_menu = on_main_menu

        # Create semi-transparent overlay
        self.overlay = pygame.Surface((self.width, self.height))
        self.overlay.fill((0, 0, 0))
        self.overlay.set_alpha(180)

        # Create buttons
        self.buttons = pygame.sprite.Group()
        button_width = 400
        button_height = 60
        button_x = (self.width - button_width) // 2
        start_y = self.height // 3

        self.resume_btn = PauseMenuButton(
            button_x, start_y,
            button_width, button_height,
            'Resume', font_path, 'resume'
        )
        self.buttons.add(self.resume_btn)

        self.skill_tree_btn = PauseMenuButton(
            button_x, start_y + 80,
            button_width, button_height,
            'Skill Tree', font_path, 'skill_tree'
        )
        self.buttons.add(self.skill_tree_btn)

        self.main_menu_btn = PauseMenuButton(
            button_x, start_y + 160,
            button_width, button_height,
            'Main Menu', font_path, 'main_menu'
        )
        self.buttons.add(self.main_menu_btn)

        # Title
        self.title_font = pygame.font.Font(font_path, 72)
        self.title_text = self.title_font.render('PAUSED', True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(center=(self.width // 2, 150))

        self.active = False

    def handle_event(self, event):
        """Handle input events"""
        if not self.active:
            return None

        # Check button clicks
        if self.resume_btn.is_clicked(event):
            self.active = False
            if self.on_resume:
                self.on_resume()
            return 'resume'

        if self.skill_tree_btn.is_clicked(event):
            if self.on_skill_tree:
                self.on_skill_tree()
            return 'skill_tree'

        if self.main_menu_btn.is_clicked(event):
            if self.on_main_menu:
                self.on_main_menu()
            return 'main_menu'

        # ESC to close
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active = False
                if self.on_resume:
                    self.on_resume()
                return 'resume'

        return None

    def update(self):
        """Update menu state"""
        if self.active:
            self.buttons.update()

    def draw(self):
        """Draw pause menu"""
        if not self.active:
            return

        # Draw overlay
        self.screen.blit(self.overlay, (0, 0))

        # Draw title
        self.screen.blit(self.title_text, self.title_rect)

        # Draw buttons
        self.buttons.draw(self.screen)

    def show(self):
        """Show the pause menu"""
        self.active = True
        pygame.mouse.set_visible(True)

    def hide(self):
        """Hide the pause menu"""
        self.active = False
        pygame.mouse.set_visible(False)

    def toggle(self):
        """Toggle pause menu visibility"""
        if self.active:
            self.hide()
        else:
            self.show()
