from dlgo.gotypes import Point

def is_point_an_eye(board, point, color):
    if board.get_color(point):
        return False
    for neighbor in point.neighbors():
        if board.is_on_grid(neighbor):
            if board.get_color(neighbor) != color:
                return False
    
    friendly_corners = 0
    off_board_corners = 0
    corners = [
        Point(point.row - 1, point.col - 1),
        Point(point.row - 1, point.col + 1),
        Point(point.row + 1, point.col - 1),
        Point(point.row + 1, point.col + 1),
    ]
    for corner in corners:
        if board.is_on_grid(corner):
            if board.get_color(corner) == color:
                friendly_corners += 1
        else:
            off_board_corners += 1
        
        if off_board_corners > 0:
            return off_board_corners + friendly_corners == 4
        return friendly_corners >= 3