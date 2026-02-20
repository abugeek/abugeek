import os
import json
import random

BOARD_FILE = 'scripts/board.json'
README_FILE = 'README.md'

# Symbols for standard tictactoe
EMPTY = ' '
X = 'X'
O = 'O'

def get_image_url(val: str) -> str:
    if val == X:
        return "https://placehold.co/50x50/0D1117/53b14f?text=X"
    elif val == O:
        return "https://placehold.co/50x50/0D1117/e06c75?text=O"
    else:
        return "https://placehold.co/50x50/0D1117/FFFFFF?text=+"

def load_board() -> list[list[str]]:
    if os.path.exists(BOARD_FILE):
        with open(BOARD_FILE, 'r') as f:
            board_data: list[list[str]] = json.load(f)
            return board_data
    return [[EMPTY, EMPTY, EMPTY] for _ in range(3)]

def save_board(board: list[list[str]]) -> None:
    with open(BOARD_FILE, 'w') as f:
        json.dump(board, f)

def check_winner(board: list[list[str]]) -> str | None:
    # Rows and cols
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != EMPTY:
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != EMPTY:
            return board[0][i]
    # Diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != EMPTY:
        return board[0][2]
    return None

def is_full(board: list[list[str]]) -> bool:
    return all(cell != EMPTY for row in board for cell in row)

def make_computer_move(board: list[list[str]]) -> None:
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == EMPTY]
    if empty_cells:
        r, c = random.choice(empty_cells)
        board[r][c] = O

def generate_readme_board(board: list[list[str]], status_msg: str) -> str:
    lines: list[str] = []
    lines.append('<div align="center">')
    lines.append(f'  <p><strong>{status_msg}</strong></p>')
    lines.append('  <table>')
    for r in range(3):
        lines.append('    <tr>')
        for c in range(3):
            cell = board[r][c]  # type: ignore
            url = get_image_url(cell)
            if cell == EMPTY and "Wins" not in status_msg and "Draw" not in status_msg:
                # Issue link
                issue_link = f"https://github.com/abugeek/abugeek/issues/new?title=ttt%7C{r}%7C{c}&body=Just+click+Submit+new+issue+to+play+your+move!"
                lines.append(f'      <td><a href="{issue_link}"><img src="{url}" alt="empty"></a></td>')
            else:
                lines.append(f'      <td><img src="{url}" alt="{cell}"></td>')
        lines.append('    </tr>')
    lines.append('  </table>')
    if "Wins" in status_msg or "Draw" in status_msg:
        lines.append('  <br/><p><a href="https://github.com/abugeek/abugeek/issues/new?title=ttt%7Creset&body=Just+click+Submit+new+issue+to+reset!">🔄 Click here to reset the board and play again!</a></p>')
    lines.append('</div>')
    return '\n'.join(lines)

def update_readme(new_board_html: str) -> None:
    with open(README_FILE, 'r') as f:
        content: str = f.read()
    
    start_marker = "<!-- tictactoe_start -->"
    end_marker = "<!-- tictactoe_end -->"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        before = content[:start_idx + len(start_marker)]  # type: ignore
        after = content[end_idx:]  # type: ignore
        new_content = before + "\n" + new_board_html + "\n" + after
        with open(README_FILE, 'w') as f:
            f.write(new_content)

def main():
    title = os.environ.get('ISSUE_TITLE', '')
    if not title.startswith('ttt|'):
        return

    parts = title.split('|')
    cmd = parts[1]

    board = load_board()
    
    # Check if someone already won, prevent further moves until reset
    existing_winner = check_winner(board)
    if existing_winner or is_full(board):
        if cmd == 'reset':
            board = [[EMPTY, EMPTY, EMPTY] for _ in range(3)]
            save_board(board)
            html = generate_readme_board(board, "Your turn! You are X.")
            update_readme(html)
        return

    if cmd == 'reset':
        board = [[EMPTY, EMPTY, EMPTY] for _ in range(3)]
        save_board(board)
        html = generate_readme_board(board, "Your turn! You are X.")
        update_readme(html)
        return
        
    if len(parts) == 3:
        r, c = int(parts[1]), int(parts[2])
        if 0 <= r < 3 and 0 <= c < 3 and board[r][c] == EMPTY:
            board[r][c] = X
            
            winner = check_winner(board)
            if not winner and not is_full(board):
                make_computer_move(board)
                
            winner = check_winner(board)
            save_board(board)
            
            if winner == X:
                status = "🎉 You Win!"
            elif winner == O:
                status = "🤖 Computer Wins!"
            elif is_full(board):
                status = "🤝 It's a Draw!"
            else:
                status = "Your turn! You are X."
                
            html = generate_readme_board(board, status)
            update_readme(html)

if __name__ == "__main__":
    main()
