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
    safemode = False
    html_dir = './src/html/'
    for (dirpath, dirnames, filenames) in walk(html_dir):
        print("\nValues:: dirpath: " + dirpath + ", dirnames: " + str(dirnames) + ", filenames: " + str(filenames))
        current_dir = "./" + dirpath[len(html_dir):] + "/"
        print("Copying to Directory: " + current_dir)
        current_filename = ""
        try:
            if not isdir(current_dir): 
                print(" > " + current_dir + " is not a directory, generating it.")
                makedirs(current_dir)
            print(" > " + "Generating: " + str(filenames))
            for filename in filenames:
                current_filename = join(current_dir, filename)

                # If safemode is on (generally something to manually enable while testing new changes)
                # the script will check before overwriting files
                if isfile(current_filename) and safemode:
                    print(" >> " + "Warning: " + current_filename + " already exists. Overwrite? (Anything / n)")
                    ans = input()
                    if ans.lower() == 'n':
                        print(" >> " + "Skipping.")
                        continue
                
                old_filename = join(dirpath, filename).replace("\\", "/")
                print(" >> " + "Reading " + old_filename)
                with open(old_filename, 'r') as old_file:
                    file_data = old_file.read()

                # To get this working ASAP, we'll just hardcode the variable substitution.
                # Format is $VARIABLE: path_to_substitution_file
                variables = {"$HEADER": "resources/html/site-header.html"}

                for v in variables:
                    with open(variables[v], 'r') as replacement:
                        d = replacement.read()
                    # print("Replacing " + v + " with:\n" + d + "\nin:\n" + file_data)
                    file_data = file_data.replace(v, d)
                    # print("\nResulting in:\n" + file_data)

                file_data = file_data.replace("<!DOCTYPE html>", "<!DOCTYPE html>\n<!--WARNING: THIS FILE WAS GENERATED AUTOMATICALLY.\nIT MAY BE OVERWRITTEN AGAIN IN THE FUTURE.\nIT IS RECOMMENDED TO EDIT THE SOURCE AT {0}-->".format(old_filename), 1)

                if isfile(current_filename):
                    print(" >> " + "Overwriting " + current_filename)
                with open(current_filename, 'w') as new_file:
                    new_file.write(file_data)
        except:
            err("Found an exception while dealing with " + current_filename + ":")
            raise

if __name__ == "__main__":
    version = "0.1"
    out("Running HTML templater version {0}".format(version))
    main()
    print("\n")
