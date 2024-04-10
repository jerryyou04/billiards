from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os, cgi, sys, glob, shutil

import Physics
import math
import random

import json
import gzip

import random
def write_svg( table_id, table ):
    with open( "table%4.2f.svg" % table.time, "w" ) as fp:
        fp.write( table.svg() );


def nudge():
    return random.uniform( -1.5, 1.5 );


def setUp(player1, player2, game_name):
    table = Physics.Table()

    # Starting point for the triangle, kept at the center of the table
    start_x = Physics.TABLE_WIDTH / 2.0
    start_y = Physics.TABLE_WIDTH / 2.0

    # Total balls excluding the cue ball
    total_balls = 15
    # Ball IDs should start from the apex of the triangle and decrease
    ball_id = total_balls

    # Setup for balls in an inverted order within the triangular formation
    for row in range(5, 0, -1):  # Starts from the base row (5 balls) towards the apex
        for ball_in_row in range(row):
            x = start_x + (ball_in_row - row / 2.0) * (Physics.BALL_DIAMETER + 4.0) + nudge()
            y = start_y + (5 - row) * math.sqrt(3) / 2 * (Physics.BALL_DIAMETER + 4.0) + nudge()
            pos = Physics.Coordinate(x, y)
            sb = Physics.StillBall(ball_id, pos)
            table += sb
            ball_id -= 1  # Decrease the ball ID as we move upwards in the triangle

    # Cue ball positioning remains the same, towards the bottom of the setup
    pos = Physics.Coordinate(Physics.TABLE_WIDTH / 2.0 + random.uniform(-3.0, 3.0),
                             Physics.TABLE_LENGTH - Physics.TABLE_WIDTH / 2.0)
    sb = Physics.StillBall(0, pos)
    table += sb

    return table, table.svg()

def eightBall(table, playerTurn, lowNumbers):
    eight_ball_on_table = False
    player_balls_on_table = False

    # Check if the eight ball is still on the table
    for ball in table:
        if isinstance(ball, Physics.StillBall) and ball.obj.still_ball.number == 8:
            eight_ball_on_table = True
        elif isinstance(ball, Physics.RollingBall) and ball.obj.rolling_ball.number == 8:
            eight_ball_on_table = True

    # If eight ball is still on the table, no winner yet
    if eight_ball_on_table:
        return None  # Game continues

    # Determine the range of numbers for the current player's balls
    if playerTurn == lowNumbers:
        player_balls_range = range(1, 8)  # Low numbers for the player
    else:
        player_balls_range = range(9, 16)  # High numbers for the player

    # Check if any of the player's balls are still on the table
    for ball in table:
        if isinstance(ball, Physics.StillBall) and ball.obj.still_ball.number in player_balls_range:
            player_balls_on_table = True
            break
        elif isinstance(ball, Physics.RollingBall) and ball.obj.rolling_ball.number in player_balls_range:
            player_balls_on_table = True
            break

    # Determine the winner based on the presence of the player's balls on the table
    if player_balls_on_table:
        # If all of the current player's balls are still on the table, they lose
        winner = 2 if playerTurn == 1 else 1
    else:
        # If some of the current player's balls were sunk, they win
        winner = playerTurn

    return winner

        

class MyHandler(BaseHTTPRequestHandler):
    game = None
    game_name = None
    player1 = None
    player2 = None
    table = None
    lowNumbers = None
    playerTurn = None
    final_ball_sunk = None
    final_player_sunk = None
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        # Serve start.html
        if path == "/start.html":
            self.serve_file(path, "text/html")

        # Serve display.html
        elif path == "/display.html":  # Add this condition
            self.serve_file(path, "text/html")
        
        # Serve table-?.svg files
        elif path.startswith("/table") and path.endswith(".svg"):
            self.serve_file(path, "image/svg+xml")
        
        else:
            self.send_error(404, "File not found: %s" % self.path)
    
    def serve_file(self, path, content_type):
        # Split the path on '?' to ignore query parameters
        filepath = path.split('?')[0].lstrip('/')

        if filepath == "display.html":
            if os.path.isfile(filepath):
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    MyHandler.table, svg_content = setUp(MyHandler.player1, MyHandler.player2, MyHandler.game_name)  
                    content = content.replace('id="svgPlaceholder"></div>', f'{svg_content}</div>')
                    
                    # Convert the modified HTML content back to bytes
                    content_bytes = content.encode('utf-8')
                    
                    self.send_response(200)
                    self.send_header("Content-type", content_type)
                    self.send_header("Content-length", len(content_bytes))
                    self.end_headers()
                    self.wfile.write(content_bytes)
            else:
                self.send_error(404, "File not found: %s" % path)
        
        else:
            if os.path.isfile(filepath):
                with open(filepath, 'rb') as file:
                    content = file.read()
                    self.send_response(200)
                    self.send_header("Content-type", content_type)
                    self.send_header("Content-length", len(content))
                    self.end_headers()
                    self.wfile.write(content)
            else:
                self.send_error(404, "File not found: %s" % path)


    def do_POST(self):
        
        content_type = self.headers['Content-Type']
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        referer = self.headers.get('Referer')

        if content_type == 'application/x-www-form-urlencoded' and referer and "start.html" in referer:
            post_data = parse_qs(post_data.decode('utf-8'))
            MyHandler.player1 = post_data.get('player1', [None])[0]
            MyHandler.player2 = post_data.get('player2', [None])[0]
            MyHandler.game_name = post_data.get('game_name', [None])[0]

            if None in (MyHandler.player1, MyHandler.player2, MyHandler.game_name):
                self.send_error(400, "Missing player1, player2, or game_name")
                return

            print("Received request from start.html")
            

            MyHandler.game = Physics.Game( gameName=MyHandler.game_name, player1Name=MyHandler.player1, player2Name=MyHandler.player2 );
            MyHandler.playerTurn = random.choice([1, 2])
            print("Assigning random player turn: ", MyHandler.playerTurn)
            redirect_url = f"/display.html?player1={MyHandler.player1}&player2={MyHandler.player2}&game_name={MyHandler.game_name}&playerTurn={MyHandler.playerTurn}"
            self.send_response(303)  # '303 See Other' status code
            self.send_header('Location', redirect_url)
            self.end_headers()

        elif content_type == 'application/json':
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return
            
            if 'x' in data and 'y' in data and 'cueX' in data and 'cueY' in data:
                try:
                    x = float(data['x'])
                    y = float(data['y'])
                    cueX = float(data['cueX'])
                    cueY = float(data['cueY'])
                except ValueError:
                    self.send_error(400, "Invalid coordinate format")
                    return
                print(f"Processing pool shot at ({x}, {y}, {cueX}, {cueY})")
                
                diffX = cueX - x
                diffY = cueY - y

                # This can be adjusted based on the desired sensitivity or speed of the ball
                scale = 5

                # Calculate preliminary velocities
                velocityX = diffX * scale
                velocityY = diffY * scale

                if (velocityX > 10000):
                    velocityX = 10000
                if (velocityY > 10000):
                    velocityY = 10000
                if (velocityX < -10000):
                    velocityX = -10000
                if (velocityY < -10000):
                    velocityY = -10000
                
                cue_ball_posX = MyHandler.table.cueBall().obj.still_ball.pos.x
                cue_ball_posY = MyHandler.table.cueBall().obj.still_ball.pos.y

                svgString, MyHandler.table, ball_sunk = MyHandler.game.shoot(MyHandler.game_name, MyHandler.player1, MyHandler.table, velocityX, velocityY );

                print("ball sunk", ball_sunk)

                winner = eightBall(MyHandler.table, MyHandler.playerTurn, MyHandler.lowNumbers)
                
                if MyHandler.lowNumbers is None and ball_sunk is not None:  # Check if it's the first ball sunk that decides teams
                    MyHandler.final_ball_sunk = ball_sunk
                    MyHandler.final_player_sunk = MyHandler.playerTurn
                    if 1 <= ball_sunk <= 7:  # If the sunk ball is a low number
                        MyHandler.lowNumbers = MyHandler.playerTurn  # The current player takes lowNumbers
                    elif 9 <= ball_sunk <= 15:  # If the sunk ball is a high number
                        MyHandler.lowNumbers = 1 if MyHandler.playerTurn == 2 else 2  # The non-current player takes lowNumbers

                if ball_sunk is None:
                    MyHandler.playerTurn = 1 if MyHandler.playerTurn == 2 else 2
                
                if (MyHandler.table.cueBall() == None):
                    pos = Physics.Coordinate( cue_ball_posX,
                        cue_ball_posY);
                    sb  = Physics.StillBall( 0, pos );
                    MyHandler.table += sb

                    svgString.append(MyHandler.table.svg())

                final_winner = None
                if winner is not None:
                    string = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
                    "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
                    <svg width="700" height="1375" viewBox="0 0 700 1375"
                    xmlns="http://www.w3.org/2000/svg"
                    xmlns:xlink="http://www.w3.org/1999/xlink">
                        <rect width="700" height="1375" fill="#C0D0C0" />
                        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="Arial" font-size="48" fill="darkgreen">Game Has Ended</text>

                        <circle id="stillball" cx="350" cy="337.5" r="28" fill="YELLOW" />
                        <circle id="stillball" cx="319" cy="285.5" r="28" fill="BLUE" />
                        <circle id="stillball" cx="379" cy="283.5" r="28" fill="RED" />
                        <circle cx="352" cy="1037.5" r="28" fill="WHITE" />
                    </svg>
                    """
                    svgString.append(string)

                    final_winner = winner
                
                print("final winner", final_winner)
                # Step 1: Create a response object
                response_data = {
                    "svgString": svgString,
                    "playerTurn": MyHandler.playerTurn,
                    "lowNumbers": MyHandler.lowNumbers,
                    "ballSunk": MyHandler.final_ball_sunk,
                    "playerSunk": MyHandler.final_player_sunk,
                    "Winner": final_winner
                }
                print("final ball sunk", MyHandler.final_ball_sunk)
                # Step 2: Convert the dictionary to a JSON string
                response_json = json.dumps(response_data)

                print("length", len(response_json))

                gzip_response_json = gzip.compress(response_json.encode('utf-8'))

                # Step 3: Send the gzipped JSON string with the correct headers
                print("sending gzipped response data")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Encoding', 'gzip')
                self.end_headers()
                self.wfile.write(gzip_response_json)
                # svgJSON = json.dumps(svgString)

                # print("length", len(svgJSON))
                
                # gzip_svgJSON = gzip.compress(svgJSON.encode('utf-8'))
                # # Convert the response data to JSON and send it
                # print("sending gzipped svgs")
                # self.send_response(200)
                # self.send_header('Content-Type', 'application/json')
                # self.send_header('Content-Encoding', 'gzip')
                # self.end_headers()
                # self.wfile.write(gzip_svgJSON)

                # print("new length", len(gzip_svgJSON))
            else:
                self.send_error(400, "Invalid pool shot data")

        else:
            # Fallback error response if the content type doesn't match expectations
            self.send_error(400, "Unsupported Content-Type or Invalid Request Source")

    
 


        

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8085
    server_address = ('localhost', port)
    httpd = HTTPServer(server_address, MyHandler)
    print("Server listening on port:", port)
    httpd.serve_forever()



