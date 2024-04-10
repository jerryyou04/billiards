import phylib;
import math;
import sqlite3
import os
################################################################################
# import constants from phylib to global varaibles
BALL_RADIUS   = phylib.PHYLIB_BALL_RADIUS;
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER
HOLE_RADIUS = phylib.PHYLIB_HOLE_RADIUS
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH
TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH
SIM_RATE = phylib.PHYLIB_SIM_RATE
VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON
DRAG = phylib.PHYLIB_DRAG
MAX_TIME = phylib.PHYLIB_MAX_TIME
MAX_OBJECTS = phylib.PHYLIB_MAX_OBJECTS

FRAME_INTERVAL = 0.01
# add more here
HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="700" height="1375" viewBox="-25 -25 1400 2750"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />"""

FOOTER = """</svg>\n"""

################################################################################
# the standard colours of pool balls
# if you are curious check this out:  
# https://billiards.colostate.edu/faq/ball/colors/

BALL_COLOURS = [ 
    "WHITE",
    "YELLOW",
    "BLUE",
    "RED",
    "PURPLE",
    "ORANGE",
    "GREEN",
    "BROWN",
    "BLACK",
    "LIGHTYELLOW",
    "LIGHTBLUE",
    "PINK",             # no LIGHTRED
    "MEDIUMPURPLE",     # no LIGHTPURPLE
    "LIGHTSALMON",      # no LIGHTORANGE
    "LIGHTGREEN",
    "SANDYBROWN",       # no LIGHTBROWN 
    ];

def balls_still_on_table(table):
        numbers_still_on_table = []
        for object in table:
            if isinstance(object, RollingBall):
                ball_number = object.obj.rolling_ball.number
                if 1 <= ball_number <= 15:
                    numbers_still_on_table.append(ball_number)
            elif isinstance(object, StillBall):
                ball_number = object.obj.still_ball.number
                if 1 <= ball_number <= 15:
                    numbers_still_on_table.append(ball_number)
                    #print(ball_number)
        
        return numbers_still_on_table

def ball_sunk_number(table, initial_still_on_table):
    # Get the current state of balls still on the table
    numbers_still_on_table = balls_still_on_table(table)
    
    # Identify the ball numbers that have been sunk since the initial state
    numbers_sunk = [number for number in initial_still_on_table if number not in numbers_still_on_table]
    
    # Return the first ball number that has been sunk (if any)
    if numbers_sunk:
        return numbers_sunk[0]  
    else:
        return None  # Return None if no balls have been sunk
################################################################################
class Coordinate( phylib.phylib_coord ):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
    pass;


################################################################################
class StillBall( phylib.phylib_object ):
    """
    Python StillBall class.
    """

    def __init__( self, number, pos ):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_STILL_BALL, 
                                       number, 
                                       pos, None, None, 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = StillBall;


    # add an svg method here
    def svg(self):
        if self.obj.still_ball.number == 0:
            return """ <circle id="cueball"  cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (
                self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.still_ball.number % len(BALL_COLOURS)]
            )

        return """ <circle id="stillball" cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (
            self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.still_ball.number % len(BALL_COLOURS)]
        )

###############################################################################
class RollingBall(phylib.phylib_object):
    def __init__(self, number, pos, vel, acc):
        phylib.phylib_object.__init__(self, 
                                      phylib.PHYLIB_ROLLING_BALL, 
                                      number, 
                                      pos, vel, acc, 
                                      0.0, 0.0);
        self.__class__ = RollingBall;

    def svg(self):
        if self.obj.rolling_ball.number == 0:
            return """ <circle id="cueball_rolling"  cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (
                self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.rolling_ball.number % len(BALL_COLOURS)]
            )
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (
            self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.rolling_ball.number % len(BALL_COLOURS)]
        )

################################################################################

class Hole(phylib.phylib_object):
    """
    Python Hole class.
    """
    
    def __init__(self, number, pos):
        """
        Constructor function for a hole. Requires hole number and position (x,y).
        """
        phylib.phylib_object.__init__(self, 
                                      phylib.PHYLIB_HOLE, 
                                      number, 
                                      pos, None, None, 
                                      0.0, 0.0)
        self.__class__ = Hole


    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="black" />\n""" % (self.obj.hole.pos.x, self.obj.hole.pos.y, HOLE_RADIUS)
###############################################################################
class HCushion(phylib.phylib_object):
    """
    Python Horizontal Cushion class.
    """
    
    def __init__(self, number, pos):
        """
        Constructor function for a horizontal cushion. Requires cushion number and position.
        Position might represent where the cushion starts or its center, depending on your phylib implementation.
        """
        phylib.phylib_object.__init__(self, 
                                      phylib.PHYLIB_HCUSHION, 
                                      number, 
                                      pos, None, None, 
                                      0.0, 0.0)
        self.__class__ = HCushion

    def svg(self):
        return """<rect width="1400" height="25" x="-25" y="%d" fill="darkgreen" />\n""" % (
            -25 if self.obj.hcushion.y == 0 else 2700
        )
###############################################################################
class VCushion(phylib.phylib_object):
    """
    Python Vertical Cushion class.
    """
    
    def __init__(self, number, pos):
        """
        Constructor function for a vertical cushion. Requires cushion number and position.
        Position might represent where the cushion starts or its center, depending on your phylib implementation.
        """
        phylib.phylib_object.__init__(self, 
                                      phylib.PHYLIB_VCUSHION, 
                                      number, 
                                      pos, None, None, 
                                      0.0, 0.0)
        self.__class__ = VCushion

    def svg(self):
        return """<rect width="25" height="2750" x="%d" y="-25" fill="darkgreen" />\n""" % (
            -25 if self.obj.vcushion.x == 0 else 1350
        )
###############################################################################

class Table( phylib.phylib_table ):
    """
    Pool table class.
    """

    def cueBall(self):
        """
        Find and return the cue ball (ball number 0) from the table.
        """
        cue_ball = None
        for ball in self:  # Assuming self can be iterated over to access the balls and other objects
            if isinstance(ball, StillBall):
                if ball.obj.still_ball.number == 0:  # Checking if the ball number is 0, which represents the cue ball
                    cue_ball = ball
            elif isinstance(ball, RollingBall):
                if ball.obj.rolling_ball.number == 0:
                    cue_ball = ball
        return cue_ball  # Return None if the cue ball is not found


    def roll(self, t):
        new = Table()
        for ball in self:
            if isinstance(ball, RollingBall):
                # create a new ball with the same number as the old ball
                new_ball = RollingBall(ball.obj.rolling_ball.number,
                                       Coordinate(0,0),
                                       Coordinate(0,0),
                                       Coordinate(0,0))
                # compute where it rolls to
                phylib.phylib_roll(new_ball, ball, t)
                # add ball to table
                new += new_ball
            if isinstance(ball, StillBall):
                # create a new ball with the same number and pos as the old ball
                new_ball = StillBall(ball.obj.still_ball.number,
                                    Coordinate(ball.obj.still_ball.pos.x,
                                               ball.obj.still_ball.pos.y))
                # add ball to table
                new += new_ball
        # return table
        return new

    def __init__( self ):
        """
        Table constructor method.
        This method call the phylib_table constructor and sets the current
        object index to -1.
        """
        phylib.phylib_table.__init__( self );
        self.current = -1;

    def __iadd__( self, other ):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object( other );
        return self;

    def __iter__( self ):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        return self;

    def __next__( self ):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1;  # increment the index to the next object
        if self.current < MAX_OBJECTS:   # check if there are no more objects
            return self[ self.current ]; # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1;    # reset the index counter
        raise StopIteration;  # raise StopIteration to tell for loop to stop

    def __getitem__( self, index ):
        """
        This method adds item retreivel support using square brackets [ ] .
        It calls get_object (see phylib.i) to retreive a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object( index ); 
        if result==None:
            return None;
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall;
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall;
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole;
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion;
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion;
        return result;

    def __str__( self ):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = "";    # create empty string
        result += "time = %6.1f;\n" % self.time;    # append time
        for i,obj in enumerate(self): # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i,obj);  # append object description
        return result;  # return the string

    def segment( self ):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """

        result = phylib.phylib_table.segment( self );
        if result:
            result.__class__ = Table;
            result.current = -1;
        return result;

    # add svg method here
    def svg(self):
        svg_elements = [HEADER]
        try:
            for obj in self:  # Utilizes the __iter__ method to loop through objects
                if obj is not None:
                    svg_elements.append(obj.svg())  # Only call svg() on non-None objects
        except StopIteration:
            pass  # Normal termination of the loop
        svg_elements.append(FOOTER)
        return "".join(svg_elements)

#################################################################################


class Database:

    def __init__(self, reset=False):
        self.db_path = "phylib.db"
        if reset and os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.conn = sqlite3.connect(self.db_path)

    def createDB(self):
        cur = self.conn.cursor()
        cur.execute(""" CREATE TABLE IF NOT EXISTS Ball
                (BALLID  INTEGER  NOT NULL,
                BALLNO   INTEGER NOT NULL,
                XPOS     FLOAT   NOT NULL,
                YPOS     FLOAT   NOT NULL,
                XVEL     FLOAT,
                YVEL     FLOAT,     
                PRIMARY KEY (BALLID));""")

        cur.execute(""" CREATE TABLE IF NOT EXISTS TTable
                        (TABLEID    INTEGER    NOT NULL,
                        TIME        FLOAT      NOT NULL,
                        PRIMARY KEY (TABLEID));""")

        cur.execute(""" CREATE TABLE IF NOT EXISTS BallTable
                        (BALLID   INTEGER NOT NULL,
                        TABLEID   INTEGER NOT NULL,
                        FOREIGN KEY (BALLID) REFERENCES Ball,
                        FOREIGN KEY (TABLEID) REFERENCES TTable);""")

        cur.execute(""" CREATE TABLE IF NOT EXISTS Game
                        (GAMEID INTEGER NOT NULL,
                        GAMENAME VARCHAR(64) NOT NULL,
                        PRIMARY KEY (GAMEID));""")


        cur.execute(""" CREATE TABLE IF NOT EXISTS Player
                        (PLAYERID INTEGER NOT NULL,
                        GAMEID INTEGER NOT NULL,
                        PLAYERNAME VARCHAR(64) NOT NULL,
                        PRIMARY KEY (PLAYERID),
                        FOREIGN KEY (GAMEID)  REFERENCES Game);""")

        cur.execute(""" CREATE TABLE IF NOT EXISTS Shot
                        (SHOTID INTEGER NOT NULL,
                        PLAYERID   INTEGER NOT NULL,
                        GAMEID INTEGER NOT NULL,
                        PRIMARY KEY (SHOTID)
                        FOREIGN KEY (PLAYERID) REFERENCES Player,
                        FOREIGN KEY (GAMEID) REFERENCES Game);""")

        cur.execute(""" CREATE TABLE IF NOT EXISTS TableShot
                        (TABLEID INTEGER NOT NULL,
                        SHOTID INTEGER NOT NULL,
                        FOREIGN KEY (TABLEID) REFERENCES TTable,
                        FOREIGN KEY (SHOTID) REFERENCES SHOT);""")
        self.conn.commit()

        cur.close()

    def readTable(self, tableID):
        tableID_sql = tableID + 1  # Adjusting for SQL numbering
        cur = self.conn.cursor()

        # Attempt to fetch the table's time attribute
        cur.execute("SELECT TIME FROM TTable WHERE TABLEID = ?", (tableID_sql,))
        
        time = cur.fetchall()
        
        # Fetch balls associated with this table
        cur.execute("""
            SELECT Ball.* FROM Ball 
            INNER JOIN BallTable ON Ball.BALLID = BallTable.BALLID 
            WHERE BallTable.TABLEID = ?
        """, (tableID_sql,))
        
        balls = cur.fetchall()
        table = Table() 

        if not balls:
            return None

        table.time = time[0][0]

        for ball in balls:
            ballID, ballNum, posX, posY, velX, velY = ball
            if velX is None or velY is None:
                table += (StillBall(ballNum, Coordinate(posX, posY)))
            else:
                speed = (velX**2 + velY**2)**0.5  # Magnitude of velocity vector
                if speed > VEL_EPSILON:
                    rb_acc_x = -(velX / speed) * DRAG
                    rb_acc_y = -(velY / speed) * DRAG
                else:
                    rb_acc_x = 0.0
                    rb_acc_y = 0.0 

                #Part 4
                table += (RollingBall(ballNum, Coordinate(posX,posY), Coordinate(velX,velY), Coordinate(rb_acc_x, rb_acc_y)))
        
        
        self.conn.commit()
        cur.close()
        return table

    
    def writeTable(self, table):

        cur = self.conn.cursor()        
        # Write table time to TTable and get TABLEID
        cur.execute("INSERT INTO TTable (TIME) VALUES (?)", (table.time,))
        table_id = cur.lastrowid
        
        # Write balls to Ball and BallTable

        for obj in table:
        # Determine if the object is a ball and extract its properties
            if isinstance(obj,RollingBall):
                cur.execute("INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?)",
                        (obj.obj.rolling_ball.number, obj.obj.rolling_ball.pos.x, obj.obj.rolling_ball.pos.y, obj.obj.rolling_ball.vel.x, obj.obj.rolling_ball.vel.y))
                ball_id = cur.lastrowid
                 # Link ball to the table in BallTable
                cur.execute("INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)", (ball_id, table_id))
            if isinstance(obj,StillBall):
                cur.execute("INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?)",
                            (obj.obj.still_ball.number, obj.obj.still_ball.pos.x, obj.obj.still_ball.pos.y, None, None))
                ball_id = cur.lastrowid
                 # Link ball to the table in BallTable
                cur.execute("INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)", (ball_id, table_id))
            
        self.conn.commit()
        cur.close()
        return table_id - 1  # Adjusting SQL TABLEID back to Python indexing

    def close(self):
        self.conn.commit()
        self.conn.close()

    def newShot(self, gameName, playerName):
        cur = self.conn.cursor()
        cur.execute("SELECT GAMEID FROM Game WHERE GAMENAME = ?", (gameName,))
        game_result = cur.fetchone()
        if not game_result:
            return None
        gameID = game_result[0]

        cur.execute("SELECT PLAYERID FROM Player WHERE PLAYERNAME = ? AND GAMEID = ?", (playerName, gameID))
        player_result = cur.fetchone()
        if not player_result:
            return None
        playerID = player_result[0]

        
        cur.execute("INSERT INTO Shot (GameID, PlayerID) VALUES (?, ?)", (gameID, playerID))
        self.conn.commit()
        shot_id = cur.lastrowid

        cur.close()
        return shot_id

    def getGame(self, gameID):
        cur = self.conn.cursor()
        cur.execute("SELECT GAMENAME FROM Game WHERE GAMEID = ?", (gameID + 1,))
        gameName = cur.fetchone()
        if gameName:
            gameName = gameName[0]
        else:
            return None  

        cur.execute("SELECT PLAYERNAME FROM Player WHERE GAMEID = ? ORDER BY PLAYERID ASC", (gameID,))
        players = cur.fetchall()
        playerNames = [player[0] for player in players] if players else (None, None)
        
        cur.close()
        return gameName, playerNames[0], playerNames[1] if len(playerNames) >= 2 else (None, None)

    def setGame(self, gameName, player1Name, player2Name):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO Game (GAMENAME) VALUES (?)", (gameName,))
        gameID = cur.lastrowid
        
        cur.execute("INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)", (gameID, player1Name))
        cur.execute("INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)", (gameID, player2Name))
        
        self.conn.commit()
        cur.close()
        return gameID

    def newShotTable(self, table_id, shot_id):
        cur = self.conn.cursor()  

        # Execute an INSERT command to add a record to the TableShot table
        cur.execute("INSERT INTO TableShot (TABLEID, SHOTID) VALUES (?, ?)", (table_id, shot_id))
        self.conn.commit()  # Commit the transaction to ensure it's saved 
        cur.close()
    


####################################################################################
class Game:
    def __init__(self, gameID=None, gameName=None, player1Name=None, player2Name=None):
        # Validate arguments
        if gameID is not None and (gameName is not None or player1Name is not None or player2Name is not None):
            raise TypeError("Invalid argument combination")
        if gameID is None and (gameName is None or player1Name is None or player2Name is None):
            raise TypeError("Name arguments cannot be None if gameID is None")
        
        #self.db = Database()
        # self.db.createDB()

        if gameID is not None:
            self.gameID = gameID  # Maybe don't add 1
            # Fetch game and player names from the database
            # self.gameName, self.player1Name, self.player2Name = self.db.getGame(self.gameID)
        else:
            # Set names directly
            self.gameName = gameName
            self.player1Name = player1Name
            self.player2Name = player2Name
            # Save new game to database and get gameID
            # self.gameID = self.db.setGame(gameName, player1Name, player2Name) - 1  # Adjust SQL ID back to Python indexing

       

    
    def shoot(self, gameName, playerName, table, xvel, yvel):
        cue_ball = None
        first_ball_sunk = None

        
        for object in table:
            if isinstance(object, StillBall):
                if object.obj.still_ball.number == 0:
                    cue_ball = object
 
        if cue_ball is None:
            return 
        
         # Retrieve and store the cue ball's current position
        xpos, ypos = cue_ball.obj.still_ball.pos.x, cue_ball.obj.still_ball.pos.y
        
        cue_ball.type = phylib.PHYLIB_ROLLING_BALL
        
        # Set the position and velocity attributes of the cue ball
        cue_ball.obj.rolling_ball.number = 0

        cue_ball.obj.rolling_ball.pos.x = xpos
        cue_ball.obj.rolling_ball.pos.y = ypos
        cue_ball.obj.rolling_ball.vel.x = xvel
        cue_ball.obj.rolling_ball.vel.y = yvel
 
        # Recalculate the acceleration parameters based on velocity
        speed = (xvel**2 + yvel**2)**0.5
        if speed > VEL_EPSILON:
            acc_x = -(xvel / speed) * DRAG
            acc_y = -(yvel / speed) * DRAG
        else:
            acc_x, acc_y = 0.0, 0.0
        
        # Set the acceleration attributes of the cue ball
        cue_ball.obj.rolling_ball.acc.x = acc_x
        cue_ball.obj.rolling_ball.acc.y = acc_y


        initial_time = table.time

        #shotID = self.db.newShot(gameName, playerName)

        svgString = []

        lastTable = None

        while True:
            segment_table = table.segment()  # Simulate the next segment of motion
            if segment_table is None:
                break  # Exit loop if there are no more segments
            lastTable = segment_table
            segment_duration = segment_table.time - table.time  # Calculate the segment's duration
            num_frames = math.floor(segment_duration / FRAME_INTERVAL)  # Determine the number of frames

            for frame in range(num_frames):
                
                frame_time = frame * FRAME_INTERVAL

                new_table = table.roll(frame_time)
                new_table.time = frame_time + table.time   # Ensure the new table's time is correctly set


                #table_id = self.db.writeTable(new_table)
                
                #shot_id = self.db.newShot(gameName, playerName)

                #self.db.newShotTable(table_id, shot_id)

                svgString.append(new_table.svg())

                
            
            # svgString.append(segment_table.svg())

            #print(balls_still_on_table(segment_table))

            initial_still_on_table = balls_still_on_table(table)
            
            table = segment_table  # Prepare for the next segment

            if (first_ball_sunk is None):
                first_ball_sunk = ball_sunk_number(table, initial_still_on_table)

        #print(table, first_ball_sunk)

        svgString.append(table.svg())

        return svgString, table, first_ball_sunk