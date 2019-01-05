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