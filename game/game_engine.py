import pygame
from pathlib import Path

from .snake import Snake
from .food import Food


# ---------------------------------------------------------
# Colors
# ---------------------------------------------------------

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)
YELLOW = (255, 220, 0)


class GameEngine:

    def __init__(self, width, height):

        # -------------------------------------------------
        # Screen / Grid
        # -------------------------------------------------

        self.width = width
        self.height = height

        self.cell_size = 20

        self.grid_width = width // self.cell_size
        self.grid_height = height // self.cell_size

        # -------------------------------------------------
        # Fonts
        # -------------------------------------------------

        self.font = pygame.font.SysFont(
            "Arial",
            30
        )

        self.game_over_font = pygame.font.SysFont(
            "Arial",
            60
        )

        self.final_score_font = pygame.font.SysFont(
            "Arial",
            35
        )

        self.instruction_font = pygame.font.SysFont(
            "Arial",
            25
        )

        self.menu_font = pygame.font.SysFont(
            "Arial",
            32
        )

        # -------------------------------------------------
        # Difficulty
        # -------------------------------------------------

        self.difficulties = {
            "Easy": 5,
            "Medium": 8,
            "Hard": 12
        }

        # Default difficulty
        self.moves_per_second = self.difficulties["Medium"]

        # -------------------------------------------------
        # Game State
        # -------------------------------------------------

        # Possible states:
        #
        # playing
        # game_over
        # difficulty
        #
        self.state = "playing"

        self._frame_counter = 0

        # -------------------------------------------------
        # Snake / Food
        # -------------------------------------------------

        self.snake = None
        self.food = None

        # -------------------------------------------------
        # Sound
        # -------------------------------------------------

        self.eat_sound = None
        self.game_over_sound = None

        self.load_sounds()

        # -------------------------------------------------
        # Start first game
        # -------------------------------------------------

        self.reset_game()

    # =====================================================
    # SOUND
    # =====================================================

    def load_sounds(self):

        try:

            project_root = Path(__file__).resolve().parent.parent

            eat_path = project_root / "sounds" / "eat.wav"
            game_over_path = (
                project_root / "sounds" / "game_over.wav"
            )

            self.eat_sound = pygame.mixer.Sound(
                str(eat_path)
            )

            self.game_over_sound = pygame.mixer.Sound(
                str(game_over_path)
            )

        except (pygame.error, FileNotFoundError):

            # Game continues normally if sound cannot
            # be loaded.
            self.eat_sound = None
            self.game_over_sound = None

    # =====================================================
    # RESET GAME
    # =====================================================

    def reset_game(self):

        # Create a completely new snake
        self.snake = Snake(
            self.grid_width // 2,
            self.grid_height // 2,
            self.cell_size
        )

        # Create new food
        self.food = Food(
            self.grid_width,
            self.grid_height,
            self.cell_size
        )

        # Reset score
        self.score = 0

        # Reset movement timing
        self._frame_counter = 0

        # Start playing
        self.state = "playing"

    # =====================================================
    # DIFFICULTY
    # =====================================================

    def set_difficulty(self, difficulty):

        if difficulty in self.difficulties:

            self.moves_per_second = (
                self.difficulties[difficulty]
            )

            # Selecting a difficulty starts a
            # completely new game.
            self.reset_game()

    # =====================================================
    # KEYBOARD INPUT
    # =====================================================

    def handle_keydown(self, key):

        # -------------------------------------------------
        # GAME OVER
        # -------------------------------------------------

        if self.state == "game_over":

            # Any key moves to difficulty selection.
            self.state = "difficulty"

            return False

        # -------------------------------------------------
        # DIFFICULTY SCREEN
        # -------------------------------------------------

        if self.state == "difficulty":

            # Easy
            if key in (
                pygame.K_e,
                pygame.K_1
            ):
                self.set_difficulty("Easy")

            # Medium
            elif key in (
                pygame.K_m,
                pygame.K_2
            ):
                self.set_difficulty("Medium")

            # Hard
            elif key in (
                pygame.K_h,
                pygame.K_3
            ):
                self.set_difficulty("Hard")

            # Exit
            elif key in (
                pygame.K_q,
                pygame.K_ESCAPE
            ):
                return True

            return False

        # -------------------------------------------------
        # PLAYING
        # -------------------------------------------------

        # Up / W
        if key in (
            pygame.K_UP,
            pygame.K_w
        ):
            self.snake.set_direction(
                0,
                -1
            )

        # Down / S
        elif key in (
            pygame.K_DOWN,
            pygame.K_s
        ):
            self.snake.set_direction(
                0,
                1
            )

        # Left / A
        elif key in (
            pygame.K_LEFT,
            pygame.K_a
        ):
            self.snake.set_direction(
                -1,
                0
            )

        # Right / D
        elif key in (
            pygame.K_RIGHT,
            pygame.K_d
        ):
            self.snake.set_direction(
                1,
                0
            )

        return False

    # =====================================================
    # CONTINUOUS INPUT
    # =====================================================

    def handle_input(self):

        # Not required for grid-based Snake.
        pass

    # =====================================================
    # UPDATE GAME
    # =====================================================

    def update(self):

        # Only update the snake during normal gameplay.
        if self.state != "playing":
            return

        # Increase frame counter
        self._frame_counter += 1

        # Calculate how many frames should pass
        # between snake movements.
        frames_per_move = max(
            1,
            60 // self.moves_per_second
        )

        # Wait until it is time for the next move.
        if self._frame_counter < frames_per_move:
            return

        self._frame_counter = 0

        # -------------------------------------------------
        # Move snake
        # -------------------------------------------------

        self.snake.move()

        # -------------------------------------------------
        # Wall Collision
        # -------------------------------------------------

        if self.snake.collides_with_wall(
            self.grid_width,
            self.grid_height
        ):

            self.state = "game_over"

            # Task 4: Game Over sound
            if self.game_over_sound:
                self.game_over_sound.play()

            return

        # -------------------------------------------------
        # Self Collision
        # -------------------------------------------------

        if self.snake.collides_with_self():

            self.state = "game_over"

            # Task 4: Game Over sound
            if self.game_over_sound:
                self.game_over_sound.play()

            return

        # -------------------------------------------------
        # Food Collision
        # -------------------------------------------------

        if self.snake.head_rect().colliderect(
            self.food.rect()
        ):

            # Grow snake
            self.snake.grow()

            # Increase score
            self.score += 1

            # Task 4: Food sound
            if self.eat_sound:
                self.eat_sound.play()

            # Spawn new food
            self.food.respawn(
                self.snake.body
            )

    # =====================================================
    # RENDER
    # =====================================================

    def render(self, screen):

        # =================================================
        # PLAYING SCREEN
        # =================================================

        if self.state == "playing":

            # -------------------------------------------------
            # Food
            # -------------------------------------------------

            pygame.draw.rect(
                screen,
                RED,
                self.food.rect()
            )

            # -------------------------------------------------
            # Snake
            # -------------------------------------------------

            for rect in self.snake.segment_rects():

                pygame.draw.rect(
                    screen,
                    GREEN,
                    rect
                )

            # -------------------------------------------------
            # Score
            # -------------------------------------------------

            score_text = self.font.render(
                f"Score: {self.score}",
                True,
                WHITE
            )

            screen.blit(
                score_text,
                (10, 10)
            )

        # =================================================
        # GAME OVER SCREEN
        # =================================================

        elif self.state == "game_over":

            # -------------------------------------------------
            # GAME OVER
            # -------------------------------------------------

            game_over_text = (
                self.game_over_font.render(
                    "GAME OVER",
                    True,
                    RED
                )
            )

            # -------------------------------------------------
            # Final Score
            # -------------------------------------------------

            final_score_text = (
                self.final_score_font.render(
                    f"Final Score: {self.score}",
                    True,
                    WHITE
                )
            )

            # -------------------------------------------------
            # Instruction
            # -------------------------------------------------

            instruction_text = (
                self.instruction_font.render(
                    "Press any key to continue",
                    True,
                    WHITE
                )
            )

            # -------------------------------------------------
            # Position
            # -------------------------------------------------

            game_over_rect = (
                game_over_text.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2 - 70
                    )
                )
            )

            final_score_rect = (
                final_score_text.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2
                    )
                )
            )

            instruction_rect = (
                instruction_text.get_rect(
                    center=(
                        self.width // 2,
                        self.height // 2 + 60
                    )
                )
            )

            # -------------------------------------------------
            # Draw
            # -------------------------------------------------

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

        # =================================================
        # DIFFICULTY SELECTION SCREEN
        # =================================================

        elif self.state == "difficulty":

            # -------------------------------------------------
            # Title
            # -------------------------------------------------

            title_text = (
                self.game_over_font.render(
                    "PLAY AGAIN",
                    True,
                    YELLOW
                )
            )

            # -------------------------------------------------
            # Options
            # -------------------------------------------------

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

            exit_text = (
                self.instruction_font.render(
                    "Q / ESC - Exit",
                    True,
                    WHITE
                )
            )

            # -------------------------------------------------
            # Position
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Draw
            # -------------------------------------------------

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