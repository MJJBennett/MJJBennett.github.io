#!/usr/bin/env python3

"""
New script for templating files.

Mechanism: Collect file objects, scrape for information, generate results, write out new files.
"""

# In order to keep this a single file, some helper functions 
# will be placed here (although they probably belong in other
# files instead, but I don't want to have to ever worry about
# import issues, ever) 42j

def lstrstrip(string_to_strip, strip_with):
    # https://stackoverflow.com/questions/3663450/
    # I was fairly surprised to find that there wasn't 
    # a standard way of doing this. Oh well.
    if string_to_strip.endswith(strip_with):
        return string_to_strip[:-len(strip_width)]
    return string_to_strip

# End helper functions

import os

CONF = {
    # All paths are relative to this directory
    'Directory': './',
    'Verbose': 'True',
    'Exclude Directories': ['.git', '.exclude'],
    'Source Directory': 'website-src',
    'Remove Extensions': ['.template']
}

class Configuration:
    def __init__(self, config_dict):
        # Working directory
        self.directory = os.path.abspath(self.default(config_dict, 'Directory', './'))
        # Whether or not write() should print anything
        self.do_write = self.default(config_dict, 'Verbose', 'False').lower() == 'true'
        # Directories that should be ignored while processing
        self.exclude_dirs = self.default(config_dict, 'Exclude Directories', ['.git', '.exclude'])
        # Directories where we can find our source files - these will be translated to be placed in the working directory        
        self.source_dir = os.path.abspath(self.default(config_dict, 'Source Directory', './source'))
        # Extensions that should be removed from the filenames
        self.remove_exts = self.default(config_dict, 'Remove Extensions', ['.remove', '.template'])

    def new_filename(self, filename):
        """
        This function takes a filename and returns it with the 
        extension removed. e.g. blog/index.html.template 
        should be placed into working_directory/blog/index.html
        """

        for remove_ext in self.remove_exts:
            filename = lstrstrip(filename, remove_ext)

        return os.path.abspath(filename)

    def source_filename(self, filename):
        """
        This function takes a filename and returns it with the
        source directory appended.
        """

        return os.path.abspath(os.path.join(self.source_dir, filename))

    def default(self, d, k, default):
        return default if k not in d else d[k]

    def is_exclude_dir(self, directory):
        return directory in self.exclude_dirs

    def is_variable_file(self, filename):
        return False

    def write(self, *args, **kwargs):
        if self.do_write:
            print(*args, **kwargs)

    def join(self, *args):
        for fa in args:
            if fa.startswith(self.directory):
                return os.path.join(*args)
            return os.path.join(self.directory, *args)

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

    def fmt_data(self, sort_of_pretty = True):
        if sort_of_pretty:
            return (
                "{ FileObject : \n\t{ infile: " + 
                os.path.relpath(self.infile) + 
                " }, \n\t{ outfile: " + 
                os.path.relpath(self.outfile) + 
                " } \n}"
                )
        return (
                "{ FileObject : { infile: " + 
                self.infile + 
                " }, { outfile: " + 
                self.outfile + 
                " } }" 
                )

class Collector:
    """
    This class is used to collect all the filenames to template.
    """
    def __init__(self, configuration):
        self.config = configuration
        self.variables = {}
        self.files = []

    def collect_files(self):
        self.config.write('Collecting files from directory:', self.config.source_dir)
        # for d in self.config.source_dirs:
        self._collect_files(self.config.source_dir)

    def _collect_files(self, directory):
        for (dirpath, dirs, files) in os.walk(directory, topdown=True):
            dirs[:] = [ d for d in dirs if not self.config.is_exclude_dir(d) ]
            current_dir = os.path.relpath(dirpath, directory)
            self._collect([ os.path.join(current_dir, f)  for f in files ])

    def _collect(self, files):
        # Collect files into either self.files or self.variables
        for filename in files:
            if self.config.is_variable_file(filename):
                self._collect_variables(filename)
            else:
                self.files.append(filename)

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

    config.write(collector.get_files())

    # Create the fileobjects to wrap the filenames for the template files
    file_objects = []
    for filename in collector.get_files():
        file_objects.append(FileObject(config.source_filename(filename), config.new_filename(filename)))
    # We might have encountered a variables file
    variables = collector.get_variables()

    for fo in file_objects:
        print(fo.fmt_data())

    # We now have the files, generate the output
    # for file_object in file_objects:
