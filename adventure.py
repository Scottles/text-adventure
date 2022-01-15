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
    combinable_items = {}

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
            maze_room['items'] = items
            if 'items' in room:
                for item in room['items']:
                    items[item['name']] = item
                maze_room['items'] = items
                if 'emptyDescription' in room:
                    maze_room['emptyWhenRemoved'] = items.copy()

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

            # Initialise room message
            maze_room['message'] = ""

            # Store processed room in maze
            maze[room['name']] = maze_room
        return maze, start_room

    def get_help_message(self):
        """
        Returns the help message
        """
        message = (
            "Commands:\n"
            "help - see this help\n"
            "go <direction> - Go in a given direction\n"
            "take <item> - take an item\n"
            "use <item> - Use an inventory item\n"
            "drop <item> - Drop a carried item in room\n"
            "exit - quit game\n"
        )
        return message

    def render_room(self, room):
        """
        Render the room for the user
        """

        message = ""
        description = ""
        objects_string = ""
        doors_string = ""
        inventory_string = ""
        room_type = ""

        if "type" in room:
            room_type = room['type']

        if "message" in room:
            if room['message'] != "":
                message = f"\n{room['message']}\n"
                room['message'] = ""

        if "show_help" in room:
            if room['show_help']:
                message += self.get_help_message()
                room['show_help'] = False

        room_empty = True
        if "items" in room:
            if room['items']:
                for item in room['items']:
                    if objects_string:
                        objects_string = f"{objects_string}, {item}"
                    else:
                        objects_string = f"{item}"

                objects_string = f"Objects you can see: {objects_string}\n"

            if "emptyWhenRemoved" in room:
                for room_item in room['emptyWhenRemoved']:
                    if room_item in room['items']:
                        room_empty = False
                        break

        if room_empty and "emptyDescription" in room:
            description = f"{room['emptyDescription']}\n"
        else:
            description = f"{room['description']}\n"

        if "doors" in room:
            if room['doors']:
                for door, values in room['doors'].items():
                    hidden = False
                    if 'hidden' in values:
                        hidden = values['hidden']
                    if not hidden:
                        if doors_string:
                            doors_string = f"{doors_string}, {door}"
                        else:
                            doors_string = f"{door}"

                doors_string = f"Doors: {doors_string}\n\n"

        if self.inventory and (room_type != "warp" and room_type != "end"):
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

        item = item.strip()
        current_room = room['name']
        run_game = True

        if action == "go" and item != "":
            found_door = False
            hidden = False
            if item in room['doors']:
                if 'hidden' in room['doors'][item]:
                    hidden = room['doors'][item]['hidden']
                if "destination" in room['doors'][item] and \
                   not hidden:
                    if room['doors'][item]['destination'] in self.maze:
                        found_door = True
                        door_open = True
                        if "open" in room['doors'][item]:
                            door_open = room['doors'][item]['open']
                        if door_open:
                            blocked_from_entering = False
                            if "blocks_entering" in room['doors'][item]:
                                for inv_item in self.inventory:
                                    if inv_item in room['doors'][
                                            item]['blocks_entering']:
                                        blocked_from_entering = True

                            if blocked_from_entering:
                                if "blocks_text" in room['doors'][item]:
                                    room['message'] = room['doors'][
                                        item]['blocks_text']
                                else:
                                    room['message'] = (
                                        "Something you carry prevents "
                                        "you entering"
                                    )
                            else:
                                current_room = room['doors'][
                                    item]['destination']
                        else:
                            path_blocked = False
                            if "keys" in room['doors'][item]:
                                if len(room['doors'][item]['keys']) > 0:
                                    room['message'] = \
                                        f"The {item} door is locked"
                                    if 'hint' in room['doors'][item]:
                                        room['message'] = (
                                            f"{room['message']}\n"
                                            f"{room['doors'][item]['hint']}"
                                        )
                                else:
                                    path_blocked = True
                            else:
                                path_blocked = True
                            if path_blocked:
                                room['message'] = \
                                    f"The {item} path is blocked"
            if found_door is False:
                room['message'] = f"You can not go {item}"
        elif action == "use" and item != "":
            if item in self.inventory:
                remove_item = False
                have_required_items = False
                item_used = False
                inventory_item = self.inventory[item]

                if "removeAfterUse" in inventory_item:
                    remove_item = inventory_item['removeAfterUse']

                if "requiredToUse" in inventory_item:
                    required_items = inventory_item['requiredToUse']
                    inv_items_required = len(required_items)
                    for inv_item in self.inventory:
                        if inv_item in required_items:
                            inv_items_required -= 1
                    if inv_items_required > 0:
                        have_required_items = False
                    else:
                        have_required_items = True
                else:
                    have_required_items = True

                if not have_required_items:
                    if "requiredToUseText" in inventory_item:
                        room['message'] = inventory_item['requiredToUseText']
                    else:
                        room['message'] = "You need another item to use this"
                else:
                    # use the item
                    # scan through closed doors
                    # to see if you can use item
                    for door, door_values in room['doors'].items():
                        if "keys" in door_values:
                            required_keys = len(door_values['keys'])
                            if item in door_values['keys']:
                                required_keys -= 1
                                door_values['keys'].remove(item)
                                item_used = True
                            if required_keys > 0:
                                room['message'] += (
                                    "A lock was disengaged on "
                                    f"{door_values['name']} door\n"
                                    f"{required_keys:.0f} locks remain\n"
                                )
                            else:
                                door_values['open'] = True
                                if 'hidden' in door_values:
                                    if door_values['hidden']:
                                        door_values['hidden'] = False
                                if 'useText' not in inventory_item:
                                    room['message'] += (
                                        f"The {door_values['name']} "
                                        "door opened\n"
                                    )
                                else:
                                    room['message'] += \
                                        f"{inventory_item['useText']}\n"
                if item_used and have_required_items and remove_item:
                    del self.inventory[item]
                elif not item_used and have_required_items:
                    if 'cannotUseText' in inventory_item:
                        room['message'] = f"{inventory_item['cannotUseText']}"
                    else:
                        room['message'] = f"You can not use the {item} here"
            else:
                singular_item = "a "
                if item[-1] == "s":
                    singular_item = "any "
                room['message'] = (
                    f"You are not carrying {singular_item}"
                    f"{item}"
                )
            pass
        elif action == "take" and item != "":
            if item in room['items']:
                take_item = True
                if "requiredToTake" in room['items'][item]:
                    required_items = room['items'][item]['requiredToTake']
                    inv_items_required = len(required_items)
                    for inventory_item in self.inventory:
                        if inventory_item in required_items:
                            inv_items_required -= 1
                    if inv_items_required > 0:
                        take_item = False
                        if "requiredToTakeText" in room['items'][item]:
                            room['message'] = \
                                room['items'][item]['requiredToTakeText']
                        else:
                            room['message'] = \
                                "Can't touch this"
                if take_item:
                    # Check if item is combinable and if so
                    # add to combinable item list
                    if "combines_with" \
                       and "combined_name" in room[
                           'items'][item]:
                        combined_name = room['items'][item]['combined_name']
                        self.combinable_items[combined_name] = {}
                        self.combinable_items[combined_name][
                            'parts_list'] = \
                            room['items'][item]['combines_with']
                        self.combinable_items[combined_name][
                            'parts_list'].append(item)
                        if "combined_item" in room['items'][item]:
                            self.combinable_items[combined_name].update(
                                room['items'][item]['combined_item']
                            )
                        if "combined_text" in room['items'][item]:
                            self.combinable_items[combined_name][
                                'combined_text'] = \
                                    room['items'][item]['combined_text']

                    if "takeText" in room['items'][item]:
                        room['message'] = \
                            f"{room['items'][item]['takeText']}"
                    else:
                        room['message'] = \
                            f"You take the {item}"
                    self.inventory[item] = room['items'][item]
                    del room['items'][item]
            else:
                singular_item = "is no "
                if item[-1] == "s":
                    singular_item = "are not any "
                room['message'] = (
                    f"There {singular_item}"
                    f"{item} here"
                )
        elif action == "drop" and item != "":
            if item in self.inventory:
                room['items'][item] = self.inventory[item]
                del self.inventory[item]
                room['message'] = f"You dropped the {item}"
            else:
                singular_item = "a "
                if item[-1] == "s":
                    singular_item = "any "
                room['message'] = (
                    f"You are not carrying {singular_item}"
                    f"{item}"
                )
        elif action == "help" or action == "":
            room['show_help'] = True
        elif action == "exit":
            run_game = False

        return room, current_room, run_game

    def combine_items(self, room):
        """
        Scans for combinable items in the inventory and combines
        them when possible
        """

        combined_items = []

        for item_name, item_values in self.combinable_items.items():
            collected_parts = 0
            for part in item_values['parts_list']:
                if part in self.inventory:
                    collected_parts += 1

            if collected_parts == len(item_values['parts_list']):
                # All parts collected. Remove parts from inventory and
                # store combined item in inventory
                for part in item_values['parts_list']:
                    del self.inventory[part]

                self.inventory[item_name] = item_values
                if "combined_text" in item_values:
                    if "message" in room:
                        message = item_values['combined_text']
                        if room['message'] != "":
                            room['message'] = f"{room['message']}\n{message}"
                        else:
                            room['message'] = message
                combined_items.append(item_name)

        # clean up combined items
        for item in combined_items:
            del self.combinable_items[item]

        return

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
                self.combine_items(room)
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
