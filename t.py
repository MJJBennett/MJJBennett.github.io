"""
This is a simple python script meant to be used for templating HTML.

It will take .html or .htmlt files from ./src/html/ and insert HTML into them from ./resources/html/ and place them into ./
"""

import re
import json
from os import listdir, makedirs, walk
from os.path import isfile, join, isdir
import sys
import argparse
import datetime

out = print
err = print

def get_date():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%MPST")

class FileObject:
    def __init__(self, fileFrom = "", fileTo = ""):
        self.args = {}
        self.fileFrom = fileFrom
        self.fileTo = fileTo
        self.data = None
    def read(self):
        with open(self.fileFrom, "r") as file:
            self.data = file.read()
    def write(self):
        with open(self.fileTo, "w") as file:
            file.write(self.data)

def replace_with_args(main_str, var, replacement, args, number):
    # Here we need to do the following:
    # - Read the main_str and find where it declares something that should look like: var&arg=value
    # We need to replace $arg in 'replacement' with value, i.e.
    # in main_str: "...$HEADER&POS=4" => find the 4, replace $POS in "...<div style="...$POS"" with 4
    search_re = r'(' + re.escape(var) + r")(&[A-Z]*=[A-Za-z0-9\.\-]*)" # assumes 1 and only 1 variable
    for _ in range(0, number):
        to_replace = re.search(search_re, main_str)
        var_str = to_replace.groups()[1]
        first_var_str = var_str.split('&')[1].split('=')
        var_name = first_var_str[0]
        var_val = first_var_str[1]
        main_str = main_str.replace(to_replace.group(0), replacement.replace("$" + var_name, var_val, 1), number)

    # print(main_str)
    return main_str

def recurse_replace_file(config = {}):
    pass

def main(args):

    # Load config
    with open("./t.conf", 'r') as file:
        json_config = json.load(file)

    # Configure safemode
    if json_config["safe-mode"] > 0:
        if args.git:
            print("Error: Running from git hook while in safe mode. Exiting.")
            return
        safemode = True
    else:
        safemode = False

    # Configure debug (verbosity)
    if json_config["debug"] > 0 or args.verbose:
        verbose = True
    else:
        verbose = False
    
    build = 0 # deploy
    value_loc = "value"

    if not args.deploy and (args.local or json_config["default-build"] == "local"):
        build = 1
        value_loc = "local-value"
    
    if build == 0:
        print("Starting deploy build.")
    else:
        print("Starting local build.")


    # Configure html source directory
    html_dir = json_config["html-dir"]
    
    # Run templating system
    for (dirpath, dirnames, filenames) in walk(html_dir):
        print()
        if verbose:
            print("Values:: dirpath: " + dirpath + ", dirnames: " + str(dirnames) + ", filenames: " + str(filenames))
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
                if verbose:
                    print(" >> " + "Reading " + old_filename)
                with open(old_filename, 'r') as old_file:
                    file_data = old_file.read()

                # To get this working ASAP, we'll just hardcode the variable substitution.
                # Format is $VARIABLE: path_to_substitution_file
                variables = json_config["variables"]
                # variables = {"$HEADER": "resources/html/site-header.html"}

                for variable in variables:
                    # Find the variable's generic type
                    if variables[variable]["type"] == "file":
                        with open(variables[variable][value_loc], 'r') as replacement:
                            d = replacement.read()
                    elif variables[variable]["type"] == "text":
                        d = variables[variable][value_loc]
                    elif variables[variable]["type"] == "function":
                        d = globals()[variables[variable][value_loc]]()
                   
                    # Find out if there is an additional piece of data we need from the file
                    if "args" in variables[variable]:
                        args = variables[variable]["args"]
                        # variables[variable][arg] tells us whether the argument is required or not
                        # potentially additional information in the future, but for now this will do
                        if verbose:
                            print("Doing special replace-with-args for variable " + variable + " and args " + str(args))
                            print("Details: \nfile_data=" + file_data + "\nvariable=" + variable + "\nd=" + d)
                        file_data = replace_with_args(file_data, variable, d, args, variables[variable]["replace"])
                    else:
                        file_data = file_data.replace(variable, d, variables[variable]["replace"])

                file_data = file_data.replace("<!DOCTYPE html>", "<!DOCTYPE html>\n<!--WARNING: THIS FILE WAS GENERATED AUTOMATICALLY.\nIT MAY BE OVERWRITTEN AGAIN IN THE FUTURE.\nIT IS RECOMMENDED TO EDIT THE SOURCE AT {0}-->".format(old_filename), 1)

                if isfile(current_filename) and verbose:
                    print(" >> " + "Overwriting " + current_filename)
                with open(current_filename, 'w') as new_file:
                    new_file.write(file_data)
        except:
            err("Found an exception while dealing with " + current_filename + ":")
            raise

def parse_cli():
    parser = argparse.ArgumentParser(description='Templates and formats html files.')
    parser.add_argument('--local', dest='local', action='store_const',
                        const=True, default=False,
                        help='Generate files to access via localhost://')
    parser.add_argument('--deploy', dest='deploy', action='store_const',
                        const=True, default=False,
                        help='Generate files that use the internet.')
    parser.add_argument('--verbose', dest='verbose', action='store_const',
                        const=True, default=False,
                        help='Print additional debug messages.')
    parser.add_argument('--git', dest='git', action='store_const',
                        const=True, default=False,
                        help='Run in git mode.')

    parsed_args = parser.parse_args()
    return parsed_args

if __name__ == "__main__":
    version = "0.2"
    out("Running HTML templater version {0}".format(version))
    # Super simple testing setup
    main(parse_cli())
    # file = open("./src/html/blog/index.html", "r").read()
    # replace_with_args(file, "$HEADER", open("./resources/html/site-header.html", "r").read(), ["POS"], 1)
    print("\n")
