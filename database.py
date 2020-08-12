import sqlite3

#class for accessing and inserting player stats into the database
#There is precisely one table called Player with the following attributes:
#-name
#-sp_score (single player score)
#-mp_scire (multi player score)
class db_connection():
    def __init__(self):
        #initiate the connection and the set the cursor,
        self.connection = sqlite3.connect("player_data.db")
        self.con = self.connection.cursor()
        #create the Player table if it does not exit
        self.con.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Player';")
        if self.con.fetchone()[0] != 1:
            self.con.execute("CREATE TABLE Player (name TEXT, sp_score INTEGER, mp_score INTEGER);")
            print("Player table created")
        self.connection.commit()
        print("successfully connected to db")

    #insert player name
    def insert_player(self, name):
        #check if player name exists
        self.con.execute("SELECT count(name) FROM Player WHERE Player.name = ?", (name,))
        if self.con.fetchall()[0][0] > 0:
            print("Duplicate player")
            return
        query = "INSERT INTO Player (name, sp_score, mp_score) VALUES (?, ?, ?);"
        self.con.execute(query, (name, 0, 0)) #intializes scores to 0
        print("successfully inserted player")
        self.connection.commit()

    #update existing player single player score
    def update_sp(self, name, sp_score):
        #check if the existing score is greater than the new score
        self.con.execute("SELECT sp_score FROM Player WHERE Player.name = ?", (name,))
        if int(self.con.fetchone()[0]) >= sp_score:
            return
        query = "UPDATE Player SET sp_score = ? WHERE name = ?"
        self.con.execute(query, (sp_score, name))
        print("successfully updated sp_score")
        self.connection.commit()

    #display list of top 10 high scores for single player
    def show_sp_score(self):
        self.con.execute("SELECT name, sp_score FROM Player ORDER BY sp_score DESC LIMIT 10;")
        return self.con.fetchall()

    #update existing multi player score
    def update_mp(self, name, mp_score):
        #check if existing score is greater than the new score
        self.con.execute("SELECT mp_score FROM Player WHERE Player.name = ?", (name,))
        if int(self.con.fetchone()[0]) >= mp_score:
            return
        query = "UPDATE Player SET mp_score = ? WHERE name = ?"
        self.con.execute(query, (mp_score, name))
        print("successfully updated mp_score")
        self.connection.commit()

    #display top 10 high scores for multi player
    def show_mp_score(self):
        self.con.execute("SELECT name, mp_score FROM Player ORDER BY mp_score DESC LIMIT 10;")
        return self.con.fetchall()

    #close the connection
    def disconnect(self):
        self.connection.close()
