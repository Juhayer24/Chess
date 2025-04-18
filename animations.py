import time
import math
import pygame

# Animation class for smooth transitions
class Animation:
    def __init__(self, start_pos, end_pos, duration=0.3):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.duration = duration
        self.start_time = time.time()
        self.complete = False
    
    def update(self):
        elapsed = time.time() - self.start_time
        progress = min(elapsed / self.duration, 1.0)
        
        # Ease out cubic function for smooth animation
        progress = 1 - (1 - progress) ** 3
        
        if progress >= 1.0:
            self.complete = True
            return self.end_pos
        
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress
        
        return (x, y)

# Particle effect for captures
class ParticleSystem:
    def __init__(self, pos, color, count=20, lifetime=1.0):
        self.particles = []
        self.start_time = time.time()
        self.lifetime = lifetime
        self.alive = True
        
        for _ in range(count):
            angle = math.radians(pygame.time.get_ticks() % 360)
            speed = 0.5 + 1.5 * pygame.time.get_ticks() % 100 / 100
            
            self.particles.append({
                'pos': pos,
                'vel': (math.cos(angle) * speed, math.sin(angle) * speed),
                'size': 3 + pygame.time.get_ticks() % 5,
                'color': color,
                'alpha': 255
            })
    
    def update(self):
        if time.time() - self.start_time > self.lifetime:
            self.alive = False
            return
        
        progress = (time.time() - self.start_time) / self.lifetime
        
        for p in self.particles:
            p['pos'] = (p['pos'][0] + p['vel'][0], p['pos'][1] + p['vel'][1])
            p['vel'] = (p['vel'][0] * 0.95, p['vel'][1] * 0.95 + 0.1)  # Add gravity
            p['alpha'] = int(255 * (1 - progress))
    
    def draw(self, surface):
        for p in self.particles:
            if p['alpha'] > 0:
                s = pygame.Surface((p['size'], p['size']), pygame.SRCALPHA)
                s.fill((p['color'][0], p['color'][1], p['color'][2], p['alpha']))
                surface.blit(s, (int(p['pos'][0]), int(p['pos'][1])))

# Add a new CheckmateAnimation class
class CheckmateAnimation:
    def __init__(self, king_pos, square_size, duration=3.0):
        self.king_pos = king_pos  # (row, col)
        self.square_size = square_size
        self.duration = duration
        self.start_time = time.time()
        self.complete = False
        self.particles = []
        
        # Create crown effect particles around the king
        self.particle_systems = []
        center_x = king_pos[1] * square_size + square_size // 2
        center_y = king_pos[0] * square_size + square_size // 2
        
        # Create multiple particle systems for a more dramatic effect
        gold_color = (255, 215, 0)
        red_color = (255, 0, 0)
        
        self.particle_systems.append(ParticleSystem((center_x, center_y), gold_color, count=30, lifetime=duration))
        self.particle_systems.append(ParticleSystem((center_x, center_y), red_color, count=20, lifetime=duration))

    def update(self):
        elapsed = time.time() - self.start_time
        progress = min(elapsed / self.duration, 1.0)
        
        # Update all particle systems
        for ps in self.particle_systems[:]:
            ps.update()
            
        if progress >= 1.0:
            self.complete = True
            
        return progress
    
    def draw(self, surface):
        # Calculate center of king's position
        col, row = self.king_pos[1], self.king_pos[0] 
        center_x = col * self.square_size + self.square_size // 2
        center_y = row * self.square_size + self.square_size // 2
        
        # Pulse effect on the king's square
        elapsed = time.time() - self.start_time
        pulse = (math.sin(elapsed * 10) + 1) * 0.5  # Value between 0 and 1
        
        # Draw a pulsating highlight on the king's square
        size = int(self.square_size * (0.8 + pulse * 0.3))
        alpha = int(200 * (1 - elapsed / self.duration))
        
        highlight = pygame.Surface((size, size), pygame.SRCALPHA)
        highlight.fill((255, 0, 0, alpha))  # Red with fading transparency
        
        # Center the highlight
        highlight_pos = (center_x - size // 2, center_y - size // 2)
        surface.blit(highlight, highlight_pos)
        
        # Draw all particle systems
        for ps in self.particle_systems:
            ps.draw(surface)

        # Draw "CHECKMATE" text with scaling effect
        scale = 1.0 + math.sin(elapsed * 3) * 0.1  # Scale between 0.9 and 1.1
        font_size = int(36 * scale)
        font = pygame.font.SysFont('Arial', font_size, bold=True)
        
        # Create a glowing effect with multiple layers
        for offset in range(5, 0, -1):
            glow_color = (255, offset * 40, offset * 40, 150)
            text = font.render("CHECKMATE", True, glow_color)
            text_rect = text.get_rect(center=(center_x, center_y - 100))
            # Add slight offset for glow effect
            surface.blit(text, (text_rect.x - offset, text_rect.y - offset))
        
        # Main text
        text = font.render("CHECKMATE", True, (255, 255, 255))
        text_rect = text.get_rect(center=(center_x, center_y - 100))
        surface.blit(text, text_rect)
        
        # Draw "Game Over" text
        font_small = pygame.font.SysFont('Arial', 24, bold=True)
        game_over_text = font_small.render("Game Over", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(center_x, center_y - 60))
        surface.blit(game_over_text, game_over_rect)