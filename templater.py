#!/usr/bin/env python3

"""
New script for templating files.

Mechanism: Collect file objects, scrape for information, generate results, write out new files.
"""

import os

CONF = {
    'Directory': './',
    'Verbose': 'True',
    'Exclude Directories': ['.git', '.exclude']
}

class Configuration:
    def __init__(self, config_dict):
        self.directory = self.default(config_dict, 'Directory', './')
        self.do_write = self.default(config_dict, 'Verbose', 'False').lower() == 'true'
        self.exclude_dirs = self.default(config_dict, 'Exclude Directories', ['.git', '.exclude'])

    def default(self, d, k, default):
        return default if k not in d else d[k]

    def is_exclude_dir(self, directory):
        return directory in self.exclude_dirs

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

        for (dirpath, dirs, files) in os.walk(directory, topdown=True):
            dirs[:] = [d for d in dirs if not self.config.is_exclude_dir(d)]
            self.config.write(files)

    def get_files(self):
        return self.files

    def get_variables(self):
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
    for filename in collector.get_files():
        file_objects.append(FileObject(filename, config.new_filename(filename)))
    # We might have encountered a variables file
    variables = collector.get_variables()

    # We now have the files, generate the output
    # for file_object in file_objects:
