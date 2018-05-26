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
    safemode = False
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
                    print("Warning: " + current_filename + " already exists. Overwrite? (Anything / n)")
                    ans = input()
                    if ans.lower() == 'n':
                        print("Skipping.")
                        continue
                old_filename = join(dirpath, filename)
                print("\nReading " + old_filename)
                with open(old_filename, 'r') as old_file:
                    file_data = old_file.read()

                # To get this working ASAP, we'll just hardcode the variable substitution.
                variables = {"$HEADER": "resources/html/site-header.html"}

                for v in variables:
                    with open(variables[v], 'r') as replacement:
                        d = replacement.read()
                    # print("Replacing " + v + " with:\n" + d + "\nin:\n" + file_data)
                    file_data = file_data.replace(v, d)
                    # print("\nResulting in:\n" + file_data)

                with open(current_filename, 'w') as new_file:
                    new_file.write(file_data)
        except:
            err("Found an exception while dealing with " + current_filename + ":")
            raise
        print("new path: " + dirpath[len(html_dir):] + ".")

if __name__ == "__main__":
    out("Running HTML templater.")
    main()
