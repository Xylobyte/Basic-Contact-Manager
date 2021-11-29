""" 
A basic contact management program.
Author: Donovan Griego
File: final_contacts.py
Assignment: Final Project
Date: 11-29-2021
"""
import json
import os
import sys
import time
import shlex
from json.decoder import JSONDecodeError

VERSION = '1.0'
APPLICATION_NAME = 'Contacts Manager'
DEVELOPER = 'Donovan Griego'
DATE_CREATED = '2021-11-10'
SPLASH_SCREEN = True
CONTACTS_FILE = 'contacts.json'
CREDENTIALS_FILE = 'credentials.txt'
CONFIG_FILE = 'config.txt'
ALWAYS_SAVE_ON_EXIT = False
SETTINGS = {}
HELP = """
    Commands:
    'exit' to exit the application.
    'about' to display information about the application, developer name, date created, and version
    'info' to show the number of contacts, number of companies, and number of contacts per company
    'remove <contact(s)>' to remove a contact.
    'add' to add a contact.
    'group add' to add contacts to a group.
    'group remove' to remove a contact from a group.
    'group members' to list all contacts in a group.
    'group list' to list all groups.
    'list contacts' to list all contacts.
    'list groups' to list all groups.
    'search <query>' to search for contacts.
    'group create' to create a group.
    'group delete' to delete a group.
    'load <filename>' loads contacts from a file.
    'save' to save the contacts to the default file.
    'export <filename>' to export the contacts to a file.
    'commands <filename>' load a set of commands from a file. Should prompt for the file name. Should warn if the file does not exist.
    'help' to display a list of commands.

    Config:
    'DISABLE_SPLASH_SCREEN' to disable the splash screen.
    'ALWAYS_SAVE_ON_EXIT' to always save the contacts file when exiting.
    'CONTACTS_FILE' to set the contacts file name.
"""
DATA = {}
CONTACTS = []
COMPANIES = {}
GROUPS = {}

class Contact:
    """A contact class.
    """
    id = ''
    name = ''
    phone = ''
    email = ''
    company = ''
    notes = ''
    groups = []
    def add_group(self, group):
        self.groups.append(group)
    
    def remove_group(self, group):
        self.groups.remove(group)
    
    def __init__(self, id, name, phone, email, company, notes, groups):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.company = company
        self.notes = notes
        self.groups = groups

    def __str__(self):
        return f"{self.name} ({self.phone})"

def print_contacts(cts):
    """Print the contacts in a list. With column headers and tabs in between
    """
    print("\n{:<10}{:<20}{:<20}{:<20}{:<20}{:<20}{:<20}".format("ID", "Name", "Phone", "Email", "Company", "Notes", "Groups"))
    for ct in cts:
        print("{:<10}{:<20}{:<20}{:<20}{:<20}{:<20}".format(ct.id, ct.name, ct.phone, ct.email, ct.company, ct.notes, ct.groups))
    print("\n")

def print_companies():
    """Print the companies in a list and the number of contacts per company.
    """
    print("\n{:<20}{:<20}".format("Company", "# of Contacts"))
    for c in COMPANIES:
        print("{:<20}{:<20}".format(c, len(COMPANIES[c])))

def print_groups():
    """Print the groups in a list and the number of contacts per group.
    """
    print("\n{:<20}{:<20}".format("Group", "# of Contacts"))
    for g in GROUPS:
        print("{:<20}{:<20}".format(g, len(GROUPS[g])))

def get_contact_by_id(id):
    """Get a contact by id.

    Args:
        id (str): The identifier of the contact.

    Returns:
        contact (Contact): The contact object.
    """
    if type(id) == list:
        results = []
        for ct in id:
            results.append(get_contact_by_id(ct))
        return results
    for ct in CONTACTS:
        if ct.id == id:
            return ct
    return None

def yorn_prompt(prompt, default="y", show_proceed=True):
    print(prompt)
    default = {"y": True, "n": False}[default.lower()]
    while True:
        print("{}({}/{})? ".format("Proceed " if show_proceed else "", "[y]" if default else "y", "[n]" if not default else "n"), end="")
        response = input().lower()
        if response == "":
            return default
        elif response[0] == "y":
            return True
        elif response[0] == "n":
            return False
        else:
            print("Invalid choice: {}".format(response))

def search(search_terms, fields = 'all', advanced=False):
    """Search for a contact.

    Args:
        search_term (str): The search term to search for.
    
    Returns:
        results (list): A list of contacts that match the search term.
    """

    results = []

    if fields[0] == 'all' and advanced:
        # search all fields for the search term
        for contact in CONTACTS:
            if search_terms[0].lower() in contact.id.lower():
                results.append(contact)
                continue
            if search_terms[0].lower() in contact.name.lower():
                results.append(contact)
                continue
            if search_terms[0].lower() in contact.phone.lower():
                results.append(contact)
                continue
            if search_terms[0].lower() in contact.email.lower():
                results.append(contact)
                continue
            if search_terms[0].lower() in contact.company.lower():
                results.append(contact)
                continue
            if search_terms[0].lower() in contact.notes.lower():
                results.append(contact)
                continue
            for group in contact.groups:
                if search_terms[0].lower() in group.lower():
                    results.append(contact)
                    continue
    # Refine search results by fields specified. Only keep results that match the search term in the specified field.
    if len(fields) > 1 and advanced:
        for i in range(1, len(fields)):
            # If the value is not found in the specified field, remove the contact from the results.
            if fields[i] == 'id':
                for contact in results:
                    if search_terms[i] != contact.id:
                        results.remove(contact)
            if fields[i] == 'name':
                for contact in results:
                    if search_terms[i].lower() not in contact.name.lower():
                        results.remove(contact)
            if fields[i] == 'phone':
                for contact in results:
                    if search_terms[i].lower() not in contact.phone.lower():
                        results.remove(contact)
            if fields[i] == 'email':
                for contact in results:
                    if search_terms[i].lower() not in contact.email.lower():
                        results.remove(contact)
            if fields[i] == 'company':
                for contact in results:
                    if search_terms[i].lower() not in contact.company.lower():
                        results.remove(contact)
            if fields[i] == 'notes':
                for contact in results:
                    if search_terms[i].lower() not in contact.notes.lower():
                        results.remove(contact)
            if fields[i] == 'groups':
                for contact in results:
                    for group in contact.groups:
                        if search_terms[i].lower() in group.lower():
                            break
                        else:
                            results.remove(contact)
    if not advanced:
        # Join the search terms together and search for them in the name, phone, email, company, and notes fields.
        search_term = " ".join(search_terms)
        for contact in CONTACTS:
            if search_term.lower() in contact.id.lower():
                results.append(contact)
                continue
            if search_term.lower() in contact.name.lower():
                results.append(contact)
                continue
            if search_term.lower() in contact.phone.lower():
                results.append(contact)
                continue
            if search_term.lower() in contact.email.lower():
                results.append(contact)
                continue
            if search_term.lower() in contact.company.lower():
                results.append(contact)
                continue
            if search_term.lower() in contact.notes.lower():
                results.append(contact)
                continue
            for group in contact.groups:
                if search_term.lower() in group.lower():
                    results.append(contact)
                    continue
        

    return results

def generate_contact_id():
    """Generate a unique identifier for a contact.

    Returns:
        identifier (str): A unique identifier.
    """
    id = ''
    for i in range(0, 5):
        id += str(time.time())[-1]
    return id

def contacts_dict_to_list(contact_dict):
    """Convert the contacts dictionary to a list of contact objects.
    """
    for contact in contact_dict:
        c = Contact(contact['id'], contact['name'], contact['phone'], contact['email'], contact['company'], contact['notes'], contact['groups'])
        CONTACTS.append(c)
        if c.company != '':
            if c.company not in COMPANIES:
                COMPANIES[c.company] = []
            COMPANIES[c.company].append(c)
        for g in c.groups:
            if g not in GROUPS:
                GROUPS[g] = []
            GROUPS[g].append(c)

def contacts_list_to_dict(contact_list):
    """Convert the contacts list to a dictionary of contact objects.
    """
    converted_contacts = []
    for contact in contact_list:
        c = {
            'id': contact.id,
            'name': contact.name,
            'phone': contact.phone,
            'email': contact.email,
            'company': contact.company,
            'notes': contact.notes,
            'groups': contact.groups
        }
        converted_contacts.append(c)
    return converted_contacts

def load_contents(filename):
    """Load the contacts file from CONTACTS_FILE.
    """

    # Load data from file
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            
            # Check if the file is in the correct format, if not then show an error message and continue.
            try:
                data = json.load(f)
                CONTACTS = contacts_dict_to_list(data['contacts'])
            except JSONDecodeError:
                print("Error: The file is not in the correct format.")
                return
        return True
    else:
        print(f"No contacts file was found for '{CONTACTS_FILE}'")
        return False

def save_contents(filename):
    """Save the contacts file to a JSON file.
    """
    with open(filename, 'w') as f:
        data = {
            'contacts': contacts_list_to_dict(CONTACTS)
        }
        json.dump(data, f, indent=4)

def fix():
    """Delete duplicate contacts and empty groups/companies.
    """
    for contact in CONTACTS:
        for c in CONTACTS:
            if contact != c and contact.id == c.id:
                CONTACTS.remove(c)
    for group in GROUPS:
        for c in GROUPS[group]:
            if c not in CONTACTS:
                GROUPS[group].remove(c)
    for company in COMPANIES:
        for c in COMPANIES[company]:
            if c not in CONTACTS:
                COMPANIES[company].remove(c)

def splash():
    """Print a startup splash screen with the application name and version.
    Basic ascii art is used to display the application name and version.

    """
    if not SPLASH_SCREEN:
        return
    print("""
    ██████╗███╗   ███╗
    ██╔════╝████╗ ████║
    ██║     ██╔████╔██║
    ██║     ██║╚██╔╝██║
    ╚██████╗██║ ╚═╝ ██║
    ╚═════╝╚═╝     ╚═╝
   """)
    print(f"{APPLICATION_NAME} v{VERSION}\n")

def execute_commands(command_list):
    """Execute a list of commands.
    """
    for c in range(0, len(command_list)):
        line  = command_list[c].strip()
        print(f"Executing command: {line}")
        words = line.split()
        if words[0] == 'add':
            sub_commands = ['name', 'phone', 'email', 'company', 'notes', 'groups']
            name = ""
            phone = ""
            email = ""
            company = ""
            notes = ""
            groups = []
            for i in range(c+1, len(command_list)):
                line = command_list[i]
                words = line.replace(':', '').split()
                
                if words[0] not in sub_commands:
                    break
                if words[0] == 'name':
                    name = " ".join(words[1:])
                if words[0] == 'phone':
                    phone = " ".join(words[1:])
                if words[0] == 'email':
                    email = " ".join(words[1:])
                if words[0] == 'company':
                    company = " ".join(words[1:])
                if words[0] == 'notes':
                    notes = " ".join(words[1:])
            contact = Contact(generate_contact_id(), name, phone, email, company, notes, groups)
            CONTACTS.append(contact)
        elif words[0] == 'remove':
            query = words[1:]
            results = search(query)
            if len(results) == 1:
                print(f"Removing contact '{results[0].name}'")
                print_contacts(results)
                CONTACTS.remove(results[0])
                print("Contact removed.")
            elif len(results) > 1:
                print("Multiple contacts found:")
                print_contacts(results)
                print("Removing mutliple contacts is not supported in this mode.")
                print("No contacts removed.")
            else:
                print("No contacts found.")
            


def main_loop():
    """The main loop of the program.
    """
    global CONTACTS_FILE
    global GROUPS
    global CONTACTS
    dataset = []
    commands_log = []
    while True:
        command = input('> ')
        commands_log.append(command)
        command = shlex.split(command)
        if len(command) == 0:
            continue

        if command[0] == 'load':
            if len(command) == 1:
                print('Please specify a file name.')
                continue
            filename = command[1]
            if load_contents(filename):
                CONTACTS_FILE = filename
                print(f"Loaded contacts from '{filename}'.")
                if yorn_prompt('Always load this file when starting the program?'):
                    # Check if a contact file setting already exists.
                    if "contacts_file" in SETTINGS:
                        print("Setting has been overridden in config file. Please edit 'contacts_file' in the config file to change this setting.")
                    else:
                        SETTINGS['contacts_file'] = filename
                        with open(CONFIG_FILE, 'a') as f:
                            f.write(f"\ncontacts_file={filename}")
        elif command[0] == 'group':
            if len(command) == 1:
                print('Usage: group <add|remove> <group_name> <contact>')
                continue
            if command[1] == 'add':
                if len(command) < 4:
                    print('Usage: group add <group_name> <contact>')
                    continue
                group_name = command[2]
                contact = command[3]
                contact = search(contact)
                print(contact)
                if len(contact) == 1:
                    contact = contact[0]
                    if group_name not in GROUPS:
                        GROUPS[group_name] = []
                    if contact not in GROUPS[group_name]:
                        GROUPS[group_name].append(contact)
                        print(f"Added '{contact.name}' to group '{group_name}'.")
                    else:
                        print(f"Contact '{contact.name}' is already in group '{group_name}'.")
                elif len(contact) > 1:
                    print("Multiple contacts found:")
                    print_contacts(contact)
                    print("Please specify a single contact.")
                    print("No contacts added.")
                else:
                    print("No contacts found.")
            elif command[1] == 'remove':
                if len(command) < 4:
                    print('Usage: group remove <group_name> <contact>')
                    continue
                group_name = command[2]
                contact = command[3]
                contact = search(contact)
                if len(contact) == 1:
                    contact = contact[0]
                    if group_name in GROUPS:
                        if contact in GROUPS[group_name]:
                            GROUPS[group_name].remove(contact)
                            print(f"Removed '{contact.name}' from group '{group_name}'.")
                        else:
                            print(f"Contact '{contact.name}' is not in group '{group_name}'.")
                    else:
                        print(f"Group '{group_name}' does not exist.")
                elif len(contact) > 1:
                    print("Multiple contacts found:")
                    print_contacts(contact)
                    print("Please specify a single contact.")
                    print("No contacts removed.")
                else:
                    print("No contacts found.")
            else:
                print('Usage: group <add|remove> <group_name> <contact>')
            fix()
        elif command[0] == 'save':
            save_contents(CONTACTS_FILE)
        elif command[0] == 'export':
            if len(command) == 1:
                print('Please specify a file name.')
                continue
            filename = command[1]
            save_contents(filename)
        elif command[0] == 'commands':
            if len(command) == 1:
                print('Please specify a file name.')
                continue
            filename = command[1]
            with open(filename, 'r') as f:
                commands = f.readlines()
                execute_commands(commands)          
        elif command[0] == 'fix':
            fix()
        elif command[0] == 'about':
            print('------------------------------')
            print('About')
            print(f"{APPLICATION_NAME} v{VERSION}\n")
            print('Last updated: 11-28-2021')
            print('Author:  Dnovan Griego')
            print('------------------------------\n')
        elif command[0] == 'info':
            print('------------------------------')
            print('Info')
            print('Contacts: ', len(CONTACTS))
            print('Companies: ', len(COMPANIES))
            print_companies()
            print('\nGroups: ', len(GROUPS))
            print_groups()
            print('------------------------------\n')
        elif command[0] == 'exit' or command[0] == 'quit':
            if not ALWAYS_SAVE_ON_EXIT:
                if yorn_prompt("Save changes before exiting?", show_proceed=False):
                    save_contents(CONTACTS_FILE)
            else:
                save_contents(CONTACTS_FILE)
            print("Goodbye!")
            break
        elif command[0] == 'search':
            if len(command) == 1:
                print('Usage: search <search term>')
                continue
            query = command[1:]
            results = search(query)
            print(f"Search results for '{query[0]}':")
            print_contacts(results)

            ### Deprecated ###

            # get search terms and possible filed indicated by a '-' prefix
            # First term is always searched in all fields
            # if len(command) == 1:
            #     query = input('Query: ')
            # else:
            #     query = command[1:]
            # search_terms = []
            # fields = []
            # # If first term is a '-' prefix, search only in the specified fields. Otherwise search in all fields then check for '-' prefixes
            # if query[0][0] != '-':
            #     search_terms.append(query[0])
            #     fields.append('all')
            #     query = query[1:]
            
            # for term in query:
            #     if term[0] == '-':
            #         fields.append(term[1:])
            #         print(f"field {term[1:]} at index {fields.index(term[1:])}")
            #     else:
            #         search_terms.append(term)
            #         print(f"search term {term} at index {search_terms.index(term)}")
            # results = search(search_terms, fields)
            # print_contacts(results)
        elif command[0] == 'add':
            contact = Contact(generate_contact_id(), '', '', '', '', '', [])
            contact.id = generate_contact_id()
            contact.name = input('Name: ')
            contact.phone = input('Phone: ')
            contact.email = input('Email: ')
            contact.company = input('Company: ')
            contact.notes = input('Notes: ')
            CONTACTS.append(contact)
            print(f"Added contact '{contact.name}'.")
            # Check for company
            if contact.company != '':
                if contact.company not in COMPANIES:
                    COMPANIES[contact.company] = [contact]
                else:
                    COMPANIES[contact.company].append(contact)
        elif command[0] == 'remove':
            if len(command) == 1:
                print('Usage: remove <contact>')
                continue
            query = command[1:]
            results = search(query)
            if len(results) == 1:
                print_contacts(results)
                if yorn_prompt("Are you sure you want to remove this contact?", default="n"):
                    CONTACTS.remove(results[0])
                    print("Contact removed.")
                else:
                    print("No contacts removed.")
            elif len(results) > 1:
                print("Multiple contacts found:")
                print_contacts(results)
                if yorn_prompt("Are you sure you want to remove these contacts?", default="n"):
                    for c in results:
                        CONTACTS.remove(c)
                    print("Removed contacts.")
                else:
                    print("No contacts removed.")
            else:
                print("No contacts found.")
        elif command[0] == 'edit':
            if len(command) == 1:
                print('Usage: edit <contact>')
                continue
            query = command[1:]
            results = search(query)
            if len(results) == 1:
                print_contacts(results)
                c = results[0]
                if yorn_prompt("Edit this contact?"):
                    c.name = input('Name [' + c.name + ']: ') or c.name
                    c.phone = input('Phone [' + c.phone + ']: ') or c.phone
                    c.email = input('Email [' + c.email + ']: ') or c.email
                    c.company = input('Company [' + c.company + ']: ') or c.company
                    c.notes = input('Notes [' + c.notes + ']: ') or c.notes
            elif len(results) > 1:
                print("Multiple contacts found:")
                print_contacts(results)
                print("Please narrow your search to one contact.")
            else:
                print("No contacts found.")
        elif command[0] == 'note' or command[0] == 'notes':
            if len(command) == 1:
                print('Usage: note <contact>')
                continue
            query = command[1:]
            results = search(query)
            if len(results) == 1:
                print_contacts(results)
                c = results[0]
                if yorn_prompt("Edit this contact?"):
                    c.notes = input('Notes [' + c.notes + ']: ') or c.notes
            elif len(results) > 1:
                print("Multiple contacts found:")
                print_contacts(results)
                print("Please narrow your search to one contact.")
            else:
                print("No contacts found.")
        elif command[0] == 'list':
            if len(command) == 1:
                print("Usage: list [contacts|groups]")
            else:
                if command[1] == 'contacts':
                    print_contacts(CONTACTS)
                elif command[1] == 'groups':
                    print_groups()
        elif command[0] == 'help':
            print(HELP)
        else:
            print('Unknown command.')



def boot():
    # loop through flags from command line
    global CONTACTS_FILE
    global CONFIG_FILE
    global ALWAYS_SAVE_ON_EXIT
    global SPLASH_SCREEN
    if len(sys.argv) > 1:
        for flag in sys.argv:
            if flag == '-f':
                # File flag with filename for contacts file
                CONTACTS_FILE = sys.argv[sys.argv.index(flag) + 1]

            if flag == '-v':
                print(VERSION)
                sys.exit()
    # Look for a config file
    if os.path.isfile(CONFIG_FILE):
        # Config file is just variable names and values separated by '='
        with open(CONFIG_FILE, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().replace(' ', '')
                if '=' in line:
                    var, val = line.split('=')
                    val = val.lower()
                    if var == 'contacts_file':
                        CONTACTS_FILE = val
                    elif var == 'commands_file':
                        COMMANDS_FILE = val
                    elif var == 'always_save_on_exit':
                        ALWAYS_SAVE_ON_EXIT = True if val == 'true' else False
                    elif var == 'splash_screen':
                        SPLASH_SCREEN = True if val == 'true' else False
                    else:
                        print(f'Unknown variable {var}')
                        continue
                    SETTINGS[var] = val
    # Then load the credentials file
    load_contents(CONTACTS_FILE)
    splash()
    # load_credentials()
    # Then load the contacts file
    # Main loop
    main_loop()



if __name__ == "__main__":
    boot()
