"""
This is a simple python script meant to be used for templating HTML.

It will take .html or .htmlt files from ./src/html/ and insert HTML into them from ./resources/html/ and place them into ./
"""

import re
import json
from os import listdir, makedirs, walk
from os.path import isfile, join, isdir

out = print
err = print

def main():
    f = []
    d = []
    safemode = True
    html_dir = './src/html/'
    for (dirpath, dirnames, filenames) in walk(html_dir):
        print("dirpath: " + dirpath + ", dirnames: " + str(dirnames) + ", filenames: " + str(filenames))
        current_dir = "./" + dirpath[len(html_dir):] + "/"
        current_filename = ""
        try:
            if not isdir(current_dir): 
                print(current_dir + " is not a directory, generating it.")
                makedirs(current_dir)
            print("Generating: " + str(filenames))
            for filename in filenames:
                current_filename = join(current_dir, filename)
                if isfile(current_filename) and safemode:
                    print("Warning: " + current_filename + "already exists. Overwrite? (Anything / n)")
                    ans = input()
                    if ans.lower() == 'n':
                        print("Skipping.")
                        continue
                old_filename = join(html_dir, join(dirpath, filename))
                print("\nReading " + old_filename)
                with open(old_filename, 'r') as old_file:
                    file_data = old_file.read()

                # To get this working ASAP, we'll just hardcode the variable substitution.
                variables = {"$HEADER": "resources/html/site-header.html"}

                for v in variables:
                    with open(variables[v], 'r') as replacement:
                        d = replacement.read()
                    file_data.replace(v, d)

                with open(current_filename, 'w') as new_file:
                    new_file.write(file_data)
        except:
            err("Found an exception while dealing with " + join(current_dir, current_filename) + ":")
            raise
        print("new path: " + dirpath[len(html_dir):] + ".")


    # Create the text file.
    print('\nGenerating text file: ')
    new_file = open('data/{0}.txt'.format(character), 'w+')
    new_file.close()

    # Copy template to the new file.
    print('> Copying template.txt to data/{0}.txt'.format(character))
    copyfile('template.txt', 'data/{0}.txt'.format(character))

    # Set the replacement strings.
    character_name = character
    character_description = char_desc.get_character_description(character_name)

    # Format the new file with the replacement strings.
    print('> Formatting data/{0}.txt'.format(character))
    with open('data/{0}.txt'.format(character), 'r') as file:
        data = file.read()

    with open('data.json', 'r+') as file:
        json_data = json.load(file)

    # Replace the target string
    data = data.replace('$NUM', str(json_data['lastDiscussion']))
    data = data.replace('$CHAR', character_name)
    data = data.replace('$UCHAR', character_name.replace(' ', '_'))
    data = data.replace('$DESC', character_description[0])
    data = data.replace('$LWS', json_data['lastPoll'])
    data = data.replace('$TWS', json_data['thisPoll'])
    data = data.replace('$RLS', relationship.get_character_relationship(character_name))
    data = data.replace('$PRCTG', str(get_percentage()))
    data = data.replace('$VER', GENERATOR_VERSION)

    # Write the file out again
    with open('data/{0}.txt'.format(character), 'w') as file:
        file.write(data)
    print('> Generated data/{0}.txt'.format(character))
if __name__ == "__main__":
    out("Running HTML templater.")
    main()
