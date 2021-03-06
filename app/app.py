"""

usage:
    app.py create_room (<room_name> <room_type> [-g=RG])...
    app.py add_person <first_name> <last_name> <gender> <person_type> [-w=WA]
    app.py load_people <file_name>
    app.py relocate_person <person_identifier> <new_room_name>
    app.py delete_room <room_name>
    app.py delete_person <person_id>
    app.py print_persons
    app.py print_allocation [-o=FN]
    app.py print_unallocated [-o=FN]
    app.py print_room <room_name>
    app.py save_state [-b=SQLD]
    app.py load_state <db_path>

option:
   -help -h                               Geting help on using the program
   -g RG, --rgender=RG                    To specify gender of Occupant of a living room
   -w WA, --wants_accom=WA                 An option argument to specify that person
                                          want accomodation
   -o FN, --option=FN                     Optional file name when printing to file
   -b SQLD --db=SQLD                      Database to load from the path provided

"""
from docopt import docopt
import pickle
import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.
    getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from app.allocation_db import AllocationDb
from app.amity import Amity
from app.exceptions import RoomIsFullError
from app.fellow import Fellow
from app.livingspace import LivingSpace
from app.office import Office
from app.roomallocation import RoomAllocation
from app.staff import Staff


def load_state():
    file_path = "roomallocation.p"
    if os.path.isfile(file_path):
        amity_object = pickle.load(open(file_path, "rb"))
        return RoomAllocation(amity_object)
    else:
        amity_object = Amity()
        return RoomAllocation(amity_object)


def save_state(room_allocation_obj):
    file_path = "roomallocation.p"
    pickle.dump(room_allocation_obj.amity, open(file_path, "wb"))


def add_person(args):
    first_name = args["<first_name>"]
    last_name = args["<last_name>"]
    gender = args["<gender>"]
    person_type = args["<person_type>"]
    wants_accom = "N"
    is_fellow = False
    if args["--wants_accom"]:
        wants_accom = args["--wants_accom"]
    name = first_name + " " + last_name
    roomallocation = load_state()
    person_type = person_type.lower()
    if person_type == "fellow":
        person = Fellow(name, gender, wants_accom)
        is_fellow = True
    elif person_type == "staff":
        person = Staff(name, gender)
    else:
        return "Invalid type: person can be fellow or staff"
    roomallocation.create_person(person)
    save_state(roomallocation)
    rooms = person.room_name
    message = ""
    if rooms.get('office'):
        message += first_name + " allocated to Office " + rooms.get('office') \
                              + "\n"
    else:
        message += "No available Office to allocate " + first_name + "\n"
    if is_fellow and rooms.get('livingspace'):
        message += first_name + " allocated to Living Space " \
                              + rooms.get('livingspace') + "\n"
    elif is_fellow and args["--wants_accom"] == "Y":
        message += "No available Living Space to allocate " + first_name + "\n"
    return message


def load_people(file_name):
    roomallocation = load_state()
    status = roomallocation.load_persons_from_text(file_name)
    save_state(roomallocation)
    return str(len(status)) + " added to Amity"


def create_room(args):
    rooms = get_room_values(args)
    roomallocation = load_state()
    message = "Room(s) created with Id (type): \n"
    for i, room in enumerate(rooms):
        room_name = room[0]
        room_type = room[1]
        if room_type.lower() == "livingspace":
            gender = room[2]
            room = LivingSpace(room_name, gender)
            status = roomallocation.create_room(room)
            if status:
                room_id = room.get_id()
        elif room_type.lower() == 'office':
            room = Office(room_name)
            status = roomallocation.create_room(room)
            if status:
                room_id = room.get_id()
        else:
            room_id = None
            status = None
        if status:
            message += room_id + " (" + room_type + ") \n"
        elif status is None:
            message += "Invalid room type for [" + room_name + " " + room_type\
                                                 + "]\n"
        else:
            message += "[Error] Room with name " + room_name + \
                       " already exit in Amity"
    save_state(roomallocation)
    return message


def relocate_person(person_identifier, new_room_name):
    new_room_name = new_room_name.lower()
    roomallocation = load_state()
    try:
        roomallocation.rellocate_person(person_identifier, new_room_name)
    except KeyError as err:
        return "{}".format(err)
    except RoomIsFullError as err:
        return "{}".format(err)
    except PersonInRoomError as err:
        return "{}".format(err)
    save_state(roomallocation)
    return "Person relocated to " + new_room_name


def print_allocation(file_name=False):
    allocation = load_state()
    if file_name:
        allocation.rmprint.print_allocation_to_file(file_name)
        return "Application printed to " + file_name
    else:
        return allocation.rmprint.build_allocation_string()


def print_unallocated(file_name=False):
    allocation = load_state()
    if file_name:
        allocation.rmprint.print_unallocated_to_file(file_name)
        return "Unallocated printed to " + file_name
    else:
        return allocation.rmprint.build_unallocation_string()


def print_room(room_name):
    allocation = load_state()
    try:
        return allocation.rmprint.print_room(room_name)
    except KeyError:
        return "Invalid room id supplied"


def save_state_to_db(db_path=None):
    if not db_path:
        db_path = "roomallocation.db"
    roomallocation = load_state()
    db = AllocationDb(db_path)
    roomallocation.save_to_database(db)
    return "Data Successfully saved to database"


def load_from_database(db_path):
    roomallocation = load_state()
    db = AllocationDb(db_path)
    roomallocation.load_from_database(db)
    save_state(roomallocation)
    return "Application State reload from database"


def get_room_values(args):
    j = 0
    rooms = []
    for i in range(len(args["<room_name>"])):
        room_name = args["<room_name>"][i]
        room_type = args["<room_type>"][i].lower()
        if room_type == "livingspace":
            gender = args["--rgender"][j]
            j += 1
            rooms.append([room_name, room_type, gender])
        else:
            rooms.append([room_name, room_type])
    return rooms


def delete(del_id, del_type):
    roomallocation = load_state()
    try:
        if del_type == "person":
            roomallocation.remove_person(del_id)
        else:
            roomallocation.remove_room(del_id)
        save_state(roomallocation)
    except KeyError:
        return "Invalid Id supplied"
    else:
        return del_id + " deleted from Amity"


def print_persons():
    roomallocation = load_state()
    return roomallocation.rmprint.print_persons()





def main(args):

    if args["add_person"]:
        print(add_person(args))
    elif args["create_room"]:
        print(create_room(args))
    elif args["load_people"]:
        print(load_people(args["<file_name>"]))
    elif args["relocate_person"]:
        person_identifier = args["<person_identifier>"]
        new_room_name = args["<new_room_name>"]
        print(relocate_person(person_identifier, new_room_name))
    elif args["print_allocation"]:
        if args["--option"]:
            print(print_allocation(args["--option"]))
        else:
            print(print_allocation())
    elif args["print_unallocated"]:
        if args["--option"]:
            print(print_unallocated(args["--option"]))
        else:
            print(print_unallocated())
    elif args["print_room"]:
        print(print_room(args["<room_name>"][0]))
    elif args["load_state"]:
        print(load_from_database(args["<db_path>"]))
    elif args["save_state"]:
        if args["--db"]:
            print(save_state_to_db(args["--db"]))
        else:
            print(save_state_to_db())
    elif args["delete_room"]:
        print(delete(args["<room_name>"][0], 'room'))
    elif args["delete_person"]:
        print(delete(args["<person_id>"], 'person'))
    elif args["print_persons"]:
        print(print_persons())
    else:
        print("use app.py --help to see usage")

if __name__ == '__main__':
    args = docopt(__doc__)
    main(args)
