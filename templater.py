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
        return string_to_strip[:-len(strip_with)]
    return string_to_strip

# End helper functions

import os, re

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

    def source_filepath(self, filename):
        """
        This function takes a filename and returns it with the
        source directory appended.
        """

        return os.path.abspath(os.path.join(self.source_dir, filename))

    def source_filename(self, filename):
        """
        This function takes a filename and returns it with the
        source directory appended.
        """

        return os.path.normpath(os.path.join(os.path.relpath(self.source_dir, self.directory), filename))

    def default(self, d, k, default):
        return default if k not in d else d[k]

    def is_exclude_dir(self, directory):
        return directory in self.exclude_dirs

    def is_variable_file(self, filename):
        return False

    def write(self, *args, **kwargs):
        if self.do_write:
            print(*args, **kwargs)

    def error(self, *args, **kwargs):
        print('ERROR:')
        print(*args, **kwargs)

    def err_msg(self, key):
        error_messages = {'err-msg-not-found': 'Error message not found.',
        'variable-files-not-supported': 'Variable files currently not supported.'}
        if key in error_messages:
            return error_messages[key]
        # This looks ridiculous but is just me thinking about localization
        return error_messages['err-msg-not-found'] + ': ' + key

    def join(self, *args):
        for fa in args:
            if fa.startswith(self.directory):
                return os.path.join(*args)
            return os.path.join(self.directory, *args)

class FileObject:
    """
    Class for abstracting away file object logic.
    """

    def __init__(self, in_filename, out_filename, name):
        # Save io information
        self.infile = in_filename
        self.outfile = out_filename
        self.name = name
        self.loaded = False
        self.data = None

    def fmt_data(self, sort_of_pretty = True):
        if sort_of_pretty:
            return (
                "{ FileObject : \n\t{ infile: " + 
                os.path.relpath(self.infile) + 
                " }, \n\t{ outfile: " + 
                os.path.relpath(self.outfile) + 
                " }, \n\t{ name: " + 
                os.path.relpath(self.name) + 
                " } \n}"
                )
        return (
                "{ FileObject : { infile: " + 
                self.infile + 
                " }, { outfile: " + 
                self.outfile + 
                " } }" 
                )

    def get_filedata(self):
        if not self.loaded:
            with open(self.infile) as file:
                data = file.read()
            return data
        return self.data

    def load_filedata(self):
        if not self.loaded:
            with open(self.infile) as file:
                self.data = file.read()
            self.loaded = True

class FileMetadataFSM():
    def __init__(self):
        self.lpos = -1
        self.esc = False
        self.inside = False
        self.in_str = False
        self.str_type = ''
        self.found_str = ''

        self.found_c1 = False

        self.STRING_CHARS = ['\'', '"']
        self.ESCAPE_CHAR = '\\'

    def soft_reset(self):
        # I guess this is sort of a hard reset...
        self.lpos = -1
        self.esc = False
        self.inside = False
        self.in_str = False
        self.found_c1 = False
        self.str_type = ''
        self.found_str = ''

    def search_remove(self, c1, c2, cend, search_string, verbose = False):
        for position in range(0, len(search_string) - 1):
            c = search_string[position]
            # If we encounter an escape char, we can invert our escape status
            if c == self.ESCAPE_CHAR:
                self.esc = not self.esc
                continue
            # We want to assume we are inside for the rest of this function
            # Handle outside here
            if not self.inside:
                # Early exit - we can ignore everything here
                if self.esc:
                    self.soft_reset()
                    continue
                if self.found_c1:
                    # Found the first character, need second right now
                    if c == c2:
                        self.inside = True
                        self.found_c1 = False # Reset this now
                        continue
                    # Did not find the second character
                    self.soft_reset()
                    continue

            # We know we are inside. Therefore, we want the next character, UNLESS
            # the next character is the terminating character. So handle that first.

            # Also, handle setting lpos here (where the string starts)
            if len(self.found_str) == 0:
                self.lpos = position - 1

            # If we encounter the end token, we're currently inside the search area
            # and we aren't escaped and we aren't in a string, we can end.
            if c == cend and not self.esc and not self.in_str:
                # We need to make sure we have all the information ready
                # That will be needed to do this again

                # This is the full search string with the part we don't want removed
                ret_str = search_string[:self.lpos] + search_string[position:]

                # This should be the full found string
                # self.found_str

                return ret_str

            # We know we are inside, and not ending here, take the next character.
            self.found_str += c

            # If we are inside the search area and we encounter a string character,
            # we should handle it appropriately if we are not currently escaped
            if c in self.STRING_CHARS and not self.esc and (not self.in_str or str(c) == self.str_type):
                if self.in_str:
                    # Because of the outer if statement, 
                    # we know that we have found the last string character
                    self.str_type = ''
                    self.in_str = False
                else:
                    # Becauise of the outer if statement,
                    # we know that we have found the first string character
                    self.str_type = str(c)
                    self.in_str = True
                continue
                
            

        # If we get here, something's gone wrong (or we just don't have a match)
        self.found_str = None
        if verbose:
            print('FSM ERROR(s):', '[Unterminated string]' if self.in_str else '',
            '[Unterminated expression at position ' + str(self.lpos) + ' ]' if self.inside else '')
        return None

    def get_result(self):
        return self.found_str
                


class FileMetadata(FileObject):
    def __init__(self, parent, config):
        super().__init__(parent.infile, parent.outfile, parent.name)
        self.config = config

        self.config.write("Processing file metadata for name:", self.name)
        self.load_filedata()

        self.parse()

    def parse(self):
        # This is just to get metadata about the file.
        # Metadata should be removed after.
        metadata_re = re.compile(r'\$\{ \
                                   (([^\}]*?(\3)[^\}\'\"]*)*?)\}')

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

    def _collect_variables(self, filename):
        self.config.error(self.config.err_msg("variable-files-not-supported"))

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
        print(filename)
        file_objects.append(FileObject(config.source_filepath(filename), config.new_filename(filename), config.source_filename(filename)))
    # We might have encountered a variables file
    variables = collector.get_variables()

    for fo in file_objects:
        config.write(fo.fmt_data())

    # This is a multi-pass parser
    # Each pass we get more information about the files
    simple_parsed_files = []
    
    for fo in file_objects:
       simple_parsed_files.append(FileMetadata(fo, config)) 

