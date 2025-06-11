import random
import typing


# info is called when you create your Battlesnake on play.battlesnake.com
# and controls your Battlesnake's appearance
# TIP: If you open your Battlesnake URL in a browser you should see this data
def info() -> typing.Dict:
    print("INFO")

    return {
        "apiversion": "1",
        "author": "",  # TODO: Your Battlesnake Username
        "color": "#888888",  # TODO: Choose color
        "head": "default",  # TODO: Choose head
        "tail": "default",  # TODO: Choose tail
    }
    

# start is called when your Battlesnake begins a game
def start(game_state: typing.Dict):
    print("GAME START")


# end is called when your Battlesnake finishes a game
def end(game_state: typing.Dict):
    print("GAME OVER\n")


# move is called on every turn and returns your next move
# Valid moves are "up", "down", "left", or "right"
# See https://docs.battlesnake.com/api/example-move for available data
def move(game_state: typing.Dict) -> typing.Dict:

    is_move_safe = {"up": True, "down": True, "left": True, "right": True}

    # We've included code to prevent your Battlesnake from moving backwards
    my_head = game_state["you"]["body"][0]  # Coordinates of your head
    my_neck = game_state["you"]["body"][1]  # Coordinates of your "neck"

    if my_neck["x"] < my_head["x"]:  # Neck is left of head, don't move left
        is_move_safe["left"] = False

    elif my_neck["x"] > my_head["x"]:  # Neck is right of head, don't move right
        is_move_safe["right"] = False

    elif my_neck["y"] < my_head["y"]:  # Neck is below head, don't move down
        is_move_safe["down"] = False

    elif my_neck["y"] > my_head["y"]:  # Neck is above head, don't move up
        is_move_safe["up"] = False

    # Prevent your Battlesnake from moving out of bounds
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    # Check if snake is at the edges of the board
    if my_head["x"] == 0:  # At left edge
        is_move_safe["left"] = False
    if my_head["x"] == board_width - 1:  # At right edge
        is_move_safe["right"] = False
    if my_head["y"] == 0:  # At bottom edge
        is_move_safe["down"] = False
    if my_head["y"] == board_height - 1:  # At top edge
        is_move_safe["up"] = False

    # Prevent Battlesnake from colliding with itself
    my_body = game_state['you']['body']
    
    # Check each body segment
    for segment in my_body[1:]:  # Skip the head
        # Check if moving in any direction would result in collision
        if my_head["x"] + 1 == segment["x"] and my_head["y"] == segment["y"]:
            is_move_safe["right"] = False
        if my_head["x"] - 1 == segment["x"] and my_head["y"] == segment["y"]:
            is_move_safe["left"] = False
        if my_head["y"] + 1 == segment["y"] and my_head["x"] == segment["x"]:
            is_move_safe["up"] = False
        if my_head["y"] - 1 == segment["y"] and my_head["x"] == segment["x"]:
            is_move_safe["down"] = False

    # Prevent Battlesnake from colliding with other Battlesnakes
    opponents = game_state['board']['snakes']
    
    # Check each opponent snake
    for opponent in opponents:
        # Skip our own snake
        if opponent["id"] == game_state["you"]["id"]:
            continue
            
        # Check each segment of the opponent's body
        for segment in opponent["body"]:
            if my_head["x"] + 1 == segment["x"] and my_head["y"] == segment["y"]:
                is_move_safe["right"] = False
            if my_head["x"] - 1 == segment["x"] and my_head["y"] == segment["y"]:
                is_move_safe["left"] = False
            if my_head["y"] + 1 == segment["y"] and my_head["x"] == segment["x"]:
                is_move_safe["up"] = False
            if my_head["y"] - 1 == segment["y"] and my_head["x"] == segment["x"]:
                is_move_safe["down"] = False

    # Are there any safe moves left?
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    if len(safe_moves) == 0:
        print(f"MOVE {game_state['turn']}: No safe moves detected! Moving down")
        return {"move": "down"}

    # Calculate available space for each safe move
    best_move = safe_moves[0]
    max_space = 0

    for move in safe_moves:
        # Calculate the next position based on the move
        next_x, next_y = my_head["x"], my_head["y"]
        if move == "right":
            next_x += 1
        elif move == "left":
            next_x -= 1
        elif move == "up":
            next_y += 1
        elif move == "down":
            next_y -= 1

        # Get available space from this position
        available_space = get_available_space(next_x, next_y, game_state)
        
        # Update best move if this move leads to more space
        if available_space > max_space:
            max_space = available_space
            best_move = move

    print(f"MOVE {game_state['turn']}: {best_move}")
    return {"move": best_move}
 # food = game_state['board']['food']
# Helper Fuction 
def get_available_space(start_x, start_y, game_state):
    to_visit = [(start_x, start_y)]  # Queue of tuples
    visited = {(start_x, start_y)}  # Set of tuples
    available_count = 1
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    while to_visit:  # While there are cells to visit
        current = to_visit.pop(0)  # Get the first cell from the queue
        x, y = current  # Unpack coordinates
        
        # Check all four neighbors
        neighbors = [
            (x+1, y),  # right
            (x-1, y),  # left
            (x, y+1),  # up
            (x, y-1)   # down
        ]
        
        for next_x, next_y in neighbors:
            # Check if neighbor is within board bounds
            if 0 <= next_x < board_width and 0 <= next_y < board_height:
                # Check if neighbor hasn't been visited
                if (next_x, next_y) not in visited:
                    # Check if neighbor is safe (not occupied by any snake)
                    is_safe = True
                    
                    # Check against our own body
                    for segment in game_state["you"]["body"]:
                        if next_x == segment["x"] and next_y == segment["y"]:
                            is_safe = False
                            break
                    
                    # Check against opponent bodies
                    if is_safe:
                        for opponent in game_state["board"]["snakes"]:
                            if opponent["id"] == game_state["you"]["id"]:
                                continue
                            for segment in opponent["body"]:
                                if next_x == segment["x"] and next_y == segment["y"]:
                                    is_safe = False
                                    break
                    
                    if is_safe:
                        to_visit.append((next_x, next_y))
                        visited.add((next_x, next_y))
                        available_count += 1
    
    return available_count

# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})
