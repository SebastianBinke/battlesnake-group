import heapq
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


def heuristic(a, b):
    # manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(start, target, game_state):
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']
    
    open_set = [(0, start)]  # priority queue (f_score, node)
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, target)}

    while open_set:
        current_f_score, current_node = heapq.heappop(open_set)

        if current_node == target:
            # reconstructing path
            path = []
            node = target
            while node in came_from:
                path.append(node)
                node = came_from[node]
            path.append(start)
            path.reverse()
            return path[1]  # return next move in path 

        x, y = current_node
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]

        for next_x, next_y in neighbors:
            neighbor = (next_x, next_y)

            if not (0 <= next_x < board_width and 0 <= next_y < board_height):
                continue  # out of bounds

            # collision check (snake) 
            is_safe = True
            for snake in game_state['board']['snakes']:
                for segment in snake['body']:
                    if (next_x, next_y) == (segment['x'], segment['y']):
                        is_safe = False
                        break
                if not is_safe:
                    break
            if not is_safe:
                continue

            tentative_g_score = g_score[current_node] + 1

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current_node
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, target)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None  # no path found


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
    if my_head["x"] == 0:  # left edge
        is_move_safe["left"] = False
    if my_head["x"] == board_width - 1:  # right edge
        is_move_safe["right"] = False
    if my_head["y"] == 0:  #  bottom edge
        is_move_safe["down"] = False
    if my_head["y"] == board_height - 1:  # top edge
        is_move_safe["up"] = False

    # prevent self collision 
    my_body = game_state['you']['body']
    
    # check every body segment
    for segment in my_body[1:]:  # Skip head
        # ceck possible collisions 
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
    
    # check every opponent snake
    for opponent in opponents:
        #skip our snake 
        if opponent["id"] == game_state["you"]["id"]:
            continue
            
        # checking every segment of opponent snake
        for segment in opponent["body"]:
            if my_head["x"] + 1 == segment["x"] and my_head["y"] == segment["y"]:
                is_move_safe["right"] = False
            if my_head["x"] - 1 == segment["x"] and my_head["y"] == segment["y"]:
                is_move_safe["left"] = False
            if my_head["y"] + 1 == segment["y"] and my_head["x"] == segment["x"]:
                is_move_safe["up"] = False
            if my_head["y"] - 1 == segment["y"] and my_head["x"] == segment["x"]:
                is_move_safe["down"] = False

    my_head = (game_state["you"]["body"][0]["x"], game_state["you"]["body"][0]["y"])

    # find closest food using A*
    food = game_state['board']['food']
    closest_food = None
    min_distance = float('inf')

    for f in food:
        food_coord = (f['x'], f['y'])
        dist = heuristic(my_head, food_coord)
        if dist < min_distance:
            min_distance = dist
            closest_food = food_coord

    if closest_food:
        next_move = a_star(my_head, closest_food, game_state)
        if next_move:
            x, y = next_move
            if x > my_head[0]:
                return {"move": "right"}
            elif x < my_head[0]:
                return {"move": "left"}
            elif y > my_head[1]:
                return {"move": "up"}
            elif y < my_head[1]:
                return {"move": "down"}

    # no food or no path --> floodfill
    safe_moves = []
    for move, isSafe in is_move_safe.items():
        if isSafe:
            safe_moves.append(move)

    if safe_moves:
        #check best possible move via floodfill
        best_move = None
        max_space = -1
        head_x = game_state["you"]["body"][0]["x"]
        head_y = game_state["you"]["body"][0]["y"]

        for move in safe_moves:
            next_x, next_y = head_x, head_y
            if move == "right":
                next_x += 1
            elif move == "left":
                next_x -= 1
            elif move == "up":
                next_y += 1
            elif move == "down":
                next_y -= 1

            available_space = floodfill(next_x, next_y, game_state)
            if available_space > max_space:
                max_space = available_space
                best_move = move

        return {"move": best_move}

    return {"move": "down"}

# food = game_state['board']['food']
def floodfill(start_x, start_y, game_state):
    to_visit = [(start_x, start_y)]  # Queue of tuples
    visited = {(start_x, start_y)}  # Set of tuples
    available_count = 1
    board_width = game_state['board']['width']
    board_height = game_state['board']['height']

    while to_visit:
        current = to_visit.pop(0)  # returning first cell in queue
        x, y = current  

        # check neighbors 
        neighbors = [
            (x+1, y),
            (x-1, y),
            (x, y+1),
            (x, y-1)
        ]
        
        for next_x, next_y in neighbors:
            # neighbor in bounds? 
            if 0 <= next_x < board_width and 0 <= next_y < board_height:
                # neighbor visited? 
                if (next_x, next_y) not in visited:
                    # neighbor safe? 
                    is_safe = True
                    
                    # check against own body
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
