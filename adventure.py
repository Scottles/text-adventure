#!/usr/bin/env python

"""

 ==========================================
 ~~* A day in the Life of Boris Johnson *~~
 ==========================================


 This is a simple text adventure game staring Boris Johnson


 By Scott Hilleard and Geoffrey Hilleard

 Story written by: Geoffrey Hilleard

 """

import os

class Room:
    """ This class contains details about a room in the maze """
    _roomName = ""
    _roomDescription = ""
    _roomEmptyDescription = ""
    _roomItem = ""
    _doorOpen = True
    _openDoorItem = ""
    _openDoorMessage = ""

    def __init__(self, roomName, roomDescription, roomItem, openDoorItem):
        """ This initialises a room """
        # Set room name
        self._roomName = roomName

        # Set room description
        self._roomDescription = roomDescription

        # Item player can take, that is in the room
        self._roomItem = roomItem

        # Set the player inventory item required to proceed to next room
        self._openDoorItem = openDoorItem


    def setOpenDoorMessage(self, message):
        """ this sets the end message when you open a door """
        self._openDoorMessage = message

    def getOpenDoorMessage(self):
        """ get end message """
        return self._openDoorMessage

    def getRoomName(self):
        """ Return the name of the room """
        return self._roomName

    def setDescription(self, message):
        """ Change the description for the room """
        self._roomDescription = message

    def getDescription(self):
        """ This prints the room desscription """
        return self._roomDescription

    def setRoomEmptyDescription(self, message):
        """ Change the room empty description for the room """
        self._roomEmptyDescription = message

    def getRoomEmptyDescription(self):
        """ This prints the room empty desscription """
        return self._roomEmptyDescription

    def getRoomItem(self):
        """ get the name of the item in the room """
        return self._roomItem

    def setOpenDoorItem(self, newItem):
        """ change the item required to open a door """
        self._openDoorItem = newItem

    def getOpenDoorItem(self):
        """ Return the name of the name of the object required
        to open the door and proceed to next room """
        return self._openDoorItem

    def removeRoomItem(self):
        """ Removes an item from a room once taken """
        self._roomItem = "none"

    def getIsDoorOpen(self):
        """ check if the room has an open door """
        return self._doorOpen

    def setDoorOpen(self, doorState):
        """ open or close the rooms door """
        self._doorOpen = doorState

class SpecialItem:
    """ This class is used to define game items that either
    require you to have another item to pick them up, or require
    you to have another item to use """
    #_itemName = ""
    _itemRequiredToTake = ""
    _itemRequiredToUse = ""
    _removeAfterUse = False

    def __init__(self, itemRequiredToTake, itemRequiredToUse, removeAfterUse):
        """ initialise variables """
        #self._itemName = itemName
        self._itemRequiredToTake = itemRequiredToTake
        self._itemRequiredToUse = itemRequiredToUse
        self._removeAfterUse = removeAfterUse

    def getRequiredToTake(self):
        """ Returns the object required to take """
        return self._itemRequiredToTake

    def getRequiredToUse(self):
        """ Returns the object required to use """
        return self._itemRequiredToUse

    def getRemoveAfterUse(self):
        """ should object be removed after use """
        return self._removeAfterUse


def getInput():
    """ Get player input and return it """
    userInput = raw_input("\n> ")

    return userInput


def gotoRoom(maze, currentRoom, roomNo):
    """ go to a room number """

    roomNumber = currentRoom

    # ensure you do not try to go to a room greater than size of maze
    if (roomNo >= 0) and (roomNo <= (len(maze) - 1)):
        roomNumber = roomNo
    return maze[roomNumber]


def processInput(room, inventory, currentRoom, userInput):
    """ This processes the players input """

    # proceed to next room if set to true
    nextLevel = False

    # This contains the state of the level when input
    # has been processed
    levelState = {"inventory": inventory, "roomComplete": nextLevel}

    # convert user input to lower case
    userInput = userInput.lower()

    # split items in to a list and check there is a command an item
    # and then put the action in one variable
    # and the item in to another
    userInput = userInput.split()

    if len(userInput) < 2:
        print("Please enter an action and an item")
        return {"inventory": inventory, "roomComplete": nextLevel}

    userAction = userInput[0]
    userItem = userInput[1]


    # check user action
    if userAction == "take":
        # User takes an item
        # check item exitst in room
        if (userItem == room.getRoomItem()) and (userItem != "none"):

            # check if user is able to take item
            ableToTakeItem = True
            if specialItems.has_key(userItem):
                if specialItems[userItem].getRequiredToTake() == "":
                    # no prerequisite item required to take this item
                    ableToTakeItem = True
                else:
                    # special item required to take new item
                    if inventory.has_key(specialItems[userItem].getRequiredToTake()):
                        if inventory[specialItems[userItem].getRequiredToTake()] > 0:
                            # user has at least 1 prerequisite so take the item
                            ableToTakeitem = True
                        else:
                            ableToTakeItem = False
                    else:
                        # user does not have prerequisite item
                        ableToTakeItem = False
            else:
                ableToTakeItem = True

            if ableToTakeItem:
                if inventory.has_key(userItem):
                    inventory[userItem] += 1
                else:
                    inventory[userItem] = 1
                    
                room.removeRoomItem()
                print("You take the %s" % userItem)
            else:
                print("You require another item to take the %s" % userItem)

        else:
            print("You find no such item ( %s )" % userItem)

    elif userAction == "use":
        # User uses an item

        # check the item exists in the inventory
        if not inventory.has_key(userItem):
            print("You do not have this item in your posession ( %s )" % userItem)
            return {"inventory": inventory, "roomComplete": nextLevel}

        # check if they are carrying any of the items
        if (inventory[userItem] > 0):
            #print room.getOpenDoorItem()
            if (userItem == room.getOpenDoorItem()):
                print("You use the %s" % userItem)
                nextLevel = True
                room.setDoorOpen(True)
                room.setOpenDoorItem("none")
                if room.getOpenDoorMessage() != "":
                    print(room.getOpenDoorMessage())
            else:
                print("You can not use the %s here" % userItem)
        else:
            print("You do not have this item in your posession ( %s )" % userItem)
    elif userAction == "go":
        # user wishes to move
        if userItem == "back":
            return {"inventory": inventory, "roomComplete": nextLevel, "level_warp":(currentRoom - 1)}
        if userItem == "forward":
            if room.getIsDoorOpen():
                return {"inventory": inventory, "roomComplete": nextLevel, "level_warp":(currentRoom + 1)}
            else:
                print("The path ahead is blocked")
        else:
            print("Can not go %s" % userItem)

    #print inventory
        
    return {"inventory": inventory, "roomComplete": nextLevel}


# Create a small maze
maze = [Room("Living room", "You are in your house's living room. You can see a damaged grand father clock with documents stuck inside it.", "documents", "none"),
        Room("Garage", "You are standing next to a rack of Boris Bikes in your garage.", "bike", "bike"),
        Room("Street", "You are cycling through your street. You can see a tipped over bin with insecticide next to it.", "insecticide", "bike"),
        Room("thames river", "You are cycling by the thames river. You can see a shotgun floating in the river.", "shotgun", "bike"),
        Room("thames river2", "You enter a wooded area alongside the bike path. You can see a pair of gloves hanging from a beautiful tree", "gloves", "bike"),
        Room("Kens blockade", "You have reached the end of the bike path. Your way forward is blocked by an angry and foaming-at-the-mouth Ken Livingstone. You can see an old tree with damaged branches nearby.", "branch", "shotgun"),
        Room("outside office", "You are outside your boring, Mayor of London office. The door is locked. Your dumb receptionist left a bunch of junk on her desk again.", "key", "key"),
        Room("Mayor's office", "YOUR OFFICE HAS BEEN SWARMED BY ANGREH BEEZ!", "none", "insecticide"),
        Room("Robotnik appears", "You sat down and began twiddling your thumbs. You heard an explosion and looked out the window... Dr Robotnik is trying to invade London... again. You're rummaging through your filing cabinet ,looking for something to get rid of him.", "paperwork", "paperwork"),
        Room("Final", "The Prime minister has come to you saying that Europe is planning to start WW3 to destory England unless he finds the documents that has the money he owes Europe. You are searching your desk draws.", "clock-piece", "documents")
        ]
maze[0].setRoomEmptyDescription("You are in your house's living room. You can see a working grand father clock.")
maze[1].setDoorOpen(False)
maze[2].setRoomEmptyDescription("You are cycling along your street. You can see a tipped over bin.")
maze[3].setRoomEmptyDescription("You are cycling by the thames river.")
maze[4].setRoomEmptyDescription("You are in a wooded area next to the bike path. You can see a beautiful tree.")
maze[5].setDoorOpen(False)
maze[5].setOpenDoorMessage("\nCongratulations you have defeated the evil Ken Livingstone! London is safe.\n")
maze[5].setRoomEmptyDescription("You are at the end of the bike path.")
maze[6].setDoorOpen(False)
maze[6].setRoomEmptyDescription("You are outside your office.")
maze[7].setDoorOpen(False)
maze[7].setOpenDoorMessage("\nYou made those beez buzz off. Now you can sit down and do nothing, like usual.\n")
maze[7].setRoomEmptyDescription("You are in your boring old office.")
maze[8].setDoorOpen(False)
maze[8].setRoomEmptyDescription("Robotnik is gone. You're still in your boring old office.")
maze[8].setOpenDoorMessage("\nYou drone on and on about your boring paperwork. Dr Robotnik gets bored and leaves, deciding that taking over London wasn't a good idea.\n")


# This sets up special objects within the game
specialItems = {}
#itemRequiredToTake, itemRequiredToUse, removeAfterUse):
specialItems["shotgun"] = SpecialItem("branch", "shotgun-shells", False)
specialItems["shotgun shells"] = SpecialItem("", "", True)
specialItems["gloves"] = SpecialItem("branch", "", False)
specialItems["insecticide"] = SpecialItem("gloves", "", False)
specialItems["documents"] = SpecialItem("clock-piece", "", False)

# This is a dictionary that stores the players items
inventory = {}
# Put collectible items from rooms in inventory, with a count of 0
#for room in maze:
#    inventory[room.getRoomItem()] = 0


# clear the screen
os.system("clear")

# Print welcome message
print("\nWelcome Boris Johnson. You must fulfill your role as Mayor of London by getting to your office on time.\n")
print("\nCommands: \n\"take\" [object]\n\"use\" [object]\n\"go\" [forward|back]")

currentRoom = 0
room = maze[currentRoom]

# This loops through each room in the maze
#for room in maze:
while (currentRoom != 999):
   # print room description
    if room.getRoomEmptyDescription() == "" or room.getIsDoorOpen() == False or room.getRoomItem() != "none":
        print("\n%s" % room.getDescription())
        if  room.getRoomItem() != "none":
            print("Objects you can see: %s" % room.getRoomItem())
    elif room.getRoomEmptyDescription() != "":
        print("\n%s" % room.getRoomEmptyDescription())
    #else:
    #    print("\n%s" % room.getDescription())
        

    # When this is true proceed to next room
    nextRoom = False

    # print inventory
    #print(inventory)

    textItems = ""
    for key, value in inventory.iteritems():
        if value > 0:
            if textItems != "":
                textItems = "%s, %s" % (textItems, key)
            else:
                textItems = key

    if textItems != "":
        print("\nYou are carrying the following items: %s" % textItems)
    
    # do stuff things the player types
    output = {}
    userInput = getInput()

    # clear the screen after use has pressed enter, but before processInput
    # displays any messages
    os.system("clear")

    output = processInput(room, inventory, currentRoom, userInput)
    #print output
    inventory = output["inventory"]
    nextRoom = output["roomComplete"]

    # jump level is required
    if output.has_key("level_warp"):

        # Ensure currentRoom is not out of bounds
        if not ((output["level_warp"] < 0) or (output["level_warp"] > (len(maze) - 1))):
            nextRoom = False
            currentRoom = output["level_warp"]
            room = gotoRoom(maze, currentRoom, output["level_warp"])
        else:
            print("You can not go that way")


    if nextRoom == True:

        # end game if currentRoom is greated than number of rooms
        if currentRoom == (len(maze) - 1):
            currentRoom = 999
        else:
            # otherwise proceed to next room
            room = gotoRoom(maze, currentRoom, (currentRoom + 1))
            currentRoom +=1
            nextRoom = False


print("\nCongratulations! You have saved the Earth from total destruction and now you can relax in your Boris pool.\n")
