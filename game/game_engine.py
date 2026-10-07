import pygame
from .snake import Snake
from .food import Food

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cell_size = 20
        self.grid_width = width // self.cell_size
        self.grid_height = height // self.cell_size

        self.snake = Snake(
            self.grid_width // 2,
            self.grid_height // 2,
            self.cell_size
        )
        self.food = Food(
            self.grid_width,
            self.grid_height,
            self.cell_size
        )

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont("Arial", 60)
        self.final_score_font = pygame.font.SysFont("Arial", 35)
        self.instruction_font = pygame.font.SysFont("Arial", 25)

        self.moves_per_second = 8
        self._frame_counter = 0

        self.game_over = False

    def handle_keydown(self, key):
        # After Game Over, any key acknowledges the screen.
        # Replay functionality will be added in Task 3.
        if self.game_over:
            return True

        # Direction changes are applied immediately on key press.
        if key in (pygame.K_UP, pygame.K_w):
            self.snake.set_direction(0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.snake.set_direction(0, 1)
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.snake.set_direction(-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.snake.set_direction(1, 0)

        return False

    def handle_input(self):
        # Reserved for continuously-held-key input.
        pass

    def update(self):
        # Do not move the snake after Game Over.
        if self.game_over:
            return

        self._frame_counter += 1
        frames_per_move = max(1, 60 // self.moves_per_second)

        if self._frame_counter < frames_per_move:
            return

        self._frame_counter = 0

        self.snake.move()

        # Wall collision
        if self.snake.collides_with_wall(
            self.grid_width,
            self.grid_height
        ):
            self.game_over = True
            return

        # Self collision
        if self.snake.collides_with_self():
            self.game_over = True
            return

        # Food collision
        if self.snake.head_rect().colliderect(self.food.rect()):
            self.snake.grow()
            self.score += 1
            self.food.respawn(self.snake.body)

    def render(self, screen):
        # Draw food
        pygame.draw.rect(screen, RED, self.food.rect())

        # Draw snake
        for rect in self.snake.segment_rects():
            pygame.draw.rect(screen, GREEN, rect)

        # Draw score
        score_text = self.font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )
        screen.blit(score_text, (10, 10))

        # Game Over screen
        if self.game_over:
            game_over_text = self.game_over_font.render(
                "GAME OVER",
                True,
                RED
            )

            final_score_text = self.final_score_font.render(
                f"Final Score: {self.score}",
                True,
                WHITE
            )

            instruction_text = self.instruction_font.render(
                "Press any key to exit",
                True,
                WHITE
            )

            game_over_rect = game_over_text.get_rect(
                center=(self.width // 2, self.height // 2 - 60)
            )

            final_score_rect = final_score_text.get_rect(
                center=(self.width // 2, self.height // 2)
            )

            instruction_rect = instruction_text.get_rect(
                center=(self.width // 2, self.height // 2 + 50)
            )

            screen.blit(game_over_text, game_over_rect)
            screen.blit(final_score_text, final_score_rect)
            screen.blit(instruction_text, instruction_rect)
