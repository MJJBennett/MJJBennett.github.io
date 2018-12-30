#!/usr/bin/env python3

"""
New script for templating files.

Mechanism: Collect file objects, scrape for information, generate results, write out new files.
"""

import os

CONF = {
    'Directory': './',
    'Verbose': 'True'
}

class Configuration:
    def __init__(self, config_dict):
        self.directory = self.default(config_dict, 'Directory', './')
        self.do_write = self.default(config_dict, 'Verbose', 'False').lower() == 'true'

    def default(self, d, k, default):
        return default if k not in d else d[k]

    def write(self, *args, **kwargs):
        if self.do_write:
            print(*args, **kwargs)

class FileObject:
    """
    Class for abstracting away file object logic.
    """
    def __init__(self, in_filename, out_filename):
        # Load the file into memory
        with open(in_filename, 'r') as file:
            self.filedata = file.readlines()
        # Save io information
        self.infile = in_filename
        self.outfile = out_filename
    def get_data(self):
        return self.filedata
    def foreach(self, Function):
        for line in self.filedata:
            Function(line)
    def foreach_replace(self, Function):
        self.filedata = [ Function(x) for x in self.filedata ]

class Collector:
    """
    This class is used to collect all the filenames to template.
    """
    def __init__(self, configuration):
        self.config = configuration
        self.variables = {}
        self.files = []

    def collect_files(self):
        self.config.write('Collecting files from directory:', self.config.directory)
        directory = self.config.directory

        for (filenames, _, _) in os.walk(directory):
            print(filenames)

    def files(self):
        return self.files

    def variables(self):
        return self.variables
        

if __name__ == "__main__":
    # Running the templating engine

    # Create and parse the configuration
    config = Configuration(CONF)

    # Create a collector; find all files that need to be generated
    collector = Collector(config)
    collector.collect_files()

    # Create the fileobjects to wrap the filenames for the template files
    file_objects = []
    for filename in collector.files():
        file_objects.append(FileObject(filename, config.new_filename(filename)))
    # We might have encountered a variables file
    variables = collector.variables()

    # We now have the files, generate the output
    # for file_object in file_objects:
