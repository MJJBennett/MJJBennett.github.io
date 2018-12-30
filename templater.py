#!/usr/bin/env python3

"""
New script for templating files.

Mechanism: Collect file objects, scrape for information, generate results, write out new files.
"""

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


if __name__ = "__main__":
    # Running the templating engine
