import json
import logging
import random

import pygame

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Constants
WINDOW_SIZE = 600
GRID_SIZE = 3
CELL_SIZE = WINDOW_SIZE // GRID_SIZE
LINE_COLOR = (0, 0, 0)
X_COLOR = (200, 0, 0)
O_COLOR = (0, 0, 200)
BG_COLOR = (255, 255, 255)
FONT_SIZE = 80
BUTTON_COLOR = (0, 255, 0)
BUTTON_TEXT_COLOR = (255, 255, 255)

# File to store board states
STATE_FILE = "board_states.json"


def tuple_value(string: str) -> tuple:
    return tuple(map(lambda x: str(x.strip("'")), string.strip("()").split(", ")))


# Initialize board states
try:
    with open(STATE_FILE, "r") as file:
        cached_board_states = json.load(file)
        LOGGER.info(f"Loaded board states from {STATE_FILE}.")
except FileNotFoundError as e:
    LOGGER.warning(f"Board states file not found: {e}")
    cached_board_states: dict[str, dict] = {}


# Helper functions
def initialize_board() -> list[list[str]]:
    LOGGER.debug("Initializing empty board.")
    return [["." for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


def is_winning(board: list[list[str]], symbol: str) -> bool:
    for row in board:
        if all(cell == symbol for cell in row):
            LOGGER.debug(f"Player {symbol} wins by row.")
            return True

    for col in range(GRID_SIZE):
        if all(row[col] == symbol for row in board):
            LOGGER.debug(f"Player {symbol} wins by column.")
            return True

    if all(board[i][i] == symbol for i in range(GRID_SIZE)) or all(
        board[i][GRID_SIZE - 1 - i] == symbol for i in range(GRID_SIZE)
    ):
        LOGGER.debug(f"Player {symbol} wins by diagonal.")
        return True

    return False


def is_full(board: list[list[str]]) -> bool:
    full = all(cell != "." for row in board for cell in row)
    if full:
        LOGGER.debug("Board is full.")
    return full


def get_empty_cells(board: list[list[str]]) -> list[tuple[int, int]]:
    empty_cells = [
        (r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == "."
    ]
    LOGGER.debug(f"Empty cells: {empty_cells}")
    return empty_cells


def canonicalize_board(board: list[list[str]]) -> tuple[str, ...]:
    """Reduce a board to its canonical representation using symmetry."""
    flat_board = [cell for row in board for cell in row]
    rotations = [
        flat_board,
        [flat_board[i] for i in [6, 3, 0, 7, 4, 1, 8, 5, 2]],
        [flat_board[i] for i in [8, 7, 6, 5, 4, 3, 2, 1, 0]],
        [flat_board[i] for i in [2, 5, 8, 1, 4, 7, 0, 3, 6]],
    ]
    reflections = [
        [flat_board[i] for i in [2, 1, 0, 5, 4, 3, 8, 7, 6]],
        [flat_board[i] for i in [6, 7, 8, 3, 4, 5, 0, 1, 2]],
    ]
    all_symmetries = rotations + reflections
    canonical = min(tuple(symmetry) for symmetry in all_symmetries)
    LOGGER.debug(f"Canonical board representation: {canonical}")
    return canonical


def make_computer_move(
    board: list[list[str]], board_states: list[tuple[str, ...]], symbol: str
) -> tuple[int, int]:
    """Make the best move for the computer."""
    opponent = "X" if symbol == "O" else "O"
    LOGGER.debug(f"Computer is making a move as {symbol}.")

    # 1. Winning move
    for r, c in get_empty_cells(board):
        board[r][c] = symbol
        if is_winning(board, symbol):
            LOGGER.info(f"Computer wins by placing {symbol} at ({r}, {c}).")
            return r, c
        board[r][c] = "."

    # 2. Blocking move
    for r, c in get_empty_cells(board):
        board[r][c] = opponent
        if is_winning(board, opponent):
            board[r][c] = symbol
            LOGGER.info(f"Computer blocks opponent's winning move at ({r}, {c}).")
            return r, c
        board[r][c] = "."

    # 3. Look up state
    looped_board_states = cached_board_states
    not_found = True
    for board_state in board_states:
        try:
            looped_board_states = looped_board_states[str(board_state)]
        except KeyError:
            break
    else:
        not_found = False

    if not_found is False:
        # TODO
        ...

    # 4. Random move
    r, c = random.choice(get_empty_cells(board))
    board[r][c] = symbol
    LOGGER.info(f"Computer makes a random move at ({r}, {c}).")
    return r, c


def draw_board(screen: pygame.Surface, board: list[list[str]]) -> None:
    screen.fill(BG_COLOR)
    font = pygame.font.Font(None, FONT_SIZE)

    # Draw grid
    for i in range(1, GRID_SIZE):
        pygame.draw.line(
            screen, LINE_COLOR, (0, i * CELL_SIZE), (WINDOW_SIZE, i * CELL_SIZE), 2
        )
        pygame.draw.line(
            screen, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, WINDOW_SIZE), 2
        )

    # Draw symbols
    for r, row in enumerate(board):
        for c, cell in enumerate(row):
            if cell != ".":
                text = font.render(cell, True, X_COLOR if cell == "X" else O_COLOR)
                screen.blit(
                    text,
                    (c * CELL_SIZE + CELL_SIZE // 4, r * CELL_SIZE + CELL_SIZE // 4),
                )


def log_board_states(board_states: list[tuple[str, ...]], outcome) -> None:
    with open(STATE_FILE, "r") as file:
        cached_board_states = json.load(file)
        LOGGER.info(f"Loaded board states from {STATE_FILE}.")
    looped_board_state = cached_board_states
    for board_state in board_states:
        if str(board_state) not in looped_board_state:
            looped_board_state[str(board_state)] = {}
        looped_board_state = looped_board_state[str(board_state)]
    looped_board_state["outcome"] = outcome

    with open(STATE_FILE, "w") as file:
        json.dump(cached_board_states, file, indent=2)


def draw_reset_button(screen):
    font = pygame.font.Font(None, 36)
    button_rect = pygame.Rect(WINDOW_SIZE // 4, WINDOW_SIZE - 80, WINDOW_SIZE // 2, 50)
    pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
    text = font.render("Reset Game", True, BUTTON_TEXT_COLOR)
    screen.blit(
        text,
        (
            button_rect.x + (button_rect.width - text.get_width()) // 2,
            button_rect.y + 10,
        ),
    )
    return button_rect


# Main game loop
def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Tic Tac Toe")
    clock = pygame.time.Clock()

    board = initialize_board()
    player_symbol = "X"
    computer_symbol = "O"
    game_over = False
    board_states = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                LOGGER.info("User quit the game.")
                pygame.quit()
                return

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                r, c = y // CELL_SIZE, x // CELL_SIZE

                if board[r][c] == ".":
                    board[r][c] = player_symbol
                    board_states.append(canonicalize_board(board))

                    LOGGER.info(f"Player {player_symbol} makes a move at ({r}, {c}).")

                    if is_winning(board, player_symbol):
                        LOGGER.info(f"Player {player_symbol} wins!")
                        log_board_states(board_states, player_symbol)
                        game_over = True
                    elif is_full(board):
                        LOGGER.info("The board is full. It's a draw.")
                        log_board_states(board_states, ".")
                        game_over = True
                    else:
                        make_computer_move(board, board_states, computer_symbol)
                        board_states.append(canonicalize_board(board))
                        if is_winning(board, computer_symbol):
                            LOGGER.info(f"Computer {computer_symbol} wins!")
                            log_board_states(board_states, computer_symbol)
                            game_over = True

            if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                x, y = event.pos
                LOGGER.info(f"Player clicked... {x, y}")
                reset_button_rect = draw_reset_button(screen)
                if reset_button_rect.collidepoint(x, y):
                    LOGGER.info("Reset button clicked.")
                    board = initialize_board()  # Reset the board
                    game_over = False  # Reset the game over state
                    board_states = []
                    continue
                else:
                    LOGGER.info(
                        f"Player clicks randomly! {reset_button_rect.x, reset_button_rect.y}"
                    )

        draw_board(screen, board)

        if game_over:
            draw_reset_button(screen)  # Draw reset button when game is over

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
