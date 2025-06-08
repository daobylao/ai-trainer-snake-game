import pygame
import random
import sys
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Game Constants
WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_WIDTH = WINDOW_SIZE // GRID_SIZE
GRID_HEIGHT = WINDOW_SIZE // GRID_SIZE
FPS = 60

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

class DataType(Enum):
    BASIC = ("Basic Data", GREEN, 1, 0.7)
    QUALITY = ("Quality Data", YELLOW, 3, 0.2)
    PREMIUM = ("Premium Data", RED, 10, 0.1)

@dataclass
class Position:
    x: int
    y: int
    
    def __iter__(self):
        return iter((self.x, self.y))
    
    def __eq__(self, other):
        if isinstance(other, tuple):
            return (self.x, self.y) == other
        return self.x == other.x and self.y == other.y

class GameState(Enum):
    PLAYING = "playing"
    GAME_OVER = "game_over"
    PAUSED = "paused"

class AISnake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        center_x, center_y = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.body = [Position(center_x, center_y)]
        self.direction = Position(1, 0)
        self.iq = 0
        self.growth_pending = 0
        
    def move(self):
        head = self.body[0]
        new_head = Position(head.x + self.direction.x, head.y + self.direction.y)
        self.body.insert(0, new_head)
        
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            self.body.pop()
    
    def grow(self, amount: int = 1):
        self.growth_pending += amount
        
    def change_direction(self, new_direction: Position):
        # Prevent reversing into itself
        if (new_direction.x != -self.direction.x or 
            new_direction.y != -self.direction.y):
            self.direction = new_direction
    
    def is_dead(self) -> bool:
        head = self.body[0]
        
        # Check wall collision (AI hallucination)
        if (head.x < 0 or head.x >= GRID_WIDTH or 
            head.y < 0 or head.y >= GRID_HEIGHT):
            return True
            
        # Check self collision (AI confusion)
        return head in self.body[1:]
    
    def get_brightness(self) -> int:
        return min(255, 50 + self.iq * 2)

class DataPoint:
    def __init__(self):
        self.respawn()
        
    def respawn(self, avoid_positions: List[Position] = None):
        if avoid_positions is None:
            avoid_positions = []
            
        # Find valid position
        attempts = 0
        while attempts < 100:  # Prevent infinite loop
            self.position = Position(
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            if self.position not in avoid_positions:
                break
            attempts += 1
        
        # Choose data type based on probability
        rand = random.random()
        cumulative_prob = 0
        
        for data_type in DataType:
            cumulative_prob += data_type.value[3]
            if rand <= cumulative_prob:
                self.type = data_type
                break
        else:
            self.type = DataType.BASIC
    
    @property
    def color(self):
        return self.type.value[1]
    
    @property
    def points(self):
        return self.type.value[2]
    
    @property
    def name(self):
        return self.type.value[0]

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("AI Training Snake - Grow Your Neural Network!")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        self.state = GameState.PLAYING
        self.high_score = self.load_high_score()
        self.flash_timer = 0
        
        self.reset_game()
    
    def reset_game(self):
        self.ai_snake = AISnake()
        self.data_point = DataPoint()
        self.data_point.respawn(self.ai_snake.body)
        self.state = GameState.PLAYING
        self.move_timer = 0
        self.last_move_time = pygame.time.get_ticks()
    
    def load_high_score(self) -> int:
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
                if self.state == GameState.PLAYING:
                    if event.key == pygame.K_UP:
                        self.ai_snake.change_direction(Position(0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.ai_snake.change_direction(Position(0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.ai_snake.change_direction(Position(-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.ai_snake.change_direction(Position(1, 0))
                    elif event.key == pygame.K_SPACE:
                        self.state = GameState.PAUSED
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.reset_game()
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING
                        self.last_move_time = pygame.time.get_ticks()
        
        return True
    
    def update(self):
        if self.state != GameState.PLAYING:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Calculate move speed based on IQ (gets faster as AI gets smarter)
        base_speed = 150  # milliseconds between moves
        speed_bonus = min(self.ai_snake.iq * 5, 100)  # max 100ms faster
        move_interval = max(50, base_speed - speed_bonus)
        
        if current_time - self.last_move_time >= move_interval:
            self.ai_snake.move()
            self.last_move_time = current_time
            
            # Check data consumption
            if self.ai_snake.body[0] == self.data_point.position:
                self.consume_data()
            
            # Check death
            if self.ai_snake.is_dead():
                self.game_over()
        
        self.flash_timer += 1
    
    def consume_data(self):
        points = self.data_point.points
        self.ai_snake.iq += points
        self.ai_snake.grow(1 if points <= 3 else 2)  # Premium data grows more
        
        # Respawn data away from snake
        self.data_point.respawn(self.ai_snake.body)
    
    def game_over(self):
        if self.ai_snake.iq > self.high_score:
            self.high_score = self.ai_snake.iq
            self.save_high_score()
        
        self.state = GameState.GAME_OVER
    
    def draw(self):
        self.screen.fill(BLACK)
        
        if self.state == GameState.PLAYING or self.state == GameState.PAUSED:
            self.draw_game()
            if self.state == GameState.PAUSED:
                self.draw_pause_overlay()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_game(self):
        # Draw grid (subtle)
        for x in range(0, WINDOW_SIZE, GRID_SIZE):
            pygame.draw.line(self.screen, (20, 20, 20), (x, 0), (x, WINDOW_SIZE))
        for y in range(0, WINDOW_SIZE, GRID_SIZE):
            pygame.draw.line(self.screen, (20, 20, 20), (0, y), (WINDOW_SIZE, y))
        
        # Draw snake with gradient effect
        brightness = self.ai_snake.get_brightness()
        
        for i, segment in enumerate(self.ai_snake.body):
            # Head is brightest, tail is darkest
            segment_brightness = brightness - (i * 5)
            segment_brightness = max(30, segment_brightness)
            
            color = (
                segment_brightness // 4,
                segment_brightness // 2,
                min(255, segment_brightness)
            )
            
            rect = pygame.Rect(
                segment.x * GRID_SIZE + 1,
                segment.y * GRID_SIZE + 1,
                GRID_SIZE - 2,
                GRID_SIZE - 2
            )
            
            pygame.draw.rect(self.screen, color, rect)
            
            # Add glow effect to head
            if i == 0:
                pygame.draw.rect(self.screen, WHITE, rect, 2)
        
        # Draw data point with flash effect for premium data
        data_rect = pygame.Rect(
            self.data_point.position.x * GRID_SIZE + 1,
            self.data_point.position.y * GRID_SIZE + 1,
            GRID_SIZE - 2,
            GRID_SIZE - 2
        )
        
        pygame.draw.rect(self.screen, self.data_point.color, data_rect)
        
        # Flash effect for high-value data
        if (self.data_point.points >= 10 and 
            self.flash_timer % 30 < 15):
            pygame.draw.rect(self.screen, WHITE, data_rect, 3)
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        # IQ Score (main score)
        iq_text = self.font_large.render(f"IQ: {self.ai_snake.iq}", True, WHITE)
        self.screen.blit(iq_text, (20, 20))
        
        # High Score
        if self.high_score > 0:
            high_text = self.font_medium.render(f"Best: {self.high_score}", True, LIGHT_GRAY)
            self.screen.blit(high_text, (20, 70))
        
        # Current data info
        data_info = f"{self.data_point.name} (+{self.data_point.points})"
        data_text = self.font_small.render(data_info, True, self.data_point.color)
        self.screen.blit(data_text, (20, WINDOW_SIZE - 60))
        
        # Snake length
        length_text = self.font_small.render(f"Neural Network Size: {len(self.ai_snake.body)}", True, GRAY)
        self.screen.blit(length_text, (20, WINDOW_SIZE - 30))
        
        # Controls hint
        controls_text = self.font_small.render("SPACE: Pause | Arrow Keys: Control", True, GRAY)
        text_rect = controls_text.get_rect()
        text_rect.topright = (WINDOW_SIZE - 20, 20)
        self.screen.blit(controls_text, text_rect)
    
    def draw_pause_overlay(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font_large.render("PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2))
        self.screen.blit(pause_text, text_rect)
        
        resume_text = self.font_medium.render("Press SPACE to resume", True, LIGHT_GRAY)
        text_rect = resume_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 50))
        self.screen.blit(resume_text, text_rect)
    
    def draw_game_over(self):
        # Background
        self.screen.fill(DARK_BLUE)
        
        # Game Over text
        game_over_text = self.font_large.render("TRAINING COMPLETE", True, WHITE)
        text_rect = game_over_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 100))
        self.screen.blit(game_over_text, text_rect)
        
        # Final IQ
        iq_text = self.font_medium.render(f"Final IQ: {self.ai_snake.iq}", True, YELLOW)
        text_rect = iq_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 50))
        self.screen.blit(iq_text, text_rect)
        
        # High score message
        if self.ai_snake.iq == self.high_score and self.high_score > 0:
            new_record_text = self.font_medium.render("NEW RECORD!", True, GREEN)
            text_rect = new_record_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2))
            self.screen.blit(new_record_text, text_rect)
        elif self.high_score > 0:
            best_text = self.font_medium.render(f"Best: {self.high_score}", True, LIGHT_GRAY)
            text_rect = best_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2))
            self.screen.blit(best_text, text_rect)
        
        # Restart instruction
        restart_text = self.font_medium.render("Press SPACE or ENTER to restart", True, WHITE)
        text_rect = restart_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 80))
        self.screen.blit(restart_text, text_rect)
        
        # Neural network size
        size_text = self.font_small.render(f"Max Neural Network Size: {len(self.ai_snake.body)}", True, GRAY)
        text_rect = size_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 120))
        self.screen.blit(size_text, text_rect)
    
    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Main entry point for the AI Training Snake game."""
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Game error: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()