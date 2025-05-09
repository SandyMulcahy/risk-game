from tkinter import *
from PIL import ImageTk, Image 
import sqlite3

import math
from random import randrange
import re

class Info():
    def __init__(s):
        s.userID = 0
        s.next_page = 'LoginPage'

        s.mapID = None
        s.saved_game_data = None

        #setup
        s.player_text = ''
        s.players = []
        s.colours = []
        s.bot = []

info = Info()

##################################################################################################################################
##################################################################################################################################
##################################################################################################################################

def LoginPage():

    def Close():
        info.next_page='Close'
        window.destroy()

    def LoginUser():

        username = E_Username.get()
        password = E_Password.get()
        if username == '' or password == '':
            E_Password.delete(0, END)
            return False

        hashed_password = Hash(password)

        DB_data = AccessDatabase(username)

        #Verify
        if DB_data[1] == hashed_password:
            info.userID = int(DB_data[0])
            
            #@ MODULE Menu
            info.next_page = 'MenuPage'
            window.destroy()

    def NewUser():
        username = E_Username.get()
        password = E_Password.get()
        if username == '' or password == '':
            return False
        
        hashed_password = Hash(password)
        
        #Check if username already exists
        if AccessDatabase(username) != False:
            return False
        
        #Regex checking
        disallowed_character = re.findall("[@#?!$%&*]", username)
        print(disallowed_character)
        if disallowed_character != []:
            return False

        db_path = "./DataBase/ProjectDb.db"
        connection = sqlite3.connect(db_path)
        db_cursor = connection.cursor()
        #insert new user
        sql = "INSERT INTO Users(username,password,games,wins,losses) VALUES (?,?,?,?,?)"
        db_cursor.execute(sql,[username,hashed_password,0,0,0])
        #find UserID
        sql = "SELECT UserID FROM Users WHERE Username = ?"
        db_cursor.execute(sql,[username])
        info.userID = int(db_cursor.fetchone()[0])

        #@ MODULE Menu
        window.destroy()
        info.next_page = 'MenuPage'

        connection.commit()
        connection.close()

    def AccessDatabase(username):
        #Fetch user data from database
        db_path = "./DataBase/ProjectDb.db"
        connection = sqlite3.connect(db_path)
        db_cursor = connection.cursor()

        sql = 'SELECT UserID, Password FROM Users WHERE Username = ?'
        db_cursor.execute(sql,[username])

        #If there is a user, verify password. If not, show NewUser button and halt.
        try:
            data = list(db_cursor.fetchone())
            connection.commit()
            connection.close()
            return data
        except:
            connection.commit()
            connection.close()
            return False


    def Hash(password):
        hash = 12345678
        for x in range(len(password)):
            character = password[x]
            ascii_code = ord(character)
            
            hash = hash + (ascii_code * 7)
            hash = hash // 3
            hash = hash + 987
            hash = hash * 5
            hash = hash - (1000% ascii_code )
            new_hash = ''
            for y in range(len(str(hash))):
                new_hash = new_hash + str(hash)[len(str(hash))-1-y]
            hash = int(new_hash)
            hash = hash - 98765
            hash = hash // 7

            if len(str(hash)) > 8:
                hash = int(str(hash)[0:8])
            elif len(str(hash)) < 8:
                add = 1
                while add != 0:
                    hash = int(str(hash) + str(add))
                    add += 1
                    if len(str(hash)) == 8:
                        add = 0
        
        return hash
                        
    ##################################################################################################################################

    window = Tk()
    #window.title('Login')

    #Start up fullscreen
    screen_width= window.winfo_screenwidth() 
    screen_height= window.winfo_screenheight()
    window.geometry("%dx%d" % (screen_width, screen_height))
    window.wm_attributes('-fullscreen', 'true')

    img = ImageTk.PhotoImage(Image.open('GreyBackground.jpeg'))
    canvas = Canvas(window, width=screen_width, height=screen_height)
    canvas.place(x=-1,y=-1)

    canvas.create_image(0,0,image=img,anchor='nw')
    canvas.create_text(screen_width/2,200, text='RISK', font = 'Ayuthaya 200 bold',fill ='#9A1111')
    'Zapfino, DIN'

    #Username
    canvas.create_text((screen_width)/2 - 100,463, text='USERNAME',font = 'Helvetica 20 bold',fill='white')
    E_Username = Entry(window,width=20)
    E_Username.place(x=(screen_width)/2,y=450)
    #Password
    canvas.create_text((screen_width)/2 - 100,513, text='PASSWORD',font = 'Helvetica 20 bold',fill='white')
    E_Password = Entry(window,show = '*',width=20)
    E_Password.place(x=(screen_width)/2,y=500)

    #Login
    B_Login = Button(window,text='LOGIN',font = 'Helvetica 20 bold', foreground = '#9A1111',highlightbackground='#444444',borderwidth=0,command=LoginUser)
    B_Login.place(x=(screen_width/2 + 100),y=550)
    #NewUser
    B_NewUser = Button(window,text='NEW USER',font = 'Helvetica 15 bold', foreground = '#9A1111',highlightbackground='#444444',borderwidth=0,width=7,command = NewUser)
    B_NewUser.place(x=(screen_width/2 + 100),y=600)

    #Close program
    B_Close = Button(window, text = 'X', font = 'Arial 30 bold', foreground='#9A1111', background = 'black',command=Close)
    B_Close.place(x=0,y=0)
    window.mainloop()

##################################################################################################################################
##################################################################################################################################
##################################################################################################################################


def MenuPage():

    def GoToSingleplayer():
        #Check if user has a current game first
        db_path = "./DataBase/ProjectDb.db"
        connection = sqlite3.connect(db_path)
        db_cursor = connection.cursor()

        sql = 'SELECT * FROM CurrentGame WHERE UserID = ?'
        db_cursor.execute(sql,(info.userID,))
        data = db_cursor.fetchone()

        if data == None:
            info.next_page = 'SetupSingleplayer'
        else:
            info.saved_game_data = data
            info.mapID = data[1]
            info.next_page = 'Gameplay'

        connection.commit()
        connection.close()
        window.destroy()

    def GoToMultiplayer():
        return False
        info.next_page = 'SetupMultiplayer'
        window.destroy()
    def GoToMapBuilder():
        info.next_page = 'MapBuilder'
        window.destroy()

    def LogOut():
        info.next_page = 'LoginPage'
        info.userID = 0
        window.destroy()

    def Close():
        info.next_page= 'Close'
        window.destroy()

    ##################################################################################################################################

    #Get Stats from Database
    db_path = "./DataBase/ProjectDb.db"
    connection = sqlite3.connect(db_path)
    db_cursor = connection.cursor()

    sql = 'SELECT Games, Wins, Losses FROM Users WHERE UserID = ?'

    db_cursor.execute(sql,(info.userID,))
    user_stats = db_cursor.fetchone()

    sql = 'SELECT Username, Games, Wins FROM Users'
    db_cursor.execute(sql)
    leaderboard_stats = []
    loop = True
    while loop:
        temp = db_cursor.fetchone()
        if temp == None:
            loop = False
        else:
            leaderboard_stats.append(list(temp))
        

    connection.commit()
    connection.close()

    info.players = []
    info.colours = []
    info.bot = []

    ##################################################################################################################################

    window = Tk()
    window.title('Menu')

    #Start up fullscreen
    screen_width= window.winfo_screenwidth() 
    screen_height= window.winfo_screenheight()
    window.geometry("%dx%d" % (screen_width, screen_height))
    window.wm_attributes('-fullscreen', 'true')

    img = ImageTk.PhotoImage(Image.open('GreyBackground.jpeg'))

    canvas = Canvas(window, width=screen_width, height=screen_height)
    canvas.place(x=-1,y=-1)

    canvas.create_image(0,0,image=img,anchor='nw')

    canvas.create_text(screen_width/2,200, text='RISK', font = 'Ayuthaya 200 bold',fill ='#9A1111')
    'Zapfino, DIN'

    #BUTTONS to go to modules
    B_SinglepLayer = Button(window, text = 'SINGLEPLAYER', font = 'Helvetica 20 bold', foreground = 'black', highlightbackground='#444444',borderwidth=0, command=GoToSingleplayer)
    B_SinglepLayer.place(x=(screen_width/2 - 92),y=400)

    B_MultipLayer = Button(window, text = 'MULTIPLAYER', font = 'Helvetica 20 bold', foreground = 'black', highlightbackground='#444444',borderwidth=0, command=GoToMultiplayer)
    B_MultipLayer.place(x=(screen_width/2 - 85),y=450)

    B_MapBuilder = Button(window, text = 'MAP BUILDER', font = 'Helvetica 20 bold', foreground = 'black', highlightbackground='#444444',borderwidth=0, command=GoToMapBuilder)
    B_MapBuilder.place(x=(screen_width/2 - 83),y=500)
    #Logout
    B_Logout = Button(window, text = 'LOG OUT', font = 'Helvetica 20 bold', foreground = '#9A1111', highlightbackground='#444444',borderwidth=0, command=LogOut)
    B_Logout.place(x=(screen_width/2 - 57),y=600)

    #Close program
    B_Close = Button(window, text = 'X', font = 'Arial 30 bold', foreground='#9A1111', background = 'black',command=Close)
    B_Close.place(x=0,y=0)

    #stats
    canvas.create_text(screen_width*3/4,435, text='Games Played: ' + str(user_stats[0]), font = 'Helvetica 20 bold',fill ='white')
    canvas.create_text(screen_width*3/4,465, text='Games Won:    ' + str(user_stats[1]), font = 'Helvetica 20 bold',fill ='white')
    canvas.create_text(screen_width*3/4,495, text='Games Lost:   ' + str(user_stats[2]), font = 'Helvetica 20 bold',fill ='white')

    window.mainloop()


##################################################################################################################################
##################################################################################################################################
##################################################################################################################################

def Setup():
    colours = ['orange','blue','red','green','pink','purple','yellow','brown']
    info.player_text = ['NAME','COLOUR','BOT?'] 

    #################################################################################################################################

    def Back():
        window.destroy()
        info.next_page = 'MenuPage'

    def Start():
        try:
            map_name = Li_Maps.get(Li_Maps.curselection())
        except:
            return False

        db_path = "./DataBase/ProjectDb.db"
        connection = sqlite3.connect(db_path)
        db_cursor = connection.cursor()

        sql = 'SELECT MapID, Polygons FROM Maps WHERE Name = ?'

        db_cursor.execute(sql,[map_name])
        data = db_cursor.fetchone()
        info.mapID = data[0]
        num_territories = data[1].count('/') + 1

        connection.commit()
        connection.close()
        
        if len(info.players) < 2 or len(info.players) > num_territories:
            return False
        
        if 'computer' in info.bot:
            return False
        
        info.next_page = 'Gameplay'
        window.destroy()
        
    def AddPlayer():
        try:
            name = E_PlayerName.get()
            colour = Li_Colours.get(Li_Colours.curselection())
            bot = Li_Bot.get(Li_Bot.curselection())
        except:
            return False
        
        if name == '' or name in info.players or colour in info.colours or bot == 'Computer':
            return False
        
        info.players.append(name)
        info.colours.append(colour)
        info.bot.append(bot)

        colours.remove(colour)
        Li_Colours.delete(0,END)
        for x in colours:
            Li_Colours.insert(END, x)


        info.player_text[0] += '\n'
        for x in range(min(len(name),10)):
            info.player_text[0] += name[x]
        info.player_text[1] += '\n' + colour
        info.player_text[2] += '\n' + bot

        L_Players.configure(text=info.player_text[0])
        L_Colours.configure(text=info.player_text[1])
        L_Bot.configure(text=info.player_text[2])


    def RemovePlayer():
        if len(info.players) == 0:
            return False
        
        info.players.pop()
        colour = info.colours.pop()
        info.bot.pop()
                
        L_Players.configure(text=info.player_text[0])
        L_Colours.configure(text=info.player_text[1])
        L_Bot.configure(text=info.player_text[2])

        colours.append(colour)
        Li_Colours.insert(END, colour)

    def Close():
        info.next_page = 'Close'
        window.destroy()
        
        
    #################################################################################################################################
    #Get Map Names

    db_path = "./DataBase/ProjectDb.db"
    connection = sqlite3.connect(db_path)
    db_cursor = connection.cursor()

    sql = 'SELECT Name FROM Maps'

    db_cursor.execute(sql)
    map_names = db_cursor.fetchall()

    connection.commit()
    connection.close()

    #################################################################################################################################

    def Import():
        info.players = ['Player1','Player2','Player3']
        info.colours = ['red','green','blue','yellow']
        info.bot = ['Human', 'Human', 'Human', 'Human']
        info.mapID = 3

    window = Tk()
    window.title('Setup')

    #Start up fullscreen
    screen_width= window.winfo_screenwidth() 
    screen_height= window.winfo_screenheight()
    window.geometry("%dx%d" % (screen_width, screen_height))
    window.wm_attributes('-fullscreen', 'true')

    img = ImageTk.PhotoImage(Image.open('GreyBackground.jpeg'))

    canvas = Canvas(window, width=screen_width, height=screen_height)
    canvas.place(x=-1,y=-1)

    canvas.create_image(0,0,image=img,anchor='nw')

    canvas.create_text(300,150, text='Setup', font = 'Ayuthaya 150 bold',fill ='#9A1111')

    #Proceed and Back
    B_Start = Button(window, text = 'START', font = 'Helvetica 20 bold', foreground = '#9A1111', highlightbackground='#444444',borderwidth=0,command=Start)
    B_Start.place(x=1200,y=700)

    B_Back = Button(window, text = 'BACK', font = 'Helvetica 20 bold', foreground = '#9A1111', highlightbackground='#444444',borderwidth=0, command=Back)
    B_Back.place(x=100,y=700)

    #Choose Map
    canvas.create_text(900,162, text='CHOOSE MAP', font = 'Ayuthaya 30 bold',fill ='white')

    Li_Maps = Listbox(window, height = 1)
    for x in map_names:
        Li_Maps.insert(END, x[0])
    Li_Maps.place(x=1050,y=150)

    #Add Players
    B_AddPlayer = Button(window, text = 'ADD PLAYER', font = 'Helvetica 20 bold', foreground = 'black', highlightbackground='#444444',borderwidth=0, command=AddPlayer)
    B_AddPlayer.place(x=1000,y=500)

    B_RemovePlayer = Button(window, text = 'REMOVE PLAYER', font = 'Helvetica 20 bold', foreground = 'black', highlightbackground='#444444',borderwidth=0,command=RemovePlayer)
    B_RemovePlayer.place(x=1000,y=550)

    E_PlayerName = Entry(window)
    E_PlayerName.place(x=1000,y=300)

    Li_Colours = Listbox(window,exportselection=False, height=1)
    for x in colours:
        Li_Colours.insert(END, x)
    Li_Colours.place(x=1000,y=350)

    Li_Bot = Listbox(window,exportselection=False, height=1)
    Li_Bot.insert(END, 'Human')
    Li_Bot.insert(END, 'Computer')
    Li_Bot.place(x=1000,y=400)

    L_Players = Label(window, text=info.player_text[0], font= 'TkFixedFont 20 bold', foreground='white',background='#222222')
    L_Players.place(x=100,y=300)
    L_Colours = Label(window, text=info.player_text[1], font= 'TkFixedFont 20 bold', foreground='white',background='#222222')
    L_Colours.place(x=200,y=300)
    L_Bot = Label(window, text=info.player_text[2], font= 'TkFixedFont 20 bold', foreground='white',background='#222222')
    L_Bot.place(x=300,y=300)

    B_import = Button(text='import',command=Import)
    #B_import.place(x=100,y=10)

    #Close program
    B_Close = Button(window, text = 'X', font = 'Arial 30 bold', foreground='#9A1111', background = 'black',command=Close)
    B_Close.place(x=0,y=0)

    window.mainloop()

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
####################
##### GAMEPLAY #####
####################

def Gameplay():

    class Map:

        coordinates = 0
        
        def __init__(s,map_data):
            
            s.name = map_data[0]

            s.territory_polygons = map_data[2]
            s.coordinates = map_data[3]
            s.label_coordinates = map_data[7]

            s.territory_names = map_data[1]
            s.player_in_territory = map_data[9]
            temp = []
            for x in s.territory_names:
                temp.append(1)
            s.troops_in_territory = temp

            s.region_names = map_data[4]
            s.region_bonuses = map_data[5]
            s.territory_regions = map_data[6]

            temp = []
            for x in range(len(s.territory_names)):
                temp.append(1)
            s.connections = []
            for x in range(len(s.territory_names)):
                s.connections.append(temp)

        def DisplayMap(s):
            canvas.delete("all")
            for x in range(len(s.territory_polygons)):
                polygon_coords = []
                for point in s.territory_polygons[x]:
                    polygon_coords.append(s.coordinates[point][0])
                    polygon_coords.append(s.coordinates[point][1])
                canvas.create_polygon(polygon_coords, fill=players[s.player_in_territory[x]].colour, outline='white')
                message = s.territory_names[x] + '\n' + ' ' * (len(s.territory_names[x]) // 2) + str(s.troops_in_territory[x]) 
                canvas.create_text(s.label_coordinates[x][0],s.label_coordinates[x][1], text=message,font = 'Helvetica 15 bold')
        
        def Deal(s):
            #put all territory indexes into a list
            unpicked_territories = []
            for x in range(len(s.territory_names)):
                unpicked_territories.append(x)

            while len(unpicked_territories) != 0:
                #each player gets a random territory index from the list, it is then removed. Repeat until none left
                for player_num in range(num_players):
                    if len(unpicked_territories) != 0:
                        num = randrange(0,len(unpicked_territories))
                        s.player_in_territory[unpicked_territories[num]] = player_num
                        unpicked_territories.pop(num)

            return s.player_in_territory

    #STARTING UP THIS INSTANCE OF GAME

    #IMPORT MAP DATA
    db_path = "./DataBase/ProjectDb.db"
    connection = sqlite3.connect(db_path)
    db_cursor = connection.cursor()
    sql = 'SELECT * FROM Maps WHERE MapID = ?'
    db_cursor.execute(sql,(info.mapID,))
    map_data = list(db_cursor.fetchone())
    map_data.pop(0)

    #get rid of the /
    for x in range(len(map_data)):
        if '/' in map_data[x]:
            if '[' in map_data[x]:
                map_data[x] = map_data[x].split('/')
                #split up brackets
                for y in range(len(map_data[x])):
                    map_data[x][y] = map_data[x][y][1:-1].split(', ')
                    #make them integers
                    for z in range(len(map_data[x][y])):
                        map_data[x][y][z] = int(map_data[x][y][z])
            else:
                map_data[x] = map_data[x].split('/')
        #changing region bonuses and territory regions into integers
        if x == 5 or x == 6:
            map_data[x] = list(map_data[x])
            for y in range(len(map_data[x])):
                map_data[x][y] = int(map_data[x][y])

    #create player in territory
    temp = []
    for x in range(len(map_data[1])):
        temp.append(-1)
    map_data.append(temp)

    connection.commit()
    connection.close()

    ################################################################################################################

    class Player:
        
        def __init__(s, player_num, name, colour, num_troops):
            s.player_num = player_num
            s.player_name = name
            s.colour = colour

            s.num_troops = num_troops
            s.cards = [0,0,0]

    ###########################################################################################################

    class Game:
        def __init__(s):
            s.next_action = 'move troops'

            s.player_turn = 0
            s.player_queue = []
            s.phase = 0
            s.stages = ['STAGE: DEPLOY', 'STAGE: ATTACK', 'STAGE: FORTIFY']

            s.troops_to_add = 0

            s.attacking = -1 #these are territories, not players
            s.defending = -1

            s.sending_troops = -1 #these are for fortify phase
            s.receiving_troops = -1

            s.card_recieved = False
            #QUEUE STRUCTURE FOR DECK
            s.deck = []
            temp = []
            for x in range(14):
                temp.append(0) #Infantry
                temp.append(1) #Cavalry
                temp.append(2) #Artillery
            #shuffle
            for x in range(len(temp)):
                num = randrange(0,len(temp))
                s.deck.append(temp[num])
                temp.pop(num)
            s.deck_front_pointer = 0
            s.deck_end_pointer = 41

        def ReceiveCard(s):
            card = s.deck[s.deck_front_pointer]
            players[s.player_turn].cards[card] += 1
            s.deck[s.deck_front_pointer] = -1
            s.deck_front_pointer = (s.deck_front_pointer + 1) % 42
        def ReturnCards(s,bonus):
            if bonus == 4:
                players[s.player_turn].cards[0] -= 3
                cards = [0,0,0]
            elif bonus == 6:
                players[s.player_turn].cards[1] -= 3
                cards = [1,1,1]
            elif bonus == 8:
                players[s.player_turn].cards[2] -= 3
                cards = [2,2,2]
            else:
                players[s.player_turn].cards[0] -= 1
                players[s.player_turn].cards[1] -= 1
                players[s.player_turn].cards[2] -= 1
                cards = [0,1,2]
            for card in cards:
                s.deck_end_pointer = (s.deck_end_pointer + 1) % 42
                s.deck[s.deck_end_pointer] = card
        
        def TurnReset(s):
            s.attacking = -1
            s.defending = -1
            L_Attacking.configure(text='Attacking: ')
            L_Defending.configure(text='Defending: ')

            s.sending_troops = -1
            s.receiving_troops = -1
            L_SendingTroops.configure(text='Sending: ')
            L_ReceivingTroops.configure(text='Receiving: ')

            Li_Dice.delete(0,END)
            Li_MoveTroops.delete(0,END)
            L_DiceRolled.configure(text='')

    game = Game()

    ###########################################################################################################

    def WhichArea(click,coordinates,polygons):
        smallest_distance = 1000
        for i in range(len(polygons)):
            for j in range(len(polygons[i])):
                coord1 = coordinates[polygons[i][j]]
                try:
                    coord2 = coordinates[polygons[i][j+1]]
                except:
                    coord2 = coordinates[polygons[i][0]]
                gradient = (coord1[1]-coord2[1])/(coord1[0]-coord2[0])
                k = coord1[1] - gradient * coord1[0]

                opposite_gradient = -1 / gradient
                opposite_k = click[1] - opposite_gradient * click[0]

                closest_x = (k-opposite_k)/(opposite_gradient-gradient)
                if (closest_x > coord1[0] and closest_x < coord2[0]) or (closest_x < coord1[0] and closest_x > coord2[0]):
                    closest_y = gradient * closest_x + k
                    distance = math.sqrt((closest_x - click[0])**2 + (closest_y - click[1])**2)
                    
                    if distance < smallest_distance:
                        try:
                            points = [polygons[i][j],polygons[i][j+1]]
                        except:
                            points = [polygons[i][j],polygons[i][0]]
                        best_line_gradient = gradient
                        best_line_k = k
                        smallest_distance = distance
                        best_closest_x = closest_x
                        best_closest_y = closest_y
        
        #canvas.create_line(click[0],click[1],best_closest_x,best_closest_y)

        #Finding next points along
        if coordinates[points[0]][1] < coordinates[points[1]][1]:
            higher_point = points[0]
            lower_point = points[1]
        else:
            higher_point = points[1]
            lower_point = points[0]

        #Find potential polygons that it could be, along with their next points
        potential_polygons = []
        for polygon in polygons:
            for x in range(len(polygon)):
                #one direction
                try:
                    if polygon[x] == lower_point and polygon[x+1] == higher_point:
                        potential_polygons.append([polygon,polygon[x+2]])
                except:
                    try:
                        if polygon[x] == lower_point and polygon[x+1] == higher_point:
                            potential_polygons.append([polygon,polygon[0]])   
                    except:
                        if polygon[x] == lower_point and polygon[0] == higher_point:
                            potential_polygons.append([polygon,polygon[1]])
                #other direction
                try:
                    if polygon[x] == lower_point and polygon[x-1] == higher_point:
                        potential_polygons.append([polygon,polygon[x-2]])
                except:
                    try:
                        if polygon[x] == lower_point and polygon[x-1] == higher_point:
                            potential_polygons.append([polygon,polygon[len(polygon)-1]])
                    except:
                        if polygon[x] == lower_point and polygon[len(polygon)-1] == higher_point:
                            potential_polygons.append([polygon,polygon[len(polygon)-2]])

        #Matrix rotation algorithm to check if it's left or right
        rotating_point = [click[0] - best_closest_x,click[1] - best_closest_y]
        angle = math.pi/2 - math.atan(best_line_gradient)
        if angle > math.pi/2:
            angle = angle - math.pi
        new_point = [math.cos(angle) * rotating_point[0] - math.sin(angle) * rotating_point[1], math.sin(angle) * rotating_point[0] + math.cos(angle) * rotating_point[0]]
        if new_point[0] > 0: 
            right = True
        else:
            right = False
        
        # matrix thing again to see which side is the correct one. Finds the next point attached to highest point on line and  sees which is
        for potential_polygon in potential_polygons:
            next_point = potential_polygon[1]
            gradient = (coordinates[next_point][1] - coordinates[higher_point][1])/(coordinates[next_point][0] - coordinates[higher_point][0])
            matrix_thing = math.cos(angle) * (coordinates[next_point][0]-coordinates[higher_point][0]) - math.sin(angle) * (coordinates[next_point][1] - coordinates[higher_point][1])
            if right == (matrix_thing > 0):
                for x in range(len(polygons)):
                    if polygons[x] == potential_polygon[0]:
                        return x
        #? this wont work if they share 2 lines. it will need to loop round this last section until different lines
        
        return 'false'

    def Click(event):
        x = WhichArea([event.x,event.y],map.coordinates,map.territory_polygons)
        if x != 'false':

            # DEPLOY: add troops to player's territories
            if game.phase == 0 and map.player_in_territory[x] == game.player_turn and game.troops_to_add != 0:
                map.troops_in_territory[x] += 1
                game.troops_to_add -= 1
                L_TroopsToDeploy.configure(text='Troops to deploy: ' + str(game.troops_to_add))
                
                if game.troops_to_add == 0:
                    L_TroopsToDeploy.place_forget()
                    game.next_action = 'pick fight'

            # ATTACK: choose territory to attack
            if game.phase == 1 and game.next_action == 'pick fight':
                if map.player_in_territory[x] == game.player_turn:
                    game.attacking = x
                    L_Attacking.config(text = 'Attacking: ' + map.territory_names[x])
                    #delete defending incase its invalid
                    game.defending = -1
                    L_Defending.config(text = 'Defending: ')
            
                else:
                    if game.attacking != -1:
                        #checks if other territory is someone elses and connected to attacking. May fail if attacking hasnt been chosen
                        if (map.player_in_territory[x] != game.player_turn) and (map.connections[x][game.attacking] == 1):
                            game.defending = x
                            L_Defending.config(text = 'Defending: ' + map.territory_names[x])

                if game.attacking != -1:
                    Li_Dice.delete(0,END)
                    for i in range(min(map.troops_in_territory[game.attacking]-1,3)):
                        Li_Dice.insert(i, i+1)
                    
            
            # FORTIFY: choose territory to give troops
            elif game.phase == 2:
                #same idea as attacking and defending actually.

                #need a way to deselect since all of them are one player's
                if game.sending_troops == x:
                    game.sending_troops = -1
                    L_SendingTroops.configure(text = 'Sending troops: ')
                    #Delete receiving incase invalid
                    game.receiving_troops = -1
                    L_ReceivingTroops.config(text = 'Receiving troops: ')

                #This must go before the sending troops one so it doesn't just always jump off sending one
                elif game.sending_troops != -1:
                    #checks if other territory is theres, and connected to sending territory
                    connected = ConnectedTerritories(game.sending_troops,x)
                    if (map.player_in_territory[x] == game.player_turn) and connected == True:
                        game.receiving_troops = x
                        L_ReceivingTroops.config(text = 'Receiving troops: ' + map.territory_names[x])
                        for i in range(map.troops_in_territory[game.sending_troops]-1):
                            Li_MoveTroops.insert(i,i+1)

                elif map.player_in_territory[x] == game.player_turn:
                    game.sending_troops = x
                    L_SendingTroops.config(text = 'Sending troops: ' + map.territory_names[x])
                    #delete recieving incase its invalid
                    game.receiving_troops = -1
                    L_ReceivingTroops.config(text = 'Receiving troops: ')




            map.DisplayMap()

    ########################################################################################################################      

    def MergeSort(unsorted):
        lists = []
        for item in unsorted:
            lists.append([item])
        def Merge(a,b,c):
            if a == [] and b == []:
                return c
            elif a == []:
                c.append(b.pop(0))
                return Merge(a,b,c)
            elif b == []:
                c.append(a.pop(0))
                return Merge(a,b,c)
            else:
                if a[0] > b[0]:
                    c.append(a.pop(0))
                    return Merge(a,b,c)
                else:
                    c.append(b.pop(0))
                    return Merge(a,b,c)

        length = len(lists)
        while length > 1:
            new_lists = []
            for x in range(length//2):
                new_lists.append(Merge(lists[2*x],lists[2*x+1],[]))
            #add extra list thats not a pair
            if length%2 == 1:
                new_lists.append(lists[length-1])

            lists = new_lists
            length = len(lists)
        return lists[0]

    def RollDice():
            
        if game.attacking == -1 or game.defending == -1:
            return False
        try:
            num_attacking_dice = Li_Dice.get(Li_Dice.curselection())
        except:
            return False
        num_defending_dice = min(map.troops_in_territory[game.defending],2)
        
        #ROLL
        attacking_dice = []
        attacking_dice_text = ''
        for x in range(num_attacking_dice):
            num = randrange(1,7)
            attacking_dice.append(num)
            attacking_dice_text += str(num) + ' '
        attacking_dice = MergeSort(attacking_dice)

        defending_dice = []
        defending_dice_text = ''
        for x in range(num_defending_dice):
            num = randrange(1,7)
            defending_dice.append(num)
            defending_dice_text += str(num) + ' '
        defending_dice = MergeSort(defending_dice)

        
        L_DiceRolled.configure(text=attacking_dice_text + 'VS ' + defending_dice_text)
        L_DiceRolled.place(x=1040,y=380)

        #Calculates number of troops each player lost based on the dice rolled
        troops_lost = [0,0]
        for x in range(min(num_attacking_dice,num_defending_dice)):
            if attacking_dice[x] > defending_dice[x]:
                troops_lost[1] += 1
            else:
                troops_lost[0] += 1
        
        #take away troops lost in battle from the player totals and the territory amounts
        players[map.player_in_territory[game.attacking]].num_troops -= troops_lost[0]
        players[map.player_in_territory[game.defending]].num_troops -= troops_lost[1]
        map.troops_in_territory[game.attacking] -= troops_lost[0]
        map.troops_in_territory[game.defending] -= troops_lost[1]

        map.DisplayMap()

        #changes listbox IF attacking troops were lost and the troops in territory are 3 and below. This is when it is needing to change
        #i got rid of troops_lost[0] != 0 and map.troops_in_territory[game.attacking] < 4
        if num_attacking_dice > map.troops_in_territory[game.attacking]-1:
            Li_Dice.delete(0,END)
            for i in range(min(map.troops_in_territory[game.attacking]-1,3)):
                Li_Dice.insert(i, i+1)

        #if the battle is won
        if map.troops_in_territory[game.defending] == 0:
            #change colours and numbers
            dead_player = map.player_in_territory[game.defending]
            map.player_in_territory[game.defending] = map.player_in_territory[game.attacking]
            map.troops_in_territory[game.defending] = ''

            #recieve card
            game.card_recieved = True

            win = CheckDead(dead_player)
            if win == True:
                Win()
            
            #Moving troops widgets
            map.DisplayMap()
            Li_MoveTroops.place(x=1040,y=310)
            B_MoveTroops.place(x=1040,y=340)

            #Add options for moving troops
            Li_MoveTroops.delete(0,END)
            for i in range(num_attacking_dice, map.troops_in_territory[game.attacking]):
                Li_MoveTroops.insert(i-1,i)

            game.next_action = 'move troops'

    ################################################################################################################

    def MoveTroops():
        try:
            num_troops_moving = Li_MoveTroops.get(Li_MoveTroops.curselection())
        except:
            return False
        
        if game.phase == 1:
            map.troops_in_territory[game.attacking] -= num_troops_moving
            map.troops_in_territory[game.defending] =  num_troops_moving
            game.next_action = 'pick fight'

        elif game.phase == 2:
            map.troops_in_territory[game.sending_troops] -= num_troops_moving
            map.troops_in_territory[game.receiving_troops] += num_troops_moving
        
        #reset variables
        game.TurnReset()
        Li_MoveTroops.place_forget()
        B_MoveTroops.place_forget()

        map.DisplayMap()

    def ConnectedTerritories(start,goal):
        #This implements a Breadth First Search, using a Queue data structure to check if there is a path between 2 territories
        visited = [start]
        queue = [start]
        while len(queue) != 0:
            parent = queue[0]
            for x in range(len(map.connections[parent])):
                if (map.connections[parent][x] == 1) and (x not in visited) and (map.player_in_territory[parent] == map.player_in_territory[x]):
                    visited.append(x)
                    queue.append(x)
                if x == goal:
                    return True
            queue.pop(0)
        return False

    def CalculateExtraTroops():
        temp = 0
        for player_in_territory in map.player_in_territory:
            if player_in_territory == game.player_turn:
                temp += 1
        territory_troops = max(temp,3) #this is usually //3 but there aren't enouh territories for this (or could be players[game.player_turn].num_troops//3)

        #Region bonuses
        for x in range(len(map.region_bonuses)):
            got_bonus = True
            for y in range(len(map.territory_regions)):
                if map.territory_regions[y] == x:
                    #If player doesn't have one of the territoryies in bonus, they don't get it
                    if map.player_in_territory[y] != game.player_turn:
                        got_bonus = False
            if got_bonus == True:
                territory_troops += (map.region_bonuses[x])
        
        cards = players[game.player_turn].cards
        #ONE OF EACH CARDS
        if cards[0] > 0 and cards[1] > 0 and cards[2] > 0:
            territory_troops += 10
            cards[0] -= 1
            cards[1] -= 1
            cards[2] -= 1
        #THREE OF THE SAME CARD
        elif cards[2] >= 3:
            cards[2] -= 3
            territory_troops += 8
        elif cards[1] >= 3:
            cards[1] -= 3
            territory_troops += 6
        elif cards[0] >= 3:
            cards[0] -= 3
            territory_troops += 4


        return territory_troops

    def CheckDead(player_num):
        own_territory = False
        for x in range(len(map.territory_names)):
            if map.player_in_territory[x] == player_num:
                own_territory = True
                
        #Player is out
        if own_territory == False:
            game.player_queue.remove(player_num)
            #Everyone is out
            if game.player_queue == []:
                return True
            
            #take cards from dead player
            for x in range(3):
                players[game.player_turn].cards[x] += players[player_num].cards[x]
            

        return False


            

    def NextPhase():
        if game.next_action != 'move troops' and game.next_action != 'quit' and game.troops_to_add == 0:

            #DEPLOY --> ATTACK
            if game.phase == 0:
                game.phase = 1

                #HIDE/SHOW WIDGETS
                game.attacking = -1
                game.defending = -1
                L_Attacking.configure(text='Attacking: ')
                L_Defending.configure(text='Defending: ')
                L_Attacking.place(x=1040,y=250)
                L_Defending.place(x=1040,y=280)
                Li_Dice.place(x=1040,y=310)
                B_Roll.place(x=1040,y=340)
                L_DiceRolled.place(x=1040,y=380)
                B_Next_Phase.configure(text='Finish Attack')

            #ATTACK --> FORTIFY
            elif game.phase == 1:
                if game.card_recieved == True:
                    game.ReceiveCard()
                game.phase = 2

                #HIDE/SHOW WIDGETS
                L_Attacking.place_forget()
                L_Defending.place_forget()
                Li_Dice.place_forget()
                B_Roll.place_forget()
                B_Next_Phase.configure(text='Finish Turn')

                L_SendingTroops.place(x=1040,y=250)
                L_ReceivingTroops.place(x=1040,y=280)
                Li_MoveTroops.delete(0,END)
                Li_MoveTroops.place(x=1040,y=310)
                B_MoveTroops.place(x=1040,y=340)

            #FORTIFY --> NEXT TURN DEPLOY
            elif game.phase == 2:
                game.phase = 0
                game.next_action = 'move troops'
                #next player's turn using a queue structure
                game.player_queue.append(game.player_turn)
                
                game.player_turn = game.player_queue[0]
                game.player_queue.pop(0)
                cards = players[game.player_turn].cards
                L_PlayerTurn.configure(text='Player turn: ' + info.players[game.player_turn] + ' (' + str(cards[0]) + ',' + str(cards[1]) + ',' + str(cards[2]) + ')',background=info.colours[game.player_turn],foreground = 'white')

                #reset variables just in case
                game.TurnReset()
                Autosave()

                #HIDE/SHOW WIDGETS
                L_SendingTroops.place_forget()
                L_ReceivingTroops.place_forget()
                Li_MoveTroops.place_forget()
                B_MoveTroops.place_forget()
                B_Next_Phase.configure(text='Start Attack')

                L_TroopsToDeploy.place(x=1040,y=250)

                game.troops_to_add = CalculateExtraTroops()
                L_TroopsToDeploy.configure(text='Troops to deploy: ' + str(game.troops_to_add))

            L_Stage.configure(text=game.stages[game.phase])
            L_DiceRolled.place_forget()
            L_Help.place_forget()
            map.DisplayMap()

    def QuitGame():
        db_path = "./DataBase/ProjectDb.db"
        connection = sqlite3.connect(db_path)
        db_cursor = connection.cursor()

        sql = 'DELETE FROM CurrentGame WHERE UserID = ?'
        db_cursor.execute(sql,(info.userID,))

        connection.commit()
        connection.close()
        window.destroy()

        info.players = []
        info.colours = []
        info.bot = []

        info.next_page = 'MenuPage'

        game.data = None

    def Help():
        L_Help.place(x=200, y=800)
        if game.phase == 0:
            L_Help.configure(text='click your territories that you want to give more troops to')
        elif game.phase == 1:
            L_Help.configure(text='choose a territory to attack. Must be adjacent to one of your territories')
        elif game.phase == 2:
            L_Help.configure(text='move troops from one territory to another. Must be connected through your territories')
            

    def Win():
        game.next_action='Quit'
        L_PlayerTurn.configure(text=info.players[game.player_turn] + ' wins!')

        
        db_path = "./DataBase/ProjectDb.db"
        connection = sqlite3.connect(db_path)
        db_cursor = connection.cursor()

        sql = 'SELECT Games, Wins FROM Users WHERE UserID = ?'
        db_cursor.execute(sql,(info.userID,))
        games, wins = db_cursor.fetchall()[0]

        sql = 'UPDATE Users SET Games = ?, Wins = ?'
        db_cursor.execute(sql,(games+1,wins+1))

        connection.commit()
        connection.close()

    def ListToString(list):
            temp_string = ''
            for x in list:
                temp_string += str(x) + '/'
            temp_string
            return temp_string[:-1]

    def Close():
        #combine player cards into one array
        cards = []
        for i in range(len(players)):
            cards.append(players[i].cards)

        #Connect to the databse in order to save the current game data. 
        db_path = "./DataBase/ProjectDb.db"
        connection = sqlite3.connect(db_path)
        db_cursor = connection.cursor()

        sql = 'DELETE FROM CurrentGame WHERE UserID = ?'
        db_cursor.execute(sql,(info.userID,))
        
        sql = 'INSERT INTO CurrentGame(UserID,MapID,Players,Colours,Bot,PlayerTurn,PlayerQueue,PlayerInTerritory,TroopsInTerritory,Cards) VALUES (?,?,?,?,?,?,?,?,?,?)'
        data = (info.userID,info.mapID,ListToString(info.players),ListToString(info.colours),ListToString(info.bot),game.player_turn,ListToString(game.player_queue),ListToString(map.player_in_territory),ListToString(map.troops_in_territory),ListToString(cards))
        db_cursor.execute(sql,data)
        
        connection.commit()
        connection.close()

        info.next_page = 'Close'
        window.destroy()

    def Autosave():
        #combine player cards into one array
        cards = []
        for i in range(len(players)):
            cards.append(players[i].cards)

        #Connect to the databse in order to save the current game data. 
        db_path = "./DataBase/ProjectDb.db"
        connection = sqlite3.connect(db_path)
        db_cursor = connection.cursor()

        sql = 'DELETE FROM CurrentGame WHERE UserID = ?'
        db_cursor.execute(sql,(info.userID,))
        
        sql = 'INSERT INTO CurrentGame(UserID,MapID,Players,Colours,Bot,PlayerTurn,PlayerQueue,PlayerInTerritory,TroopsInTerritory,Cards) VALUES (?,?,?,?,?,?,?,?,?,?)'
        data = (info.userID,info.mapID,ListToString(info.players),ListToString(info.colours),ListToString(info.bot),game.player_turn,ListToString(game.player_queue),ListToString(map.player_in_territory),ListToString(map.troops_in_territory),ListToString(cards))
        db_cursor.execute(sql,data)
        
        connection.commit()
        connection.close()
        

    ##############################################################################################################
    #START OF THE GAME
    map = Map(map_data)

    #Was there a current game for this user? If not, start the game by randomly assigning territories and troops
    if info.saved_game_data == None:
        players = []
        for x in range(len(info.players)):
            players.append(Player(x,info.players[x],info.colours[x],0))
            game.player_queue.append(x)
            
        num_players = len(players)
        game.player_queue.pop(0)
        map.Deal()

        starting_troops = 12//len(players)
        for i in range(len(players)):
            players[i].num_troops = starting_troops
            x = starting_troops
            while x > 0:
                num = randrange(0,len(map.territory_names))
                if map.player_in_territory[num] == players[i].player_num:
                    map.troops_in_territory[num] += 1
                    x -= 1

    #If so, import the saved data into the game
    else:
        game_data = list(info.saved_game_data)
        #get rid of the /
        for x in range(len(game_data)):
            if type(game_data[x]) is int:
                pass
            elif '/' in game_data[x]:
                if '[' in game_data[x]:
                    game_data[x] = game_data[x].split('/')
                    #split up brackets
                    for y in range(len(game_data[x])):
                        game_data[x][y] = game_data[x][y][1:-1].split(', ')
                        #make them integers
                        for z in range(len(game_data[x][y])):
                            game_data[x][y][z] = int(game_data[x][y][z])
                else:
                    game_data[x] = game_data[x].split('/')

            #changing region bonuses and territory regions into integers
            if x == 6 or x == 7 or x == 8:
                game_data[x] = list(game_data[x])
                for y in range(len(game_data[x])):
                    game_data[x][y] = int(game_data[x][y])

        players = []
        for x in range(len(game_data[2])):
            #add up total troops that a player has
            num_troops = 0
            for y in range(len(game_data[7])):
                if x == game_data[7][y]:
                    num_troops += game_data[8][y]
            players.append(Player(x,game_data[2][x],game_data[3][x],num_troops))
        
        game.player_turn = game_data[5]
        game.player_queue = game_data[6]
        map.player_in_territory = game_data[7]
        map.troops_in_territory = game_data[8]
        info.colours = game_data[3]
        info.players = game_data[2]
        
        #split up the cards
        for i in range(len(game_data[9])):
            players[i].cards = game_data[9][i]

    #First turn
    game.troops_to_add = CalculateExtraTroops() #+10

    ########################################################################################################################
    window = Tk()
    window.title('RISK')
    window.geometry('1000x500')

    #Start up fullscreen
    screen_width= window.winfo_screenwidth() 
    screen_height= window.winfo_screenheight()
    window.geometry("%dx%d" % (screen_width, screen_height))
    window.wm_attributes('-fullscreen', 'true')

    background = Canvas(window,width=screen_width,height=screen_height)
    background.place(x=0,y=0)

    img = ImageTk.PhotoImage(Image.open('GreyBackground.jpeg'))
    background.create_image(0,0,image=img,anchor='nw')

    background.create_text(1125,100, text='RISK', font = 'Ayuthaya 120 bold', fill ='#9A1111')

    canvas = Canvas(window, width=700, height=700, background="#777777")
    canvas.place(x=100,y=75)
    map.DisplayMap()

    ### BUTTONS ###
    L_Stage = Label(window,text=game.stages[game.phase], font = 'Helvetica 20 bold', background='black', foreground = 'white')
    L_Stage.place(x=1030,y=200)
    L_PlayerTurn = Label(window,text='Player turn: ' + str(game.player_turn + 1) + ' (0,0,0)', font = 'Helevtica 20 bold',background=info.colours[game.player_turn],foreground='white')
    L_PlayerTurn.place(x=400,y=30)

    B_Quit = Button(window, text='Quit Game',foreground='#9A1111', font = 'Helvetica 20 bold', highlightbackground='#444444', borderwidth=0, command=QuitGame)
    B_Quit.place(x=900,y=650)
    B_Help = Button(window, text='Help',background='white', font = 'Helvetica 20 bold', highlightbackground='#444444', borderwidth=0, command= Help)
    B_Help.place(x=900,y=700)
    L_Help = Label(window,text='', font = 'Helvetica 20 bold', background='black', foreground = 'white')

    #Close program
    B_Close = Button(window, text = 'X', font = 'Arial 30 bold', foreground='#9A1111', background = 'black',command=Close)
    B_Close.place(x=0,y=0)

    #DEPLOY
    L_TroopsToDeploy = Label(window,text='Troops to deploy: ' + str(game.troops_to_add),font = 'Helvetica 15 bold')
    L_TroopsToDeploy.place(x=1040,y=250)

    #ATTACK
    L_Attacking = Label(window,text='Attacking: ', font = 'Helvetica 15 bold', background='black', foreground = 'white')
    L_Defending = Label(window,text='Defending: ', font = 'Helvetica 15 bold', background='black', foreground = 'white')

    Li_Dice = Listbox(window,height=1)
    B_Roll = Button(window,text='ROLL',background='white', font = 'Helvetica 15 bold', activebackground='#444444', borderwidth=0, command=RollDice)
    L_DiceRolled = Label(window,text='', font = 'Helvetica 20 bold', background='black', foreground = 'white')

    Li_MoveTroops = Listbox(window,height=1)
    B_MoveTroops = Button(window,text='Move troops', font = 'Helvetica 15 bold', highlightbackground='#444444',borderwidth=0,command=MoveTroops)

    B_Next_Phase = Button(window,text='Start Attack',font = 'Helvetica 20 bold', highlightbackground='#444444', borderwidth=0,command=NextPhase)
    B_Next_Phase.place(x=1040,y=450)

    #FORTIFY
    L_SendingTroops = Label(window,text='Sending troops: ', font = 'Helvetica 15 bold')
    L_ReceivingTroops = Label(window,text='Receiving troops: ', font = 'Helvetica 15 bold')
        #using Li_MoveTroops and B_MoveTroops

    canvas.bind("<Button 1>", Click)
    window.update_idletasks
    window.update
    window.mainloop()

######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
#######################
##### MAP BUILDER #####
#######################

def MapBuilder():

    ### CREATING LINES ###

    class LineMaker:
        # s instead of self
        def __init__(s):
            s.drawing = True

            s.coordinates = []
            s.lines = []
            s.line_equations = []

            s.selected = 0
            s.click = 0
            s.change = -1
            s.undo = False
            
            s.oval = []
            
        def Point(s,x,y,new):
            s.undo = [s.selected]
            #This loop iterates through the existing points, checking if the new point is close enough to be one.
            for i in range(len(s.coordinates)):
                z = s.coordinates[i]
                #This calculation checks if the click is in a certain radius of points already drawn
                if math.sqrt((x - z[0])**2 + (y - z[1])**2) <= 6:
                    new = False
                    #if already selected is selected again, deselect
                    if s.selected == i:
                        s.selected = -1
                    #if none is selected already, select new click
                    elif s.selected == -1:
                        s.selected = i
                    #if already selected and other is selected, wait until line drawn
                    else:
                        s.change = i

                    s.oval = [z[0],z[1],False]
                    
                    s.click = i
            #If none of the existing points are close enough, create a new point
            if new == True:
                s.coordinates.append([x,y])
                s.click = len(s.coordinates) - 1
                s.oval = [x,y,True]
                s.change = s.click
        
        def Line(s):
            if s.selected != s.click:
                x1,y1 = s.coordinates[s.selected][0], s.coordinates[s.selected][1]
                x2,y2 = s.coordinates[s.click][0], s.coordinates[s.click][1]
                Valid = True
                for i in range(len(s.lines)):
                    if s.selected not in s.lines and s.click not in s.lines:
                        valid = CrossingLines(x1,y1,x2,y2,s.coordinates[s.lines[i][0]][0], s.coordinates[s.lines[i][0]][1], s.coordinates[s.lines[i][1]][0],s.coordinates[s.lines[i][1]][1])
                        if valid != True:
                            Valid = False
                            s.change = s.selected
                if Valid == True:
                    s.lines.append([s.selected,s.click])
                    s.line_equations.append(FindEquation(s.coordinates[s.selected][0],s.coordinates[s.selected][1],s.coordinates[s.click][0],s.coordinates[s.click][1]))
                    canvas.create_line(x1,y1,x2,y2,fill="blue",width = 1)
                    s.undo.append('line')
                    s.selected = len(s.coordinates)-1
                else:
                    s.oval[2] = False
                    s.coordinates.pop(len(s.coordinates)-1)


    def FindEquation(x1,y1,x2,y2): 
        #Gradient
        if x1 == x2:
            return False
        m = (y2-y1)/(x2-x1)
        #Constant
        c = y1 - m * x1
        return [m,c]

    def CrossingLines(x1,y1,x2,y2,x3,y3,x4,y4):
        #x1,y1,x2,y2 : new line
        #x3,y3,x4,y4 : existing lines

        if x1 == x2 or x3 == x4:
            return 0
        #Calculate Gradients
        g1 = (y2-y1)/(x2-x1)
        g2 = (y4-y3)/(x4-x3)
        #Calculate Cs
        k1 = y1 - g1 * x1
        k2 = y3 - g2 * x3
        #Set lines equal to each other
        g3 = g1 - g2
        k3 = (k1 - k2) * -1
        #Find point of intersection
        if g3 == 0:
            return 0
        x = k3 / g3
        #Check if intersection is within both lines
        within_line1 = (x+.0001 < x1 and x-.0001 > x2) or (x-.0001 > x1 and x+.0001 < x2)
        within_line2 = (x+.0001 < x3 and x-.0001 > x4) or (x-.0001 > x3 and x+.0001 < x4)
        if within_line1 and within_line2:
            return False
        
        return True

    linemaker = LineMaker()

    ##################################################################################################################

    def Click(event):
        #After drawing is finished, this function is used to create the regions instead
        if linemaker.drawing == False:
            if after_drawing.next_action == "ClickOnTerritory":
                after_drawing.ClickOnTerritory(event.x,event.y)
            elif after_drawing.next_action == "InputLabelPosition":
                after_drawing.InputLabelPosition(event.x,event.y)
        
            L_NextAction.configure(text=after_drawing.next_action)
            return False
        
        linemaker.Point(event.x,event.y,True)
        #print('[',event.x,',',event.y,']')
        print(linemaker.selected)
        

        if linemaker.selected != -1:
            linemaker.Line()

        if linemaker.change != -1:
            linemaker.selected = linemaker.change
            linemaker.change = -1

        if linemaker.oval[2] == True:
            canvas.create_oval(linemaker.oval[0] - 3, linemaker.oval[1] - 3, linemaker.oval[0] + 3, linemaker.oval[1] + 3)
            linemaker.undo.append('point')

    def Undo():
        #Don't run if undo has happened just now OR if drawing stage is over
        if linemaker.undo == False or linemaker.drawing == False:
            return False
        
        if 'line' in linemaker.undo:
            line = linemaker.lines[len(linemaker.lines)-1]
            linemaker.lines.pop(len(linemaker.lines)-1)
            linemaker.line_equations.pop(len(linemaker.line_equations)-1)
            #drawing over the line in white
            canvas.create_line(linemaker.coordinates[line[0]][0],linemaker.coordinates[line[0]][1],linemaker.coordinates[line[1]][0],linemaker.coordinates[line[1]][1],fill="white",width = 3)
            #redrawing circles attached
            canvas.create_oval(linemaker.coordinates[line[0]][0] - 3, linemaker.coordinates[line[0]][1] - 3, linemaker.coordinates[line[0]][0] + 3, linemaker.coordinates[line[0]][1] + 3)
            canvas.create_oval(linemaker.coordinates[line[1]][0] - 3, linemaker.coordinates[line[1]][1] - 3, linemaker.coordinates[line[1]][0] + 3, linemaker.coordinates[line[1]][1] + 3)
        if 'point' in linemaker.undo:
            coordinates = linemaker.coordinates[len(linemaker.coordinates)-1]
            linemaker.coordinates.pop(len(linemaker.coordinates)-1)
            #drawing over the circle
            canvas.create_oval(coordinates[0] - 4, coordinates[1] - 4, coordinates[0] + 4, coordinates[1] + 4,outline='white',fill="white")
        

        linemaker.selected = linemaker.undo[0]
        #So you can only do 1 undo
        linemaker.undo = False

    ### AFTER DRAWING ###   MAKE ALL OF THIS A CLASS THATS NOT LINEMAKER ANYMORE ##########################################

    class AfterDrawing: 

        regions = []
        territories = []
        territory_regions = []
        #this is for when each is selected, to put them in order
        territory_polygons = []
        #this is when all of them are created at the start
        polygons = []

        text_coordinates = []

        map_data = []

        def __init__(s):
            s.next_action = 'ClickOnTerritory'
            s.clicked_polygon = -1

        
        def PlaceButtons(s):
            L_NextAction.place(x=867,y=550)

            background.create_text(905,260, text='Territory', font = 'Helvetica 20 bold', fill ='black')
            background.create_text(900,310, text='Region', font = 'Helvetica 20 bold', fill ='black')

            E_Name.place(x=970,y=250)
            Li_Region.place(x=970,y=300)

            E_AddRegion.place(x=970,y=350)
            B_AddRegion.place(x=1200,y=351)
            B_Finish.configure(text='FINISH',command=ExportMap)
            B_Finish.place(x=1200,y=700)

            B_SubmitNameRegion.place(x=867,y=450)

            canvas.delete('all')
            B_Undo.destroy()

        def MakePolygons(s):
            lines = linemaker.lines
            coordinates = linemaker.coordinates
            lines_used = []
            for x in range(len(lines)):
                lines_used.append(0)

            polygons = []

            for i in range(len(coordinates)):
                coordinate = coordinates[i]
                finding_polygons = True
                #find every polygon attached to a point
                while finding_polygons:
                    #find smallest polygon first
                    queue = [[i,[i]]]
                    searched = []
                    path = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                    finding_smallest_polygon = True
                    while queue != []:
                        searching = queue.pop(0)
                        
                        searched.append(searching)
                        #find all paths to search that are connected to point and havent been used twice
                        for l in range(len(lines)):
                            if searching[0] in lines[l] and lines_used[l] != 2:
                                
                                #find next node
                                next = lines[l][0]
                                if next == searching[0]:
                                    next = lines[l][1]

                                #add new node to potential path, add path to queue
                                if (next not in searching[1]):
                                    #so it doesnt mess up lists
                                    temp = []
                                    for item in searching[1]:
                                        temp.append(item)
                                    temp.append(next)
                                    queue.append([next,temp])

                                #if it has made a loop, check if loop is smallest
                                elif next == i and len(searching[1]) > 2:
                                    #check if polygon has already been found
                                    found_already = False
                                    for polygon in polygons:
                                        if SamePolygon(searching[1],polygon):
                                            found_already = True
                                    if found_already == False and len(searching[1]) < len(path):
                                        path = searching[1]
                                        
                    
                    if path != [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]:
                        polygons.append(path)
                    else:
                        finding_polygons = False

                    #adding to lines used
                    for x in range(len(lines)):
                        for y in range(len(path)-1):
                            if (lines[x][0] == path[y] and lines[x][1] == path[y+1]) or (lines[x][0] == path[y+1] and lines[x][1] == path[y]):
                                lines_used[x] += 1
                        if (lines[x][0] == path[len(path)-1] and lines[x][1] == path[0]) or (lines[x][0] == path[0] and lines[x][1] == path[len(path)-1]):
                            lines_used[x] += 1


            #remove biggest polygon (this is the perimeter of the country) §won't work with multiple land masses   
            if 1 not in lines_used:
                biggest = [0,0]
                for x in range(len(polygons)):
                    if len(polygons[x]) > biggest[1]:
                        biggest = [x,len(polygons[x])]
                polygons.pop(biggest[0])

            #print em
            s.polygons = polygons
            colours = ['#333333','#444444','#555555','#666666','#777777','#888888']
            for i in range(len(polygons)):
                temp = []
                for point in polygons[i]:
                    temp.append(linemaker.coordinates[point])
                canvas.create_polygon(temp,fill=colours[i%6],outline='white')

        def Connections(s):
            #creating the 2D matrix
            connections = []
            temp = []
            for x in range(len(after_drawing.polygons)):
                temp.append(0)
            for x in range(len(after_drawing.polygons)):
                connections.append(temp)

            #Find which polygons the lines are connected to. If connected to 2 polygons, make a connection between them
            for x in range(len(linemaker.lines)):
                connection = []
                for y in range(len(after_drawing.polygons)):
                    for z in range(len(after_drawing.polygons[y])-1):
                        if after_drawing.polygons[y][z] in linemaker.lines[x] and after_drawing.polygons[y][z+1] in linemaker.lines[x]:
                            connection.append(y)
                    if after_drawing.polygons[y][len(after_drawing.polygons[y])-1] in linemaker.lines[x] and after_drawing.polygons[y][0] in linemaker.lines[x]:
                            connection.append(y)

                if len(connection) == 2:
                    connections[connection[0]][connection[1]] = 1
                    connections[connection[1]][connection[0]] = 1

        def ClickOnTerritory(s,x,y):
            #highlight the polygon that you are naming
            s.clicked_polygon = WhichArea([x,y],linemaker.coordinates,s.polygons)
            if s.clicked_polygon == 'false' or s.clicked_polygon in s.territory_polygons:
                return False
            s.territory_polygons.append(s.clicked_polygon)
            
            temp = []
            for point in s.polygons[s.clicked_polygon]:
                temp.append(linemaker.coordinates[point])
            canvas.create_polygon(temp,fill='white',outline='red')
            
            s.next_action = 'NameAndRegion'
            L_NextAction.configure(text=s.next_action)
            
        def NameAndRegion(s):
            if s.next_action != "NameAndRegion":
                return False
            
            try:
                name = E_Name.get()
                E_Name.delete(0,END)
                region = Li_Region.get(Li_Region.curselection())
                
            except:
                return False

            if name == '' or region == '':
                return False
            
            s.next_action = "InputLabelPosition"
            L_NextAction.config(text=s.next_action)

            s.territories.append(name)
            for i in range(len(s.regions)):
                if s.regions[i] == region:
                    s.territory_regions.append(i)
            
        
        def InputLabelPosition(s,x,y):
            s.text_coordinates.append([x,y])
            temp = []
            for point in s.polygons[s.clicked_polygon]:
                temp.append(linemaker.coordinates[point])
            
            colours = ['#142C85','#A5322E','#238026','#FFEA00'] 
            canvas.create_polygon(temp,fill=colours[s.territory_regions[len(s.territory_regions)-1]],outline='white')
            canvas.create_text(x,y, text=s.territories[len(s.territories)-1],font = 'Helvetica 15 bold')

            #finished?
            if len(s.territory_polygons) == len(s.polygons):
                s.Complete()
            else:
                s.next_action = "ClickOnTerritory"
                L_NextAction.config(text=s.next_action)
            

        def AddRegion(s):
            if len(s.regions) == 4:
                return False
            value = E_AddRegion.get()
            if value == '':
                return False
            s.regions.append(value)
            Li_Region.insert('end',value)
            #E_AddRegion.text = '' §
        
        def Complete(s):
            s.next_action = 'map name and finish'
            L_MapName.place(x=1200,y=520)
            E_MapName.place(x=1200,y=560)

            s.map_data.append(ListToString(s.territories))

            ordered_polygons = []
            for polygon_index in s.territory_polygons:
                ordered_polygons.append(s.polygons[polygon_index])
            s.map_data.append(ListToString(ordered_polygons))
            s.map_data.append(ListToString(linemaker.coordinates))
            s.map_data.append(ListToString(s.regions))
            #§
            region_bonuses = []
            for x in range(len(s.regions)):
                #This calculates how much a bonus should be for each region (num territories in it / 2)
                count = 1
                for y in s.territory_regions:
                    if x == y:
                        count += 1
                region_bonuses.append(count // 2)
            s.map_data.append(ListToString(region_bonuses))

            s.map_data.append(ListToString(s.territory_regions))
            s.map_data.append(ListToString(s.text_coordinates))

            s.map_data.append('N/A')



    after_drawing = AfterDrawing()

    ##################################################################################################################

    def FinishDrawing():

        if len(linemaker.lines) < 3:
            return False
        
        #Check if any points have only 1 connection
        count = []
        for i in range(len(linemaker.coordinates)):
            count.append(0)
        for line in linemaker.lines:
            count[line[0]] += 1
            count[line[1]] += 1
            
        valid = True
        for num in count:
            if num < 2:
                valid = False

        if valid == False:
            return False
        
        linemaker.drawing = False
        
        after_drawing.PlaceButtons()
        after_drawing.MakePolygons()
        after_drawing.Connections()

        

    #OTHER METHODS

    def SamePolygon(polygon1,polygon2):
        count = 0
        for point in polygon1:
            if point in polygon2:
                #coudn't just remove it because it was messing up list on outside
                count += 1
        if len(polygon2) == count:
            return True
        return False

    def ListToString(list):
        temp_string = ''
        for x in list:
            temp_string += str(x) + '/'
        temp_string
        return temp_string[:-1]


    def WhichArea(click,coordinates,polygons):
        smallest_distance = 1000
        for i in range(len(polygons)):
            for j in range(len(polygons[i])):
                coord1 = coordinates[polygons[i][j]]
                try:
                    coord2 = coordinates[polygons[i][j+1]]
                except:
                    coord2 = coordinates[polygons[i][0]]
                gradient = (coord1[1]-coord2[1])/(coord1[0]-coord2[0])
                k = coord1[1] - gradient * coord1[0]

                opposite_gradient = -1 / gradient
                opposite_k = click[1] - opposite_gradient * click[0]

                closest_x = (k-opposite_k)/(opposite_gradient-gradient)
                if (closest_x > coord1[0] and closest_x < coord2[0]) or (closest_x < coord1[0] and closest_x > coord2[0]):
                    closest_y = gradient * closest_x + k
                    distance = math.sqrt((closest_x - click[0])**2 + (closest_y - click[1])**2)
                    
                    if distance < smallest_distance:
                        try:
                            points = [polygons[i][j],polygons[i][j+1]]
                        except:
                            points = [polygons[i][j],polygons[i][0]]
                        best_line_gradient = gradient
                        best_line_k = k
                        smallest_distance = distance
                        best_closest_x = closest_x
                        best_closest_y = closest_y
        
        #canvas.create_line(click[0],click[1],best_closest_x,best_closest_y)

        #Finding next points along
        if coordinates[points[0]][1] < coordinates[points[1]][1]:
            higher_point = points[0]
            lower_point = points[1]
        else:
            higher_point = points[1]
            lower_point = points[0]

        #Find potential polygons that it could be, along with their next points
        potential_polygons = []
        for polygon in polygons:
            for x in range(len(polygon)):
                #one direction
                try:
                    if polygon[x] == lower_point and polygon[x+1] == higher_point:
                        potential_polygons.append([polygon,polygon[x+2]])
                except:
                    try:
                        if polygon[x] == lower_point and polygon[x+1] == higher_point:
                            potential_polygons.append([polygon,polygon[0]])   
                    except:
                        if polygon[x] == lower_point and polygon[0] == higher_point:
                            potential_polygons.append([polygon,polygon[1]])
                #other direction
                try:
                    if polygon[x] == lower_point and polygon[x-1] == higher_point:
                        potential_polygons.append([polygon,polygon[x-2]])
                except:
                    try:
                        if polygon[x] == lower_point and polygon[x-1] == higher_point:
                            potential_polygons.append([polygon,polygon[len(polygon)-1]])
                    except:
                        if polygon[x] == lower_point and polygon[len(polygon)-1] == higher_point:
                            potential_polygons.append([polygon,polygon[len(polygon)-2]])

        #Matrix rotation algorithm to check if it's left or right
        rotating_point = [click[0] - best_closest_x,click[1] - best_closest_y]
        angle = math.pi/2 - math.atan(best_line_gradient)
        if angle > math.pi/2:
            angle = angle - math.pi
        new_point = [math.cos(angle) * rotating_point[0] - math.sin(angle) * rotating_point[1], math.sin(angle) * rotating_point[0] + math.cos(angle) * rotating_point[0]]
        if new_point[0] > 0: 
            right = True
        else:
            right = False
        
        # matrix thing again to see which side is the correct one. Finds the next point attached to highest point on line and  sees which is
        for potential_polygon in potential_polygons:
            next_point = potential_polygon[1]
            gradient = (coordinates[next_point][1] - coordinates[higher_point][1])/(coordinates[next_point][0] - coordinates[higher_point][0])
            matrix_thing = math.cos(angle) * (coordinates[next_point][0]-coordinates[higher_point][0]) - math.sin(angle) * (coordinates[next_point][1] - coordinates[higher_point][1])
            if right == (matrix_thing > 0):
                for x in range(len(polygons)):
                    if polygons[x] == potential_polygon[0]:
                        return x
        #? this wont work if they share 2 lines. it will need to loop round this last section until different lines
        
        return 'false'

    def ExportMap():
        if after_drawing.next_action != 'map name and finish':
            return False
        
        map_name = E_MapName.get()
        if map_name == '':
            return False
        
        map_data = after_drawing.map_data
        map_data.insert(0,map_name)
        
        #Connect to Database
        db_path = "./DataBase/ProjectDb.db"
        connection = sqlite3.connect(db_path)
        db_cursor = connection.cursor()
        

        sql = "INSERT INTO Maps(Name,TerritoryNames,Polygons,Coordinates,RegionNames,RegionBonuses,TerritoryRegions,LabelCoordinates,Connections) VALUES (?,?,?,?,?,?,?,?,?)"
        db_cursor.execute(sql,map_data)

        connection.commit()
        connection.close()

        window.destroy()

    def Back():
        info.next_page = 'MenuPage'
        window.destroy()

    def Close():
        info.next_page = 'Close'
        window.destroy()


    window = Tk()
    window.title('Vector Menu')

    screen_width= window.winfo_screenwidth() 
    screen_height= window.winfo_screenheight()
    window.geometry("%dx%d" % (screen_width, screen_height))
    window.wm_attributes('-fullscreen', 'true')

    background = Canvas(window,width=screen_width,height=screen_height)
    background.place(x=0,y=0)

    canvas = Canvas(window, width=700, height=700, background="white")
    canvas.place(x=100,y=75)

    background.create_text(1125,100, text='Map Builder', font = 'Ayuthaya 80 bold', fill ='#9A1111')

    img = ImageTk.PhotoImage(Image.open('IMG_3772.jpg'))
    #canvas.create_image(0,0,image=img,anchor='nw')

    #BUTTONS
    B_Undo = Button(window, text='UNDO', background='white', font = 'Helvetica 20 bold', foreground = 'black', highlightbackground='#444444',borderwidth=0, command=Undo)
    B_Undo.place(x=867,y=200)

    B_Finish = Button(window, text = 'FINISH DRAWING', font = 'Helvetica 20 bold', foreground = 'black', highlightbackground='#444444',borderwidth=0, command=FinishDrawing)
    B_Finish.place(x=867,y=250)

    B_Back = Button(window, text = 'BACK', font = 'Helvetica 20 bold', foreground = '#9A1111', highlightbackground='#444444',borderwidth=0, command=Back)
    B_Back.place(x=867,y=700)

    L_NextAction = Label(window,text=after_drawing.next_action, font = 'Helvetica 20 bold')
    E_Name = Entry(window)
    B_SubmitNameRegion = Button(window, text = 'SUBMIT',font = 'Helvetica 20 bold', foreground = 'black', highlightbackground='#444444',borderwidth=0,command=after_drawing.NameAndRegion)

    Li_Region = Listbox(window,height=1)
    E_AddRegion = Entry(window)
    B_AddRegion = Button(window, text='Add Region',background = 'white', font = 'Helvetica 15 bold', foreground = 'black', highlightbackground='#444444',borderwidth=0, command=after_drawing.AddRegion)

    L_MapName = Label(window,text='Map Name:', font = 'Helvetica 20 bold ')
    E_MapName = Entry(window)

    canvas.bind("<Button 1>", Click)

    #Close program
    B_Close = Button(window, text = 'X', font = 'Arial 30 bold', foreground='#9A1111', background = 'black',command=Close)
    B_Close.place(x=0,y=0)

    window.mainloop()


######################################################################################################################################
######################################################################################################################################
######################################################################################################################################
### MODULE SWITCHER ###
#######################
'''
running = True
while running == True:
    if info.next_page == 'LoginPage':
        LoginPage()
    elif info.next_page == 'MenuPage':
        MenuPage()
    elif info.next_page == 'SetupSingleplayer':
        Setup()
    elif info.next_page == 'Gameplay':
        Gameplay()
    elif info.next_page == 'MapBuilder':
        MapBuilder()
    else:
        running = False

'''
running = True
while running == True:
    match info.next_page:
        case 'LoginPage':
            LoginPage()
        case 'MenuPage':
            MenuPage()
        case 'SetupSingleplayer':
            Setup()
        case 'Gameplay':
            Gameplay()
        case 'MapBuilder':
            MapBuilder()
        case _:
            running = False