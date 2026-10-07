import pygame
from .snake import Snake
from .food import Food

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)
YELLOW = (255, 220, 0)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cell_size = 20
        self.grid_width = width // self.cell_size
        self.grid_height = height // self.cell_size

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont("Arial", 60)
        self.final_score_font = pygame.font.SysFont("Arial", 35)
        self.instruction_font = pygame.font.SysFont("Arial", 25)
        self.menu_font = pygame.font.SysFont("Arial", 32)

        # Difficulty speeds
        self.difficulties = {
            "Easy": 5,
            "Medium": 8,
            "Hard": 12
        }

        self.moves_per_second = self.difficulties["Medium"]
        self._frame_counter = 0

        # Game states:
        # "playing", "game_over", "difficulty"
        self.state = "playing"

        self.snake = None
        self.food = None

        self.reset_game()

    def reset_game(self):
        """Reset the snake, food, score and movement state."""
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
        self._frame_counter = 0
        self.state = "playing"

    def set_difficulty(self, difficulty):
        """Set the speed and start a completely new game."""
        if difficulty in self.difficulties:
            self.moves_per_second = self.difficulties[difficulty]
            self.reset_game()

    def handle_keydown(self, key):
        # ---------------------------------------------------------
        # GAME OVER SCREEN
        # ---------------------------------------------------------
        if self.state == "game_over":
            # Any key moves from Game Over to difficulty selection.
            self.state = "difficulty"
            return False

        # ---------------------------------------------------------
        # DIFFICULTY SELECTION SCREEN
        # ---------------------------------------------------------
        if self.state == "difficulty":
            if key in (pygame.K_e, pygame.K_1):
                self.set_difficulty("Easy")
            elif key in (pygame.K_m, pygame.K_2):
                self.set_difficulty("Medium")
            elif key in (pygame.K_h, pygame.K_3):
                self.set_difficulty("Hard")
            elif key in (pygame.K_q, pygame.K_ESCAPE):
                return True

            return False

        # ---------------------------------------------------------
        # PLAYING
        # ---------------------------------------------------------
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
        # Never move the snake unless the game is being played.
        if self.state != "playing":
            return

        self._frame_counter += 1

        frames_per_move = max(
            1,
            60 // self.moves_per_second
        )

        if self._frame_counter < frames_per_move:
            return

        self._frame_counter = 0

        self.snake.move()

        # Wall collision
        if self.snake.collides_with_wall(
            self.grid_width,
            self.grid_height
        ):
            self.state = "game_over"
            return

        # Self collision
        if self.snake.collides_with_self():
            self.state = "game_over"
            return

        # Food collision
        if self.snake.head_rect().colliderect(
            self.food.rect()
        ):
            self.snake.grow()
            self.score += 1
            self.food.respawn(self.snake.body)

    def render(self, screen):
        # ---------------------------------------------------------
        # PLAYING SCREEN
        # ---------------------------------------------------------
        if self.state == "playing":

            # Draw food
            pygame.draw.rect(
                screen,
                RED,
                self.food.rect()
            )

            # Draw snake
            for rect in self.snake.segment_rects():
                pygame.draw.rect(
                    screen,
                    GREEN,
                    rect
                )

            # Draw score
            score_text = self.font.render(
                f"Score: {self.score}",
                True,
                WHITE
            )

            screen.blit(
                score_text,
                (10, 10)
            )

        # ---------------------------------------------------------
        # GAME OVER SCREEN
        # ---------------------------------------------------------
        elif self.state == "game_over":

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
                "Press any key to continue",
                True,
                WHITE
            )

            game_over_rect = game_over_text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 - 70
                )
            )

            final_score_rect = final_score_text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2
                )
            )

            instruction_rect = instruction_text.get_rect(
                center=(
                    self.width // 2,
                    self.height // 2 + 60
                )
            )

            screen.blit(
                game_over_text,
                game_over_rect
            )

            screen.blit(
                final_score_text,
                final_score_rect
            )

            screen.blit(
                instruction_text,
                instruction_rect
            )

        # ---------------------------------------------------------
        # DIFFICULTY SELECTION SCREEN
        # ---------------------------------------------------------
        elif self.state == "difficulty":

            title_text = self.game_over_font.render(
                "PLAY AGAIN",
                True,
                YELLOW
            )

            easy_text = self.menu_font.render(
                "E - Easy",
                True,
                WHITE
            )

            medium_text = self.menu_font.render(
                "M - Medium",
                True,
                WHITE
            )

            hard_text = self.menu_font.render(
                "H - Hard",
                True,
                WHITE
            )

            exit_text = self.instruction_font.render(
                "Q / ESC - Exit",
                True,
                WHITE
            )

            title_rect = title_text.get_rect(
                center=(
                    self.width // 2,
                    120
                )
            )

            easy_rect = easy_text.get_rect(
                center=(
                    self.width // 2,
                    240
                )
            )

            medium_rect = medium_text.get_rect(
                center=(
                    self.width // 2,
                    300
                )
            )

            hard_rect = hard_text.get_rect(
                center=(
                    self.width // 2,
                    360
                )
            )

            exit_rect = exit_text.get_rect(
                center=(
                    self.width // 2,
                    450
                )
            )

            screen.blit(
                title_text,
                title_rect
            )

            screen.blit(
                easy_text,
                easy_rect
            )

            screen.blit(
                medium_text,
                medium_rect
            )

            screen.blit(
                hard_text,
                hard_rect
            )

            screen.blit(
                exit_text,
                exit_rect
            )