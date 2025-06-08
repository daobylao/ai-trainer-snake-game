import pygame
import random
import sys
import math
import os
from enum import Enum

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Get user's screen resolution
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h

# Calculate optimal game size (use 90% of screen, maintain square aspect)
GAME_SIZE = min(int(SCREEN_WIDTH * 0.9), int(SCREEN_HEIGHT * 0.9))
GRID_SIZE = 20
GRID_WIDTH = GAME_SIZE // GRID_SIZE
GRID_HEIGHT = GAME_SIZE // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 215, 0)
RED = (255, 50, 50)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_BLUE = (0, 50, 100)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)

class AILevel(Enum):
    BASIC_CHATBOT = (0, "Basic Chatbot", (100, 100, 255))
    LANGUAGE_MODEL = (25, "Language Model", (150, 100, 255))
    MULTIMODAL_AI = (75, "Multimodal AI", (200, 100, 255))
    AGI_CANDIDATE = (150, "AGI Candidate", (255, 100, 200))
    SUPER_INTELLIGENCE = (300, "Super Intelligence", (255, 255, 255))

class Particle:
    def __init__(self, x, y, color, velocity=(0, 0)):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.life = 30
        self.max_life = 30
        
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            size = int(5 * (self.life / self.max_life))
            if size > 0:
                color = (*self.color[:3], alpha)
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.create_sounds()
        
    def create_sounds(self):
        """Create simple sound effects programmatically"""
        try:
            # Basic data sound (low pitch beep)
            self.sounds['basic'] = self.create_beep(220, 0.1)
            # Quality data sound (medium pitch)
            self.sounds['quality'] = self.create_beep(440, 0.15)
            # Premium data sound (high pitch with harmonics)
            self.sounds['premium'] = self.create_beep(880, 0.2)
            # Level up sound
            self.sounds['levelup'] = self.create_chord([440, 554, 659], 0.3)
            # Game over sound
            self.sounds['gameover'] = self.create_beep(110, 0.5)
        except:
            # If sound creation fails, use dummy sounds
            self.sounds = {key: None for key in ['basic', 'quality', 'premium', 'levelup', 'gameover']}
    
    def create_beep(self, frequency, duration):
        """Create a simple beep sound"""
        try:
            sample_rate = 22050
            frames = int(duration * sample_rate)
            arr = []
            for i in range(frames):
                wave = 4096 * math.sin(frequency * 2 * math.pi * i / sample_rate)
                arr.append([int(wave), int(wave)])
            sound = pygame.sndarray.make_sound(pygame.array.array('i', arr))
            return sound
        except:
            return None
    
    def create_chord(self, frequencies, duration):
        """Create a chord sound with multiple frequencies"""
        try:
            sample_rate = 22050
            frames = int(duration * sample_rate)
            arr = []
            for i in range(frames):
                wave = 0
                for freq in frequencies:
                    wave += 1024 * math.sin(freq * 2 * math.pi * i / sample_rate)
                arr.append([int(wave), int(wave)])
            sound = pygame.sndarray.make_sound(pygame.array.array('i', arr))
            return sound
        except:
            return None
    
    def play(self, sound_name):
        """Play a sound effect"""
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except:
                pass

class Achievement:
    def __init__(self, name, description, condition_func, icon="🏆"):
        self.name = name
        self.description = description
        self.condition_func = condition_func
        self.icon = icon
        self.unlocked = False
        self.show_notification = False
        self.notification_timer = 0

class AISnake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.body = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.direction = (1, 0)
        self.iq = 0
        self.growth_pending = 0
        self.level = AILevel.BASIC_CHATBOT
        self.data_consumed = 0
        self.premium_consumed = 0
        
    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)
        
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.body.pop()
        
    def grow(self, segments=1):
        self.growth_pending += segments
        
    def change_direction(self, new_direction):
        if (new_direction[0] != -self.direction[0] or 
            new_direction[1] != -self.direction[1]):
            self.direction = new_direction
        
    def is_dead(self):
        head = self.body[0]
        
        if (head[0] < 0 or head[0] >= GRID_WIDTH or 
            head[1] < 0 or head[1] >= GRID_HEIGHT):
            return True
            
        return head in self.body[1:]
    
    def get_brightness(self):
        return min(255, 50 + self.iq * 2)
    
    def update_level(self):
        old_level = self.level
        for level in AILevel:
            if self.iq >= level.value[0]:
                self.level = level
        return old_level != self.level

class DataPoint:
    def __init__(self):
        self.respawn()
        
    def respawn(self, avoid_positions=None):
        if avoid_positions is None:
            avoid_positions = []
            
        attempts = 0
        while attempts < 100:
            self.x = random.randint(0, GRID_WIDTH-1)
            self.y = random.randint(0, GRID_HEIGHT-1)
            if (self.x, self.y) not in avoid_positions:
                break
            attempts += 1
            
        rand = random.random()
        if rand < 0.7:
            self.type = "basic"
            self.color = GREEN
            self.points = 1
            self.name = "Basic Data"
        elif rand < 0.9:
            self.type = "quality" 
            self.color = YELLOW
            self.points = 3
            self.name = "Quality Data"
        else:
            self.type = "premium"
            self.color = RED
            self.points = 10
            self.name = "Premium Data"

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("AI Training Snake - Grow Your Neural Network!")
        
        # Calculate offset to center the game
        self.game_offset_x = (SCREEN_WIDTH - GAME_SIZE) // 2
        self.game_offset_y = (SCREEN_HEIGHT - GAME_SIZE) // 2
        
        self.clock = pygame.time.Clock()
        self.font_huge = pygame.font.Font(None, 72)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game state
        self.high_score = self.load_high_score()
        self.paused = False
        self.game_over = False
        self.flash_timer = 0
        self.screen_shake = 0
        
        # Effects
        self.particles = []
        self.sound_manager = SoundManager()
        
        # Achievements
        self.achievements = self.create_achievements()
        
        # Game objects
        self.ai_snake = AISnake()
        self.data_point = DataPoint()
        self.data_point.respawn(self.ai_snake.body)
        
        # Timing
        self.last_move_time = pygame.time.get_ticks()
        
    def create_achievements(self):
        achievements = [
            Achievement("First Steps", "Consume your first data", 
                       lambda s: s.data_consumed >= 1, "🐣"),
            Achievement("Smart Cookie", "Reach 25 IQ", 
                       lambda s: s.iq >= 25, "🍪"),
            Achievement("Data Scientist", "Consume 50 data points", 
                       lambda s: s.data_consumed >= 50, "🧪"),
            Achievement("Premium Hunter", "Consume 5 premium data", 
                       lambda s: s.premium_consumed >= 5, "💎"),
            Achievement("Language Model", "Reach Language Model level", 
                       lambda s: s.level.value[0] >= 25, "🗣️"),
            Achievement("Multimodal Master", "Reach Multimodal AI level", 
                       lambda s: s.level.value[0] >= 75, "🎭"),
            Achievement("AGI Candidate", "Reach AGI Candidate level", 
                       lambda s: s.level.value[0] >= 150, "🤖"),
            Achievement("Super Intelligence", "Reach Super Intelligence", 
                       lambda s: s.level.value[0] >= 300, "🌟"),
            Achievement("Neural Giant", "Grow to 50 neurons", 
                       lambda s: len(s.body) >= 50, "🧠"),
            Achievement("Speed Demon", "Survive at maximum speed", 
                       lambda s: s.iq >= 100, "⚡"),
        ]
        return achievements
        
    def load_high_score(self):
        try:
            with open("high_score.txt", "r") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0
    
    def save_high_score(self):
        try:
            with open("high_score.txt", "w") as f:
                f.write(str(self.high_score))
        except IOError:
            print("Could not save high score")
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                    
                if not self.game_over and not self.paused:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.ai_snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.ai_snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.ai_snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.ai_snake.change_direction((1, 0))
                    elif event.key == pygame.K_SPACE:
                        self.paused = True
                        
                elif self.paused:
                    if event.key == pygame.K_SPACE:
                        self.paused = False
                        self.last_move_time = pygame.time.get_ticks()
                        
                elif self.game_over:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.restart_game()
                        
        return True
    
    def restart_game(self):
        self.ai_snake.reset()
        self.data_point.respawn(self.ai_snake.body)
        self.game_over = False
        self.paused = False
        self.last_move_time = pygame.time.get_ticks()
        self.particles.clear()
        self.screen_shake = 0
        
        # Reset achievement notifications
        for achievement in self.achievements:
            achievement.show_notification = False
    
    def update(self):
        if self.game_over or self.paused:
            # Update particles even when paused/game over
            self.particles = [p for p in self.particles if p.life > 0]
            for particle in self.particles:
                particle.update()
            
            # Update achievement notifications
            for achievement in self.achievements:
                if achievement.show_notification:
                    achievement.notification_timer -= 1
                    if achievement.notification_timer <= 0:
                        achievement.show_notification = False
            return
            
        current_time = pygame.time.get_ticks()
        
        # Calculate speed based on IQ level
        base_speed = 150
        speed_increase = min(self.ai_snake.iq * 3, 100)
        move_interval = max(60, base_speed - speed_increase)
        
        if current_time - self.last_move_time >= move_interval:
            self.ai_snake.move()
            self.last_move_time = current_time
            
            # Check data consumption
            if self.ai_snake.body[0] == (self.data_point.x, self.data_point.y):
                self.consume_data()
            
            # Check for death
            if self.ai_snake.is_dead():
                self.handle_game_over()
        
        # Update effects
        self.flash_timer += 1
        if self.screen_shake > 0:
            self.screen_shake -= 1
            
        # Update particles
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
            
        # Update achievements
        self.check_achievements()
        for achievement in self.achievements:
            if achievement.show_notification:
                achievement.notification_timer -= 1
                if achievement.notification_timer <= 0:
                    achievement.show_notification = False
    
    def consume_data(self):
        points = self.data_point.points
        old_level = self.ai_snake.level
        
        self.ai_snake.iq += points
        self.ai_snake.data_consumed += 1
        
        if points >= 10:
            self.ai_snake.premium_consumed += 1
        
        # Level up check
        level_up = self.ai_snake.update_level()
        if level_up:
            self.sound_manager.play('levelup')
            self.screen_shake = 10
            # Create level up particles
            self.create_level_up_particles()
        else:
            # Play appropriate sound
            if points == 1:
                self.sound_manager.play('basic')
            elif points == 3:
                self.sound_manager.play('quality')
            else:
                self.sound_manager.play('premium')
                self.screen_shake = 5
        
        # Create consumption particles
        self.create_consumption_particles()
        
        # Growth
        growth = 2 if points >= 10 else 1
        self.ai_snake.grow(growth)
        
        # Respawn data
        self.data_point.respawn(self.ai_snake.body)
    
    def create_consumption_particles(self):
        """Create particles when consuming data"""
        x = self.game_offset_x + self.data_point.x * GRID_SIZE + GRID_SIZE // 2
        y = self.game_offset_y + self.data_point.y * GRID_SIZE + GRID_SIZE // 2
        
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.particles.append(Particle(x, y, self.data_point.color, velocity))
    
    def create_level_up_particles(self):
        """Create special particles for level up"""
        head = self.ai_snake.body[0]
        x = self.game_offset_x + head[0] * GRID_SIZE + GRID_SIZE // 2
        y = self.game_offset_y + head[1] * GRID_SIZE + GRID_SIZE // 2
        
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            color = self.ai_snake.level.value[2]
            self.particles.append(Particle(x, y, color, velocity))
    
    def check_achievements(self):
        """Check and unlock achievements"""
        for achievement in self.achievements:
            if not achievement.unlocked and achievement.condition_func(self.ai_snake):
                achievement.unlocked = True
                achievement.show_notification = True
                achievement.notification_timer = 180  # 3 seconds at 60 FPS
                self.sound_manager.play('levelup')
    
    def handle_game_over(self):
        if self.ai_snake.iq > self.high_score:
            self.high_score = self.ai_snake.iq
            self.save_high_score()
            print(f"🎉 NEW HIGH SCORE: {self.ai_snake.iq} IQ! 🎉")
        else:
            print(f"Training Complete! Final IQ: {self.ai_snake.iq} (Best: {self.high_score})")
        
        self.sound_manager.play('gameover')
        self.game_over = True
    
    def draw(self):
        # Apply screen shake
        shake_x, shake_y = 0, 0
        if self.screen_shake > 0:
            shake_x = random.randint(-self.screen_shake, self.screen_shake)
            shake_y = random.randint(-self.screen_shake, self.screen_shake)
        
        self.screen.fill(BLACK)
        
        if not self.game_over:
            self.draw_game(shake_x, shake_y)
            if self.paused:
                self.draw_pause_overlay()
        else:
            self.draw_game_over_screen()
        
        # Draw achievements notifications
        self.draw_achievement_notifications()
            
        pygame.display.flip()
    
    def draw_game(self, shake_x=0, shake_y=0):
        # Draw game border
        border_rect = pygame.Rect(
            self.game_offset_x - 2 + shake_x, 
            self.game_offset_y - 2 + shake_y,
            GAME_SIZE + 4, 
            GAME_SIZE + 4
        )
        pygame.draw.rect(self.screen, WHITE, border_rect, 2)
        
        # Draw grid
        for x in range(0, GAME_SIZE, GRID_SIZE):
            pygame.draw.line(self.screen, (20, 20, 20), 
                           (self.game_offset_x + x + shake_x, self.game_offset_y + shake_y), 
                           (self.game_offset_x + x + shake_x, self.game_offset_y + GAME_SIZE + shake_y))
        for y in range(0, GAME_SIZE, GRID_SIZE):
            pygame.draw.line(self.screen, (20, 20, 20), 
                           (self.game_offset_x + shake_x, self.game_offset_y + y + shake_y), 
                           (self.game_offset_x + GAME_SIZE + shake_x, self.game_offset_y + y + shake_y))
        
        # Draw snake with level colors
        brightness = self.ai_snake.get_brightness()
        level_color = self.ai_snake.level.value[2]
        
        for i, segment in enumerate(self.ai_snake.body):
            segment_brightness = max(30, brightness - (i * 3))
            
            # Blend level color with brightness
            color = (
                min(255, (level_color[0] * segment_brightness) // 255),
                min(255, (level_color[1] * segment_brightness) // 255),
                min(255, (level_color[2] * segment_brightness) // 255)
            )
            
            rect = pygame.Rect(
                self.game_offset_x + segment[0] * GRID_SIZE + 1 + shake_x,
                self.game_offset_y + segment[1] * GRID_SIZE + 1 + shake_y,
                GRID_SIZE - 2,
                GRID_SIZE - 2
            )
            
            pygame.draw.rect(self.screen, color, rect)
            
            if i == 0:  # Head
                pygame.draw.rect(self.screen, WHITE, rect, 2)
                # Draw eyes
                eye_size = 3
                eye1_pos = (rect.centerx - 4, rect.centery - 2)
                eye2_pos = (rect.centerx + 4, rect.centery - 2)
                pygame.draw.circle(self.screen, BLACK, eye1_pos, eye_size)
                pygame.draw.circle(self.screen, BLACK, eye2_pos, eye_size)
        
        # Draw data point
        data_rect = pygame.Rect(
            self.game_offset_x + self.data_point.x * GRID_SIZE + 1 + shake_x,
            self.game_offset_y + self.data_point.y * GRID_SIZE + 1 + shake_y,
            GRID_SIZE - 2,
            GRID_SIZE - 2
        )
        
        pygame.draw.rect(self.screen, self.data_point.color, data_rect)
        
        # Flash effect for premium data
        if (self.data_point.points >= 10 and 
            self.flash_timer % 30 < 15):
            pygame.draw.rect(self.screen, WHITE, data_rect, 3)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        self.draw_ui()
    
    def draw_ui(self):
        # AI Level and IQ (top center)
        level_text = self.font_large.render(f"{self.ai_snake.level.value[1]}", True, self.ai_snake.level.value[2])
        level_rect = level_text.get_rect(centerx=SCREEN_WIDTH//2, y=20)
        self.screen.blit(level_text, level_rect)
        
        iq_text = self.font_huge.render(f"IQ: {self.ai_snake.iq}", True, WHITE)
        iq_rect = iq_text.get_rect(centerx=SCREEN_WIDTH//2, y=level_rect.bottom + 10)
        self.screen.blit(iq_text, iq_rect)
        
        # High score (top left)
        if self.high_score > 0:
            high_text = self.font_medium.render(f"Best: {self.high_score}", True, LIGHT_GRAY)
            self.screen.blit(high_text, (20, 20))
        
        # Current data info (bottom left)
        data_info = f"{self.data_point.name} (+{self.data_point.points})"
        data_text = self.font_small.render(data_info, True, self.data_point.color)
        self.screen.blit(data_text, (20, SCREEN_HEIGHT - 100))
        
        # Neural network size
        size_text = self.font_small.render(f"Neural Network: {len(self.ai_snake.body)} neurons", True, GRAY)
        self.screen.blit(size_text, (20, SCREEN_HEIGHT - 70))
        
        # Data consumed
        consumed_text = self.font_small.render(f"Data Consumed: {self.ai_snake.data_consumed}", True, GRAY)
        self.screen.blit(consumed_text, (20, SCREEN_HEIGHT - 40))
        
        # Controls (top right)
        controls = ["ESC: Exit", "WASD/Arrows: Move", "SPACE: Pause"]
        for i, control in enumerate(controls):
            controls_text = self.font_small.render(control, True, GRAY)
            text_rect = controls_text.get_rect()
            text_rect.topright = (SCREEN_WIDTH - 20, 20 + i * 25)
            self.screen.blit(controls_text, text_rect)
        
        # Achievements counter (bottom right)
        unlocked_count = sum(1 for a in self.achievements if a.unlocked)
        achievement_text = self.font_small.render(f"Achievements: {unlocked_count}/{len(self.achievements)}", True, LIGHT_GRAY)
        text_rect = achievement_text.get_rect()
        text_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
        self.screen.blit(achievement_text, text_rect)
    
    def draw_achievement_notifications(self):
        """Draw achievement unlock notifications"""
        y_offset = 0
        for achievement in self.achievements:
            if achievement.show_notification:
                # Create notification background
                notification_height = 60
                notification_width = 400
                notification_rect = pygame.Rect(
                    SCREEN_WIDTH - notification_width - 20,
                    100 + y_offset,
                    notification_width,
                    notification_height
                )
                
                # Background with fade effect
                alpha = min(255, achievement.notification_timer * 2)
                notification_surf = pygame.Surface((notification_width, notification_height))
                notification_surf.set_alpha(alpha)
                notification_surf.fill((50, 50, 50))
                self.screen.blit(notification_surf, notification_rect)
                
                # Border
                pygame.draw.rect(self.screen, YELLOW, notification_rect, 2)
                
                # Achievement text
                title_text = self.font_medium.render(f"{achievement.icon} {achievement.name}", True, YELLOW)
                desc_text = self.font_small.render(achievement.description, True, WHITE)
                
                title_rect = title_text.get_rect(x=notification_rect.x + 10, y=notification_rect.y + 5)
                desc_rect = desc_text.get_rect(x=notification_rect.x + 10, y=notification_rect.y + 30)
                
                self.screen.blit(title_text, title_rect)
                self.screen.blit(desc_text, desc_rect)
                
                y_offset += 70
    
    def draw_pause_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font_huge.render("TRAINING PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(pause_text, text_rect)
        
        resume_text = self.font_medium.render("Press SPACE to resume", True, LIGHT_GRAY)
        text_rect = resume_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70))
        self.screen.blit(resume_text, text_rect)
    
    def draw_game_over_screen(self):
        self.screen.fill(DARK_BLUE)
        
        # Title
        title_text = self.font_huge.render("AI TRAINING COMPLETE", True, WHITE)
        text_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 200))
        self.screen.blit(title_text, text_rect)
        
        # Final level and IQ
        level_text = self.font_large.render(f"Final Level: {self.ai_snake.level.value[1]}", True, self.ai_snake.level.value[2])
        text_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 130))
        self.screen.blit(level_text, text_rect)
        
        final_iq_text = self.font_large.render(f"Final IQ: {self.ai_snake.iq}", True, YELLOW)
        text_rect = final_iq_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 90))
        self.screen.blit(final_iq_text, text_rect)
        
        # High score status
        if self.ai_snake.iq == self.high_score and self.high_score > 0:
            record_text = self.font_large.render("🎉 NEW RECORD! 🎉", True, GREEN)
            text_rect = record_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(record_text, text_rect)
        elif self.high_score > 0:
            best_text = self.font_medium.render(f"Personal Best: {self.high_score}", True, LIGHT_GRAY)
            text_rect = best_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(best_text, text_rect)
        
        # Stats
        stats = [
            f"Neural Network Size: {len(self.ai_snake.body)} neurons",
            f"Total Data Consumed: {self.ai_snake.data_consumed}",
            f"Premium Data Consumed: {self.ai_snake.premium_consumed}",
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.font_small.render(stat, True, GRAY)
            text_rect = stat_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20 + i * 30))
            self.screen.blit(stat_text, text_rect)
        
        # Achievements
        unlocked_count = sum(1 for a in self.achievements if a.unlocked)
        achievement_text = self.font_medium.render(f"Achievements Unlocked: {unlocked_count}/{len(self.achievements)}", True, YELLOW)
        text_rect = achievement_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120))
        self.screen.blit(achievement_text, text_rect)
        
        # Restart instruction
        restart_text = self.font_medium.render("Press SPACE or ENTER to restart training", True, WHITE)
        text_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 180))
        self.screen.blit(restart_text, text_rect)
        
        exit_text = self.font_small.render("Press ESC to exit", True, GRAY)
        text_rect = exit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 220))
        self.screen.blit(exit_text, text_rect)
    
    def run(self):
        running = True
        
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

def main():
    print("🧠 AI Training Snake - Enhanced Edition!")
    print("=" * 60)
    print("🎮 FULL SCREEN MODE - Optimized for your display!")
    print(f"📺 Resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    print(f"🎯 Game Size: {GAME_SIZE}x{GAME_SIZE}")
    print()
    print("✨ NEW FEATURES:")
    print("  🔊 Sound Effects - Audio feedback for actions")
    print("  💥 Particle Effects - Visual flair for data consumption")
    print("  🏆 Achievements - 10 achievements to unlock!")
    print("  📱 Screen Shake - Haptic-like feedback")
    print("  🎨 AI Level Colors - Visual progression through AI stages")
    print("  👁️  Snake Eyes - More personality for your AI")
    print("  ⌨️  WASD Support - Alternative controls")
    print()
    print("Controls:")
    print("  ⬆️⬇️⬅️➡️ Arrow Keys OR WASD - Move your AI")
    print("  SPACE - Pause/Resume")
    print("  ESC - Exit game")
    print("  SPACE/ENTER - Restart after game over")
    print()
    print("🎯 Goal: Reach Super Intelligence (300 IQ)!")
    print("=" * 60)
    print()
    
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"❌ Game error: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main() 