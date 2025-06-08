import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Game settings
WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_WIDTH = WINDOW_SIZE // GRID_SIZE
GRID_HEIGHT = WINDOW_SIZE // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 215, 0)
RED = (255, 50, 50)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_BLUE = (0, 50, 100)

class AISnake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.body = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.direction = (1, 0)
        self.iq = 0
        self.growth_pending = 0
        
    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)
        
        # Only remove tail if not growing
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.body.pop()
        
    def grow(self, segments=1):
        self.growth_pending += segments
        
    def change_direction(self, new_direction):
        # Prevent reversing into self
        if (new_direction[0] != -self.direction[0] or 
            new_direction[1] != -self.direction[1]):
            self.direction = new_direction
        
    def is_dead(self):
        head = self.body[0]
        
        # Hit walls = AI hallucinated
        if (head[0] < 0 or head[0] >= GRID_WIDTH or 
            head[1] < 0 or head[1] >= GRID_HEIGHT):
            return True
            
        # Hit self = AI got confused
        if head in self.body[1:]:
            return True
            
        return False
    
    def get_brightness(self):
        """Calculate snake brightness based on IQ"""
        return min(255, 50 + self.iq * 2)

class DataPoint:
    def __init__(self):
        self.respawn()
        
    def respawn(self, avoid_positions=None):
        if avoid_positions is None:
            avoid_positions = []
            
        # Find valid position not overlapping snake
        attempts = 0
        while attempts < 100:
            self.x = random.randint(0, GRID_WIDTH-1)
            self.y = random.randint(0, GRID_HEIGHT-1)
            if (self.x, self.y) not in avoid_positions:
                break
            attempts += 1
            
        # Set data type with probabilities
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
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("AI Training Snake - Grow Your Neural Network!")
        
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game state
        self.high_score = self.load_high_score()
        self.paused = False
        self.game_over = False
        self.flash_timer = 0
        
        # Game objects
        self.ai_snake = AISnake()
        self.data_point = DataPoint()
        self.data_point.respawn(self.ai_snake.body)
        
        # Timing
        self.last_move_time = pygame.time.get_ticks()
        
    def load_high_score(self):
        """Load high score from file"""
        try:
            with open("high_score.txt", "r") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0
    
    def save_high_score(self):
        """Save high score to file"""
        try:
            with open("high_score.txt", "w") as f:
                f.write(str(self.high_score))
        except IOError:
            print("Could not save high score")
    
    def handle_input(self):
        """Handle keyboard input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if not self.game_over and not self.paused:
                    # Movement controls
                    if event.key == pygame.K_UP:
                        self.ai_snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.ai_snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.ai_snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
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
        """Restart the game"""
        self.ai_snake.reset()
        self.data_point.respawn(self.ai_snake.body)
        self.game_over = False
        self.paused = False
        self.last_move_time = pygame.time.get_ticks()
    
    def update(self):
        """Update game state"""
        if self.game_over or self.paused:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Calculate speed based on IQ (AI gets faster as it learns)
        base_speed = 150  # milliseconds between moves
        speed_increase = min(self.ai_snake.iq * 3, 100)  # max 100ms faster
        move_interval = max(60, base_speed - speed_increase)
        
        if current_time - self.last_move_time >= move_interval:
            self.ai_snake.move()
            self.last_move_time = current_time
            
            # Check if data was consumed
            if self.ai_snake.body[0] == (self.data_point.x, self.data_point.y):
                self.consume_data()
            
            # Check for death
            if self.ai_snake.is_dead():
                self.handle_game_over()
        
        self.flash_timer += 1
    
    def consume_data(self):
        """Handle data point consumption"""
        points = self.data_point.points
        self.ai_snake.iq += points
        
        # Premium data makes snake grow more
        growth = 2 if points >= 10 else 1
        self.ai_snake.grow(growth)
        
        # Respawn data in safe location
        self.data_point.respawn(self.ai_snake.body)
    
    def handle_game_over(self):
        """Handle game over logic"""
        # Check for new high score
        if self.ai_snake.iq > self.high_score:
            self.high_score = self.ai_snake.iq
            self.save_high_score()
            print(f"NEW HIGH SCORE: {self.ai_snake.iq} IQ!")
        else:
            print(f"Training Complete! Final IQ: {self.ai_snake.iq} (Best: {self.high_score})")
        
        self.game_over = True
    
    def draw(self):
        """Draw everything to screen"""
        self.screen.fill(BLACK)
        
        if not self.game_over:
            self.draw_game()
            if self.paused:
                self.draw_pause_overlay()
        else:
            self.draw_game_over_screen()
            
        pygame.display.flip()
    
    def draw_game(self):
        """Draw the main game"""
        # Draw subtle grid
        for x in range(0, WINDOW_SIZE, GRID_SIZE):
            pygame.draw.line(self.screen, (20, 20, 20), (x, 0), (x, WINDOW_SIZE))
        for y in range(0, WINDOW_SIZE, GRID_SIZE):
            pygame.draw.line(self.screen, (20, 20, 20), (0, y), (WINDOW_SIZE, y))
        
        # Draw snake with gradient brightness effect
        brightness = self.ai_snake.get_brightness()
        
        for i, segment in enumerate(self.ai_snake.body):
            # Each segment gets slightly dimmer
            segment_brightness = max(30, brightness - (i * 3))
            color = (
                segment_brightness // 4,
                segment_brightness // 2, 
                min(255, segment_brightness)
            )
            
            rect = pygame.Rect(
                segment[0] * GRID_SIZE + 1,
                segment[1] * GRID_SIZE + 1,
                GRID_SIZE - 2,
                GRID_SIZE - 2
            )
            
            pygame.draw.rect(self.screen, color, rect)
            
            # Head gets white outline
            if i == 0:
                pygame.draw.rect(self.screen, WHITE, rect, 2)
        
        # Draw data point
        data_rect = pygame.Rect(
            self.data_point.x * GRID_SIZE + 1,
            self.data_point.y * GRID_SIZE + 1,
            GRID_SIZE - 2,
            GRID_SIZE - 2
        )
        
        pygame.draw.rect(self.screen, self.data_point.color, data_rect)
        
        # Flash effect for premium data
        if (self.data_point.points >= 10 and 
            self.flash_timer % 30 < 15):
            pygame.draw.rect(self.screen, WHITE, data_rect, 3)
        
        self.draw_ui()
    
    def draw_ui(self):
        """Draw user interface elements"""
        # Main IQ score
        iq_text = self.font_large.render(f"IQ: {self.ai_snake.iq}", True, WHITE)
        self.screen.blit(iq_text, (20, 20))
        
        # High score
        if self.high_score > 0:
            high_text = self.font_medium.render(f"Best: {self.high_score}", True, LIGHT_GRAY)
            self.screen.blit(high_text, (20, 70))
        
        # Current data info
        data_info = f"{self.data_point.name} (+{self.data_point.points})"
        data_text = self.font_small.render(data_info, True, self.data_point.color)
        self.screen.blit(data_text, (20, WINDOW_SIZE - 60))
        
        # Neural network size
        size_text = self.font_small.render(f"Neural Network Size: {len(self.ai_snake.body)}", True, GRAY)
        self.screen.blit(size_text, (20, WINDOW_SIZE - 30))
        
        # Controls
        controls = "Arrow Keys: Move | SPACE: Pause"
        controls_text = self.font_small.render(controls, True, GRAY)
        text_rect = controls_text.get_rect()
        text_rect.topright = (WINDOW_SIZE - 20, 20)
        self.screen.blit(controls_text, text_rect)
    
    def draw_pause_overlay(self):
        """Draw pause overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font_large.render("TRAINING PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2))
        self.screen.blit(pause_text, text_rect)
        
        resume_text = self.font_medium.render("Press SPACE to resume", True, LIGHT_GRAY)
        text_rect = resume_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 50))
        self.screen.blit(resume_text, text_rect)
    
    def draw_game_over_screen(self):
        """Draw game over screen"""
        self.screen.fill(DARK_BLUE)
        
        # Title
        title_text = self.font_large.render("AI TRAINING COMPLETE", True, WHITE)
        text_rect = title_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 120))
        self.screen.blit(title_text, text_rect)
        
        # Final IQ
        final_iq_text = self.font_medium.render(f"Final IQ: {self.ai_snake.iq}", True, YELLOW)
        text_rect = final_iq_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 70))
        self.screen.blit(final_iq_text, text_rect)
        
        # High score status
        if self.ai_snake.iq == self.high_score and self.high_score > 0:
            record_text = self.font_medium.render("🎉 NEW RECORD! 🎉", True, GREEN)
            text_rect = record_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 20))
            self.screen.blit(record_text, text_rect)
        elif self.high_score > 0:
            best_text = self.font_medium.render(f"Personal Best: {self.high_score}", True, LIGHT_GRAY)
            text_rect = best_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 20))
            self.screen.blit(best_text, text_rect)
        
        # Neural network final size
        size_text = self.font_small.render(f"Max Neural Network Size: {len(self.ai_snake.body)} neurons", True, GRAY)
        text_rect = size_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 30))
        self.screen.blit(size_text, text_rect)
        
        # Restart instruction
        restart_text = self.font_medium.render("Press SPACE or ENTER to restart training", True, WHITE)
        text_rect = restart_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 80))
        self.screen.blit(restart_text, text_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

def main():
    """Main entry point"""
    try:
        print("🧠 AI Training Snake - Grow Your Neural Network!")
        print("=" * 50)
        print("Controls:")
        print("  Arrow Keys - Move your AI")
        print("  SPACE - Pause/Resume")
        print("  SPACE/ENTER - Restart after game over")
        print()
        print("Data Types:")
        print("  🟢 Basic Data - +1 IQ")
        print("  🟡 Quality Data - +3 IQ") 
        print("  🔴 Premium Data - +10 IQ (rare!)")
        print()
        print("Goal: Train your AI by consuming data!")
        print("Your neural network grows as your IQ increases!")
        print("=" * 50)
        
        game = Game()
        game.run()
        
    except Exception as e:
        print(f"Game error: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main() 