#!/usr/bin/env python3
import argparse
import os
import sys
import yaml
from time import sleep


class AdventureGame:
    """
    A simple text adventure game engine with adventures constructed using YAML
    """

    maze = None
    current_room = None
    inventory = {}

    def __init__(self, game_file):
        self.maze, self.current_room = self.load_game(game_file)

    def load_game(self, game_file):
        """
        Load a new game from a yaml file
        """

        maze = {}
        start_room = None

        stream = open(game_file, 'r')
        data = yaml.safe_load(stream)

        start_room = data['start_room']
        for room in data['rooms']:
            maze_room = {}
            items = {}
            doors = {}
            monsters = {}

            maze_room['name'] = room['name']

            if 'welcome_message' in room:
                maze_room['welcome_message'] = room['welcome_message']
                if "show_welcome" in room:
                    maze_room['show_welcome'] = room['show_welcome']

            if 'show_help' in room:
                maze_room['show_help'] = room['show_help']

            maze_room['description'] = room['description']

            if 'emptyDescription' in room:
                maze_room['emptyDescription'] = room['emptyDescription']

            if 'type' in room:
                maze_room['type'] = room['type']

                # Make sure warp rooms have a duration set
                # and a destination
                if room['type'] == "warp":
                    if 'duration' in room:
                        maze_room['duration'] = room['duration']
                    else:
                        maze_room['duration'] = 10
                    if 'destination' in room:
                        maze_room['destination'] = room['destination']
                    else:
                        maze_room['destination'] = start_room

            # Load items in room
            if 'items' in room:
                for item in room['items']:
                    items[item['name']] = item
                maze_room['items'] = items

            # Load doors in room
            if 'doors' in room:
                for door in room['doors']:
                    doors[door['name']] = door
                maze_room['doors'] = doors

            # Load monsters in room
            if 'monsters' in room:
                for monster in room['monsters']:
                    monsters[monster['name']] = monster
                maze_room['monsters'] = monsters

            # Store processed room in maze
            maze[room['name']] = maze_room
        return maze, start_room

    def render_room(self, room):
        """
        Render the room for the user
        """

        message = ""
        description = f"{room['description']}\n"
        objects_string = ""
        doors_string = ""
        inventory_string = ""

        if "message" in room \
           and 'show_message' in room:
            if room['show_message']:
                message = f"\n{room['message']}\n"
                room['show_message'] = False

        if "show_help" in room:
            if room['show_help']:
                message += (
                    "Commands:\n"
                    "help - see this help\n"
                    "exit - quit game\n"
                )
                room['show_help'] = False

        if "items" in room:
            if room['items']:
                for item in room['items']:
                    if objects_string:
                        objects_string = f"{objects_string}, {item}"
                    else:
                        objects_string = f"{item}"

                objects_string = f"Objects you can see: {objects_string}\n"
            else:
                if "emptyDescription" in room:
                    description = f"{room['emptyDescription']}\n"

        if "doors" in room:
            if room['doors']:
                for doors in room['doors']:
                    if doors_string:
                        doors_string = f"{doors_string}, {doors}"
                    else:
                        doors_string = f"{doors}"

                doors_string = f"Doors: {doors_string}\n\n"

        if self.inventory:
            for item in self.inventory:
                if inventory_string:
                    inventory_string = f"{inventory_string}, {item}"
                else:
                    inventory_string = f"{item}"

            inventory_string = (
                "You are carrying the following items: "
                f"{inventory_string}\n"
            )

        # This is the final rendering of the room
        output = (
            f"{message}\n"
            "\n"
            f"{description}\n"
            f"{objects_string}\n"
            f"{doors_string}\n"
            f"{inventory_string}\n"
        )

        return output

    def process_input(self, user_input, room):
        """
        Process user input and take suitable action
        """

        action = ""
        item = ""
        input_list = user_input.split(maxsplit=1)
        if len(input_list) == 1:
            action = input_list[0]
        elif len(input_list) == 2:
            action, item = input_list

        current_room = room['name']
        run_game = True

        if action == "go":
            found_door = False
            if item in room['doors']:
                if "destination" in room['doors'][item]:
                    if room['doors'][item]['destination'] in self.maze:
                        found_door = True
                        door_open = True
                        if "open" in room['doors'][item]:
                            door_open = room['doors'][item]['open']
                        if door_open:
                            current_room = room['doors'][item]['destination']
                        else:
                            room['message'] = f"The path {item} is blocked"
                            room['show_message'] = True
            if found_door is False:
                room['message'] = f"You can not go {item}"
                room['show_message'] = True
        elif action == "help":
            room['message'] = "This message is not very helpful"
            room['show_message'] = True
        elif action == "exit":
            run_game = False

        return room, current_room, run_game

    def start(self):
        """
        Start a new adventure
        """

        os.system("clear")
        self.main()

    def main(self):
        """
        Main loop for game
        """

        run_game = True
        while run_game:
            room = self.maze[self.current_room]
            room_type = None
            print(self.render_room(room))

            if "type" in room:
                room_type = room['type']

            if room_type is None:
                user_input = input("\n> ")
                room, self.current_room, run_game = \
                    self.process_input(user_input, room)
                if self.current_room not in self.maze:
                    print("ERROR warping to non-existent room")
                    run_game = False
            elif room_type == "end":
                run_game = False
            elif room_type == "warp":
                self.current_room = room['destination']
                sleep(room['duration'])

            else:
                pass

            # Blank screen at the end of the loop
            if run_game:
                os.system("clear")


if __name__ == "__main__":

    game_file = ""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--game-file",
        type=str,
        help="Load adventure game",
        required=True)

    args = parser.parse_args()
    if args.game_file:
        game_file = args.game_file

    new_adventure = AdventureGame(game_file)
    new_adventure.start()
    sys.exit()
