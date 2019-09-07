# -*- coding: utf-8 -*-

import re

class Names():
    def __init__(self, list_of_names):
        self.names = list(list_of_names)

    def count(self):
        return len(self.names)
    
    def select_first_n(self, n):
        return Names(self.names[:n])
    
    def select_with_all_smalls(self):
        return Names([name for name in self.names if name == name.lower()])

    def select_with_all_caps(self):
        return Names([name for name in self.names if name == name.upper()])
    
    def select_starts_with_small(self):
        return Names([name for name in self.names if name[0] == name[0].lower()])
    
    def select_starts_with_cap(self):
        return Names([name for name in self.names if name[0] == name[0].upper()])
    
    def select_with_mixed_case(self):
        return Names([name for name in self.names if name != name.upper() and name != name.lower()])

    def select_with_not_all_caps(self):
        return Names([name for name in self.names if name != name.upper()])

    def select_with_underscore(self):
        return Names([name for name in self.names if '_' in name])

    def select_without_underscores(self):
        return Names([name for name in self.names if '_' not in name])

    def select_with_digits(self):
        digit = re.compile('\D*\d+\.*')
        return Names([name for name in self.names if digit.match(name) != None])

    def select_without_digits(self):
        digit = re.compile('\D*\d+\.*')
        return Names([name for name in self.names if digit.match(name) == None])
    
    def select_with_len_less_than(self, max_len):
        return Names([name for name in self.names if len(name) < max_len])
    
    def some_start_with_caps(self):
        for name in self.names:
            if name[0] == name[0].upper():
                return True
            
        return False
    
    def some_start_with_smalls(self):
        for name in self.names:
            if name[0] == name[0].lower():
                return True
            
        return False
    
    def some_have_humps(self):
        for name in self.names:
            if set(name[1:]).intersection(set('ABCDEFGHIJKLMNOPQESTUVWXYZ')):
                return True
            
        return False
    
    def some_have_underscores(self):
        for name in self.names:
            if '_' in name[1:]:
                return True
            
        return False
    
    def len_shortest(self):
        return min([len(name) for name in self.names])
    
    def len_longest(self):
        return max([len(name) for name in self.names])
    
    def len_average(self):
        return sum([len(name) for name in self.names]) / len(self.names)
    
    def __iter__(self):
        return self.names.__iter__()
    
    def __str__(self):
        return '\n'.join(self.names)
    
    def __repr__(self):
        ret_val = 'Names(['
        ret_val += ', '.join([repr(name) for name in self.names])
        ret_val += '])'
        return ret_val