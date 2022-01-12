from random import randint
from textwrap import dedent
from textwrap import indent
from sys import exit
game_beginning = True
accuse_count = 0

#################
# See code line 514 for game engine and instantiatons of objects used in game
#################

# The following two functions return instances of Character and Room depending on the string passed in.
def function_mapping_names(char_name):
    characters = {
        'alexander': alexander,
        'clarissa': clarissa,
        'jonathan': jonathan,
        'kimberly': kimberly,
        'michael': michael,
        'lisa': lisa,
        'richie': richie,
    }
    return characters.get(char_name)

def function_mapping_rooms(player_action):
    rooms = {       
        'hallway': hallway,
        'kitchen': kitchen,
        'living room': living_room,
        'dining room': dining_room,
        'garage': garage,
        'master bathroom': master_bath,
        'master bedroom': master_bed,
        'hall bathroom': hall_bath,
        'player death': player_death,
        'accusation': accusation
    }
    for key in rooms.keys():
        if key in player_action:
            return rooms.get(key)
    else:
        print('Looks like we ran into a problem. Restart the game and try again.')
        exit()

user_notes = ''
def notes(player_action):
    while 'note' in player_action:
        global user_notes

        if user_notes == '':
            print('No notes yet.')
        else:
            print('\nNotes:\n')
            print(user_notes)
        user_notes += input('\nWrite your note here (if you have nothing to add, hit enter): ') + '\n'
        print('\nOk. Now what would you like to do? ')
        player_action = input('> ')
    return player_action

# User room set seperately due to user input determining next room
def set_player_room(player_action):

    player.set_next_room(function_mapping_rooms(player_action.strip().lower()))

    current_room = player.get_current_room()
    next_room = player.get_next_room()
    next_room.characters.append(player)
    current_room.characters.remove(char)

    player.set_prev_room(current_room)
    player.set_current_room(next_room)
    player.set_next_room(None)

def set_all_char_moves(player_action):
    # Saves previous room characters to be called in Character.interact if necessary
    for room in all_rooms:
        characters_in_room = room.get_characters()
        room.set_prev_room_chars(characters_in_room[:])

    # Cycles all rooms to find all characters and change their rooms
    completed_chars = []
    completed_chars.append(player)
    for room in all_rooms:
        characters_in_room = room.get_characters()

        for char in characters_in_room[:]:
            if char in completed_chars:
                continue

            # Determines random room from available choices and sets equal to character's next room
            rand_int = randint(0, len(room.room_options)-1)
            rand_room = room.room_options[rand_int]
            char.set_next_room(rand_room)

            # Gets current and next room instances to enable manipulation of character list in each
            current_room = char.get_current_room()
            next_room = char.get_next_room()
            next_room.characters.append(char)
            current_room.characters.remove(char)

            char.set_prev_room(current_room)
            char.set_current_room(next_room)
            char.set_next_room(None)

            completed_chars.append(char)

    set_player_room(player_action)

    # Enables murderer to pick up weapon
    for char in all_characters:
        if len(char.current_room.characters) == 1 and char.is_murderer() == True:
                if char.weapon == 'their bare hands':
                    char.pick_up_weapon(char.get_current_room().weapon)
                    char.current_room.weapon = None
                elif char.current_room.weapon == None:  # Avoids murderer weapon becoming None
                    continue
                else:
                    weapon = char.weapon
                    char.pick_up_weapon(char.get_current_room().weapon)
                    char.current_room.weapon = weapon

    # If the killer is in a room with one other person other than the user_player, the character dies.
    for char in all_characters:    
        if len(char.current_room.characters) == 2 and player not in char.current_room.characters and char.is_murderer() == True:
            if char.current_room.weapon != None:
                if char.weapon == 'their bare hands':
                    char.pick_up_weapon(char.get_current_room().weapon)
                    char.current_room.weapon = None
                else:
                    weapon = char.weapon
                    char.pick_up_weapon(char.get_current_room().weapon)
                    char.current_room.weapon = weapon
            char.current_room.generate_body(char.current_room.characters[:])

    global game_beginning
    game_beginning = False

################
# Long class methods are organized alphabetically below setters and getters
################

class Character:
    def __init__(self, name, prev_room=None, current_room=None, next_room=None):
        self.name = name
        self.weapon = None
        self.prev_room = prev_room
        self.prev_room_chars = None
        self.current_room = current_room
        self.next_room = next_room
        self.murderer = False

    def __repr__(self):
        return self.name

    def is_murderer(self):
        return self.murderer

    def get_prev_room(self):
        return self.prev_room
    
    def get_current_room(self):
        return self.current_room
    
    def get_next_room(self):
        return self.next_room

    def set_prev_room(self, prev_room):
        self.prev_room = prev_room
    
    def set_current_room(self, current_room):
        self.current_room = current_room

    def set_next_room(self, next_room):
        self.next_room = next_room
    
    def pick_up_weapon(self, weapon):
            self.weapon = weapon

    def interact(self):
        if self.get_prev_room() == None:
            print(dedent(f'''
            You approach {self.name} who says, "I have not been in any other rooms yet."'''))
        # Dense if/elif/else statements. Essentially just printing different statements based on whether there is a body, weapon, or other people in the room.
        else:
            list_of_prev_room_char_names = []
            for char in self.get_prev_room().get_prev_room_chars():
                list_of_prev_room_char_names.append(char.name)  # List of string names used below

            weapon = ''
            if self.get_prev_room().weapon == None:
                weapon = 'No weapon'
            else:
                weapon = self.get_prev_room().weapon
            
            if len(self.get_prev_room().bodies) == 0:
                if len(list_of_prev_room_char_names) == 1:
                    print(dedent(f'''
                    You approach {self.name} who says, "The last room I was in was the {self.get_prev_room()}...
                    {weapon} was there and no one was in there with me."'''))
                elif len(list_of_prev_room_char_names) == 2:
                    list_of_prev_room_char_names.remove(self.name)
                    room_chars = list_of_prev_room_char_names[0]
                    if 'you' in list_of_prev_room_char_names:
                        room_chars += ' were'
                    else:
                        room_chars += ' was'
                    print(dedent(f'''
                    You approach {self.name} who says, "The last room I was in was the {self.get_prev_room()}... 
                    {weapon} was there and {room_chars} there too."'''))
                else:
                    list_of_prev_room_char_names.remove(self.name)
                    str_of_chars = ', '.join(list_of_prev_room_char_names[:len(list_of_prev_room_char_names)-1]) + ' and ' + list_of_prev_room_char_names[-1]
                    print(dedent(f'''
                    You approach {self.name} who says, "The last room I was in was the {self.get_prev_room()}... 
                    {weapon} was there and {str_of_chars} were there too."'''))

            # last_room_description used here to avoid duplicative code
            elif len(self.get_prev_room().bodies) == 1:
                bodies = self.get_prev_room().bodies[0].name
                self.last_room_description(bodies, weapon, list_of_prev_room_char_names)
            elif len(self.get_prev_room().bodies) == 2:
                bodies = [char.name for char in self.get_prev_room().bodies]
                bodies = ' and '.join(bodies)
                self.last_room_description(bodies, weapon, list_of_prev_room_char_names)
            else:
                bodies = [char.name for char in self.get_prev_room().bodies]
                bodies = ', '.join(bodies) + ' and ' + bodies[-1]
                self.last_room_description(bodies, weapon, list_of_prev_room_char_names)

    def last_room_description(self, bodies, weapon, prev_room_chars):
        if len(prev_room_chars) == 1:
                print(dedent(f'''
                You approach {self.name} who says, "The last room I was in was the {self.get_prev_room()}...
                {weapon} was there and no one was in there with me. Oh! And how could I forget... I saw the body of {bodies} in there too."'''))
        elif len(prev_room_chars) == 2:
            prev_room_chars.remove(self.name)
            print(dedent(f'''
            You approach {self.name} who says, "The last room I was in was the {self.get_prev_room()}... 
            {weapon} was there and {prev_room_chars[0]} was there too. Oh! And how could I forget... I saw the bodies of {bodies} in there too."'''))
        else:
            prev_room_chars.remove(self.name)
            str_of_chars = ', '.join(prev_room_chars[:len(prev_room_chars)-1]) + ' and ' + prev_room_chars[-1]
            print(dedent(f'''
            You approach {self.name} who says, "The last room I was in was the {self.get_prev_room()}... 
            {weapon} was there and {str_of_chars} were there too. Oh! And how could I forget... I saw the bodies of {bodies} in there too."'''))

################
# Long class methods are organized alphabetically below setters and getters
################

class Room:
    def __init__(self, name, weapon, characters, room_options):
        self.name = name
        self.weapon = weapon
        self.characters = characters
        self.room_options = room_options
        self.bodies = []
        self.body_in_room = False
        self.visit_with_body = 0

    def __str__(self):
        return self.name

    def get_characters(self):
        return self.characters

    def get_prev_room_chars(self):
        return self.prev_room_chars

    def set_prev_room_chars(self, prev_room_chars_list):
        self.prev_room_chars = prev_room_chars_list

    def determine_game_begin(self):
        if game_beginning == True:
            self.characters = all_characters[:]
        else:
            return
    
    # Formats string of characters in room and determines whether there is a weapon in the room via room_weapon_check function.
    # Passes info to room_descrip to avoid duplicative code
    def determine_room_environ(self, chars):

        formatted_names = ''

        if player.name in chars:
            chars.remove(player.name)
        if len(chars) > 2:
            formatted_names = ', '.join(chars[0:len(chars)-1])
            formatted_names += f' and {chars[-1]} are'
            is_weapon = self.room_weapon_check()
            self.room_descrip(is_weapon, formatted_names)
        elif len(chars) == 1:
            formatted_names = f'{chars[0]} is'
            is_weapon = self.room_weapon_check()
            self.room_descrip(is_weapon, formatted_names)
        elif len(chars) == 2:
            formatted_names = f'{chars[0]} and {chars[-1]} are'
            is_weapon = self.room_weapon_check()
            self.room_descrip(is_weapon, formatted_names)
        else:
            formatted_names = 'no one is'
            is_weapon = self.room_weapon_check()
            self.room_descrip(is_weapon, formatted_names)
    
    # Does most of the heavy lifting. Calls several different methods to properly present info based on user choices.
    def enter(self):
        self.determine_game_begin()
        
        chars = []
        for char in self.characters:
                chars.append(char.name)
            
        self.determine_room_environ(chars)

        # Determines whether there is a body in the room user player enters. 
        if self.body_in_room == True and player not in self.bodies:
            self.visit_with_body += 1
            if self.visit_with_body == 1 and len(self.bodies) == 1:
                print(f'Out of the corner of your eye, you also see... Oh no! It looks like the killer got to {self.bodies[0].name}!')
            elif len(self.bodies) == 2:
                str_names = []
                for char in self.bodies:
                    str_names.append(char.name)
                formatted_names = ' and '.join(str_names)
                print(f'Out of the corner of your eye, you also see... Oh no! It looks like the killer got to {formatted_names}!')
            elif len(self.bodies) > 2:
                str_names = []
                for char in self.bodies:
                    str_names.append(char.name)
                formatted_names = ', '.join(str_names[0: len(str_names)-1]) + ' and ' + str_names[-1]
                print(f'Out of the corner of your eye, you also see... Oh no! It looks like the killer got to {formatted_names} all in the same room!')
            else:
                print(f'You still see {self.bodies[-1].name}\'s body lying there as well. A stark reminder of the danger you are in.')

        # This if statement is called here to reveal murderer after user player sees body
        if len(self.characters) == 2 and the_murderer in self.characters and player in self.characters:
           return self.murder_fight()

        print(dedent('''
        What would you like to do? You can:
        - Interact with a character (type interact, hit enter, then type the character's name and hit enter again.)
        - Accuse someone of being the murderer (type accuse, hit enter.)
        - Go to:
        '''), end='')
        for room in self.room_options:
            print(indent(room.name.capitalize(), '    * '))

        action = input('> ')

        # Handles selecting next room for game engine
        return self.next_room_selector(chars, action)

    # Removes character killed as active player, and adds them to the list of bodies for room they were in
    def generate_body(self, chars_in_room):
        chars_in_room.remove(the_murderer)
        self.bodies.append(chars_in_room[-1])
        self.characters.remove(self.bodies[-1])
        all_characters.remove(self.bodies[-1])
        self.body_in_room = True

    def interactions(self, chars, action):
        while 'interact' in action:
            if len(chars) >= 1:
                which_char_interact = input('\nWho would you like to interact with? > ').lower()
                loop_count = 0
                while which_char_interact.capitalize() not in chars:
                    which_char_interact = input('\nTry again. Who would you like to interact with? > ').lower()
                    loop_count += 1
                    if loop_count >= 3:
                        print('Are you sure they are in the room with you?')
                char_name = function_mapping_names(which_char_interact)
                char_name.interact()
                action = input('\nWhat would you like to do now? > ')
            else:
                print('\nLooks like no one else is in the room with you.')
                action = input('\nWhat room would you like to go to? >')
        return action

    def murder_fight(self):
        if the_murderer.weapon == 'their bare hands':
            print(dedent(f'Suddenly {the_murderer.name} is in front of you smiling manically! Quickly pick a number between 1 and 4 to defend yourself!'))
        else:
            print(dedent(f'Suddenly {the_murderer.name} is in front of you with {the_murderer.weapon}! Quickly pick a number between 1 and 4 to defend yourself!'))
        
        user_num = input('> ')
        rand_num = randint(1, 4)

        if user_num == str(rand_num):
            print(f'Your quick thinking allowed you to stave off {the_murderer.name}\'s attack. Now, gather everyone in the living room and tell them who the murderer is.\n')
            return 'accusation'
        else:
            print(f'You try to fight off {the_murderer.name} but aren\'t quite quick enough.')
            return 'player death'

    def next_room_selector(self, chars, action):

        # Handles multiple user requests for notes or interact. Avoids duplicate prompts that were being caused by else statement at bottom of method.
        if 'interact' in action or 'notes' in action:
            action = self.notes_interaction_handler(chars, action)
        
        # If user player is the only one left with the murderer, they lose
        if len(all_characters) == 2:
            return 'player death'
        
        if 'accus' in action.lower():
            return 'accusation'

        for room in self.room_options:
                if self.name in action.lower():
                    print(f'\nYou\'re already in the {self.name}!')
                    return self.enter()
                elif room.name in action.lower():
                    set_all_char_moves(action)
                    return room.name
                elif room.name.lower() not in action.lower():
                    continue
        else:
            print('\nEnter a room from the list above, interact with someone, or accuse someone.\n')
            action = input('> ')
            return self.next_room_selector(chars, action)

    # Update: Used to avoid improper returns due to recursion written into original code
    def notes_interaction_handler(self, chars, player_action):
        while 'interact' in player_action or 'notes' in player_action:
            if 'interact' in player_action:
                player_action = self.interactions(chars, player_action)
            elif 'notes' in player_action:
                player_action = notes(player_action)
        return player_action

    def room_descrip(self, is_weapon, formatted_names):
        if is_weapon == False:
            print(f'\nThe {self.name} is quiet, {formatted_names} in there with you, and the room has no weapon. If only you could remember whether it had one to begin with...')
        else:
            print(f'\nThe {self.name} is quiet, {formatted_names} in there with you, and {self.weapon} hangs on the wall.')
    
    def room_weapon_check(self):
        return self.weapon != None

class Accusation:
    def __init__(self, murderer, characters):
        self.murderer = murderer
        self.characters = characters

    def enter(self):
        global accuse_count

        for room in all_rooms:
            room.characters.clear()

        self.characters = all_characters

        for char in self.characters:
            char.set_current_room(living_room)
            living_room.characters.append(char)

        str_char_names = []
        for char in self.characters[:]:
            if char.name != 'you':
                str_char_names.append(char.name)
            else:
                continue

        joined_names = ', '.join(str_char_names[0:len(str_char_names)-1]) + ' and ' + str_char_names[-1]
        print(dedent(f'{joined_names} have gathered in the living room... it is time to make your accusation.'))

        # Limits number of accusals user player can make
        if accuse_count == 2:
            print(dedent(f'''
            Everyone stands in a circle to hear what you have to say when suddenly {the_murderer.name} jumps towards you and begins to attack you!
            The others try to hold {the_murderer.name} back, but it is too late. You started to ask too many questions and paid the ultimate price...\n''')) 
            print(dedent('Better luck next time.'))
            exit()
        
        accused = input('\nWho do you accuse? > ')

        # Handles random names in input
        while accused.capitalize().strip() not in str_char_names:
                print('\nPlease enter the name of who you would like to accuse.')
                accused = input('Who do you accuse? > ')
        
        if accused.capitalize() == self.murderer.name:
            print(dedent(f'''
            Everyone turns in shock to stare at {accused.capitalize()}, but {accused.capitalize()} just glares at you
            and says, "I could\'ve gotten away with it if you weren\'t here."'''))

            print(dedent(f'''
            Soon after, the police arrive to take {accused.capitalize()} away. Thanks to your sharp wits and
            quick thinking, you managed to save the rest of your friends!'''))

            print(f'\nCongratulations on solving the mystery {player_name}!')
        else:
            print(f'\n{accused.capitalize()} is offended you would suggest such a thing. But the real killer knows you\'re on their trail... you better watch your back.')
            accuse_count += 1
            return 'living room'

class PlayerDeath:
    def __init__(self, weapon, murderer):
        self.weapon = weapon
        self.murderer = murderer

    def enter(self):
        if the_murderer.weapon == 'their bare hands' or the_murderer.weapon == None:
            if len(all_characters) == 2:  # Used if murderer has killed all other players in game
                manner_of_death = f'''
                            Suddenly, you feel the cold chill of someone approaching behind you and hear a voice, "You\'re the last one left..."
                            You turn around and see {the_murderer.name} and smiling manically.
                            
                            It's too late, {player_name}. All your friends are dead.'''
            else:
                manner_of_death = f'\nThe last thing you see is {self.murderer.name} standing over you. The darkness is closing in...'
        else:
            if len(all_characters) == 2:
                manner_of_death = f'''
                            Suddenly, you feel the cold chill of someone approaching behind you and hear a voice, "You\'re the last one left..."
                            You turn around and see {the_murderer.name} holding {the_murderer.weapon} and smiling manically.
                            
                            It's too late, {player_name}. All your friends are dead.'''
            else:
                manner_of_death = f'\nThe last thing you see is {self.murderer.name} standing over you with {self.murderer.weapon}. The darkness is closing in...'
        print(dedent(manner_of_death))
        print(f'\nBetter luck next time...')



#############################################
# Engine, Map and all class instances and other info necessary for game are below this line.
#############################################

# Engine for game that enables room to room movement on map object that is passed in during instantiation
class Engine:
    def __init__(self, scene_map):
        self.scene_map = scene_map

    def play(self):

        print(dedent(
            f'''
        Welcome to Mansion Mystery, {player_name}.
        Everything seemed to be going well at the house party until one of your friends turned up dead.
        Now there is a killer on the loose and it is up to you to figure out who it is. Good luck. You'll need it...'''))

        game_end_player_death = PlayerDeath(the_murderer.weapon, the_murderer)
        
        # This is what runs the game... scene map is a map object
        current_scene = self.scene_map.opening_scene()
        while current_scene:
            if isinstance(current_scene, PlayerDeath):
                game_end_player_death.enter()
                break
            next_scene_name = current_scene.enter()
            current_scene = self.scene_map.return_scene(next_scene_name)

# Room instances and their weapons... empty lists are for room chars and next room options
# *Note* It doesn't seem like they need to be there, but if they aren't and I set the default lists to [] in Room  __init__
# I get a strange bug where everyone moves from the hallway to whatever you input as next room at the beginning of the game
hallway = Room('hallway', 'a broadsword', [], [])
kitchen = Room('kitchen', 'a kitchen knife', [], [])
living_room = Room('living room', 'a fire poker', [], [])
dining_room = Room('dining room', None, [], [])
garage = Room('garage', 'a baseball bat', [], [])
master_bed = Room('master bedroom', None, [], [])
master_bath = Room('master bathroom', None, [], [])
hall_bath = Room('hall bathroom', None, [], [])

# Adding room objects as next room options for each room
hallway.room_options = [kitchen, living_room, hall_bath, master_bed, dining_room]
kitchen.room_options = [hallway, dining_room, garage]
living_room.room_options = [dining_room, hallway]
dining_room.room_options = [kitchen, living_room, hallway]
garage.room_options = [kitchen]
master_bed.room_options = [hallway, master_bath]
master_bath.room_options = [master_bed]
hall_bath.room_options = [hallway]

# Instantiates all characters in game
player_name = input('\nWhat is your name? > ')
player = Character('you')
alexander = Character('Alexander')
clarissa = Character('Clarissa')
jonathan = Character('Jonathan')
kimberly = Character('Kimberly')
michael = Character('Michael')
lisa = Character('Lisa')
richie = Character('Richie')

# You (user player) not added yet to avoid being set as murderer
all_characters = [alexander, clarissa, jonathan, kimberly, michael, lisa, richie]

# Decides who the murderer is and sets their current weapon
the_murderer = all_characters[randint(0, len(all_characters)-1)]
the_murderer.murderer = True
the_murderer.weapon = 'their bare hands'

# User added here to avoid player being murderer
all_characters.append(player)

# Sets current room for all characters at beginning of game
for char in all_characters:
    char.current_room = hallway

player_death = PlayerDeath(the_murderer.weapon, the_murderer)
accusation = Accusation(the_murderer, all_characters)

all_rooms = [hallway, kitchen, living_room, dining_room, garage, master_bed, master_bath, hall_bath]

class Map:
    scenes = {
        'hallway': hallway,
        'kitchen': kitchen,
        'living room': living_room,
        'dining room': dining_room,
        'garage': garage,
        'master bathroom': master_bath,
        'master bedroom': master_bed,
        'hall bathroom': hall_bath,
        'player death': player_death,
        'accusation': accusation
    }

    def __init__(self, start_scene):
        self.start_scene = start_scene

    def opening_scene(self):
        return self.return_scene(self.start_scene)

    def return_scene(self, scene_name):
        val = Map.scenes.get(scene_name)
        return val

map = Map('hallway')
game = Engine(map)
game.play()