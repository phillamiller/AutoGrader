# -*- coding: utf-8 -*-

import glob, os

import javalang # 3rd party library

# Returns a str containing the access modifier 
# ('public', 'private', 'protected' or '' <default>) 
def parse_access(modifiers):
    if 'public' in modifiers:
        return 'public'
    elif 'private' in modifiers:
        return 'private'
    elif 'protected' in modifiers:
        return 'protected'
    else:
        return '' # default

# Returns a str containing the full datatype 
# including square brackets for arrays
def parse_datatype(type_node):
    if type_node == None:
        return 'void'
    
    array_indexes = '[]'*len(type_node.dimensions)
    type_name = type_node.name + array_indexes
    return type_name

class JavaFile():
    def __init__(self, file_name):
        self.file_name = file_name
        self.classes = Classes()
        
        self.source = open(file_name, 'r').read()
        self.file_size = len(self.source)
        
        # source lines is 1-based (first line [index 0] is blank)
        self.source_lines = [''] + self.source.split('\n')
        
        self.tree = javalang.parse.parse(self.source)
        
        for path, node in self.tree.filter(javalang.tree.ClassDeclaration):
            self.classes.add(JavaClass(node, self))
    
    def get_all_class_names(self):
        return self.classes.get_names()
    
    def get_all_field_names(self):
        return self.classes.get_all_field_names()
    
    def get_all_method_names(self):
        return self.classes.get_all_method_names()
    
    def get_all_local_variable_names(self):
        return self.classes.get_all_local_variable_names()
    
    def get_total_loop_count(self):
        return self.classes.get_total_loop_count()
        
    def get_total_decision_count(self):
        return self.classes.get_total_decision_count()
    
    def get_file_size(self):
        return self.file_size
    
class JavaFiles():
    def __init__(self):
        self.files = []
        
    def add(self, java_file):
        self.files.append(java_file)
    
    def count(self, selector=None):
        if selector:
            return sum([1 for java_file in self.files if selector(java_file)])
        # no selector
        return len(self.files)

    def get_file_names(self):
        return [java_file.file_name for java_file in self.files]
    
    def get_all_class_names(self):
        class_names = set()
        for java_file in self.files:
            class_names.update(java_file.get_all_class_names())
            
        return sorted(list(class_names))
    
    def get_all_field_names(self):
        field_names = set()
        for java_file in self.files:
            field_names.update(java_file.get_all_field_names())
            
        return sorted(list(field_names))
    
    def get_all_method_names(self):
        method_names = set()
        for java_file in self.files:
            method_names.update(java_file.get_all_method_names())
            
        return sorted(list(method_names))
    
    def get_all_local_variable_names(self):
        local_variable_names = set()
        for java_file in self.files:
            local_variable_names.update(java_file.get_all_local_variable_names())
            
        return sorted(list(local_variable_names))
    
    def get_total_loop_count(self):
        return sum([file.get_total_loop_count() for file in self.files])
        
    def get_total_decision_count(self):
        return sum([file.get_total_decision_count() for file in self.files])
    
    def get_by_name(self, file_name):
        for java_file in self.files:
            if java_file.file_name == file_name:
                return java_file
            
        return None
    
    def get_all_matching(self, selector):
        matches = JavaFiles()
        
        for java_file in self.files:
            if selector(java_file):
                matches.add(java_file)
        
        return matches
    
    def get_total_file_size(self):
        total_size = 0
        for java_file in self.files:
            total_size += java_file.get_file_size()
            
        return total_size
    
    def get_all_source(self):
        source = ''
        for java_file in self.files:
            source += java_file.source
        return source
    
    def __iter__(self):
        return self.files.__iter__()
    
class JavaClass():
    def __init__(self, class_node, java_file):
        self.java_file = java_file
        self.ast_node = class_node
        self.access = parse_access(class_node.modifiers)
        self.name = class_node.name
        
        self.fields = Variables()
        self.methods = Methods()
        self.constructors = Methods()
        
        for field_node in class_node.fields:
            for declarator in field_node.declarators:
                self.fields.add(Variable(field_node, declarator.name, self))
        
        for constructor_node in class_node.constructors:
            self.constructors.add(Method(constructor_node, self))
            
        for method_node in class_node.methods:
            self.methods.add(Method(method_node, self))
    
    def get_field_names(self):
        return self.fields.get_names()
    
    def get_method_names(self):
        return self.methods.get_names()
    
    def get_all_local_variable_names(self):
        return self.methods.get_all_local_variable_names()
    
    def get_total_loop_count(self):
        return self.methods.get_total_loop_count()
        
    def get_total_decision_count(self):
        return self.methods.get_total_decision_count()
                
    def get_header(self):
        ret_val = ''
        
        if self.access:
            ret_val = self.access + ' '
            
        ret_val += 'class '
        
        ret_val += self.name
            
        return ret_val
        
    def get_outline(self):
        ret_val = self.get_header() + '\n'
        
        ret_val += ' '*2 + 'FIELDS:\n'
        for field in self.fields:
            ret_val += '-'*4 + field.get_decl() + '\n'
            
        ret_val += ' '*2 + 'METHODS:\n'
        for method in self.methods:
            ret_val += '-'*4 + method.get_header() + '\n'
        
        return ret_val
    
    def get_uml(self):
        def border(text, width):
            width = width - len(text)
            return '|' + text #+ ' '*width + '|'
        
        fields = []
        fields.extend(self.fields.get_all_matching(lambda f : not f.is_static and f.access == 'private'))
        fields.extend(self.fields.get_all_matching(lambda f : not f.is_static and f.access == 'protected'))
        fields.extend(self.fields.get_all_matching(lambda f : not f.is_static and f.access == ''))
        fields.extend(self.fields.get_all_matching(lambda f : not f.is_static and f.access == 'public'))
        fields.extend(self.fields.get_all_matching(lambda f : f.is_static and f.access == 'private'))
        fields.extend(self.fields.get_all_matching(lambda f : f.is_static and f.access == 'protected'))
        fields.extend(self.fields.get_all_matching(lambda f : f.is_static and f.access == ''))
        fields.extend(self.fields.get_all_matching(lambda f : f.is_static and f.access == 'public'))
        fields = [field.get_uml() for field in fields]
        max_field_width = max([len(field) for field in fields] + [10])
        
        methods = []
        methods.extend(self.constructors)
        methods.extend(self.methods.get_all_matching(lambda f : not f.is_static and f.access == 'private'))
        methods.extend(self.methods.get_all_matching(lambda f : not f.is_static and f.access == 'protected'))
        methods.extend(self.methods.get_all_matching(lambda f : not f.is_static and f.access == ''))
        methods.extend(self.methods.get_all_matching(lambda f : not f.is_static and f.access == 'public'))
        methods.extend(self.methods.get_all_matching(lambda f : f.is_static and f.access == 'private'))
        methods.extend(self.methods.get_all_matching(lambda f : f.is_static and f.access == 'protected'))
        methods.extend(self.methods.get_all_matching(lambda f : f.is_static and f.access == ''))
        methods.extend(self.methods.get_all_matching(lambda f : f.is_static and f.access == 'public'))
        methods = [method.get_uml() for method in methods]
        max_method_width = max([len(method) for method in methods] + [10])
        
        width = max(max_field_width, max_method_width, len(self.name)) + 1
        bar = '+' + '-'*(width) + '+\n'
        
        ret_val = bar
        ret_val += '|' + self.name.center(width) + '\n' #+ '|\n'
        ret_val += bar
        if len(fields) == 0: ret_val += '|'
        ret_val += '\n'.join([border(field, width) for field in fields])
        ret_val += '\n'
        ret_val += bar
        if len(methods) == 0: ret_val += '|'
        ret_val += '\n'.join([border(method, width) for method in methods])
        ret_val += '\n'
        ret_val += bar
        
        return ret_val

class Classes():
    def __init__(self):
        self.classes = []
        
    def add(self, java_class):
        self.classes.append(java_class)
    
    def count(self, selector=None):
        if selector:
            return sum([1 for java_class in self.classes if selector(java_class)])
        # no selector
        return len(self.classes)

    def get_names(self):
        return [java_class.name for java_class in self.classes]
    
    def get_all_field_names(self):
        field_names = set()
        for java_class in self.classes:
            field_names.update(java_class.get_field_names())
            
        return sorted(list(field_names))
    
    def get_all_method_names(self):
        method_names = set()
        for java_class in self.classes:
            method_names.update(java_class.get_method_names())
            
        return sorted(list(method_names))
    
    def get_all_local_variable_names(self):
        local_variable_names = set()
        for java_class in self.classes:
            local_variable_names.update(java_class.get_all_local_variable_names())
            
        return sorted(list(local_variable_names))
    
    def get_total_loop_count(self):
        return sum([java_class.get_total_loop_count() for java_class in self.classes])
        
    def get_total_decision_count(self):
        return sum([java_class.get_total_decision_count() for java_class in self.classes])
    
    def get_by_name(self, name):
        
        for java_class in self.classes:
            if java_class.name == name:
                return java_class
            
        return None
    
    def get_all_matching(self, selector):
        matches = Classes()
        
        for java_class in self.classes:
            if selector(java_class):
                matches.add(java_class)
        
        return matches
    
    def __iter__(self):
        return self.classes.__iter__()

class Method():
    def __init__(self, method_node, containing_class):
        self.ast_node = method_node
        self.containing_class = containing_class
        self.access = parse_access(method_node.modifiers)
        self.is_static = True if 'static' in method_node.modifiers else False
        self.name = method_node.name
        self.def_source_line_num = method_node.position[0] # 1-based line index of function header
        
        self.parameters = Variables()
        self.local_variables = Variables()
        
        # get all parameters
        for parameter in method_node.parameters:
            variable = Variable(parameter, parameter.name, self)
            variable.is_param = True
            self.parameters.add(variable)
            self.local_variables.add(variable)
        
        # find all local variabel declarations
        for path, node in method_node.filter(javalang.tree.VariableDeclaration):
                for declarator in node.declarators:
                    variable = Variable(node, declarator.name, self)
                    self.local_variables.add(variable)
        
        if 'return_type' in   method_node.attrs:      
            self.return_type = parse_datatype(method_node.return_type)
        else:
            self.return_type = ''
        
        self.while_count = sum([1 for _ in method_node.filter(javalang.tree.WhileStatement)])
        self.do_while_count = sum([1 for _ in method_node.filter(javalang.tree.DoStatement)]);
        self.for_count = sum([1 for _ in method_node.filter(javalang.tree.ForStatement)])
        
        self.if_count = sum([1 for _ in method_node.filter(javalang.tree.IfStatement)])
        self.switch_count = sum([1 for _ in method_node.filter(javalang.tree.SwitchStatement)])
        
    def get_loop_count(self):
        return (self.while_count
                + self.do_while_count
                + self.for_count)
        
    def get_decision_count(self):
        return (self.if_count + self.switch_count)
        
    def get_header(self):
        ret_val = ''
        
        if self.access:
            ret_val = self.access + ' '
            
        if self.is_static:
            ret_val += 'static '
            
        ret_val += self.return_type + ' '
        
        ret_val += self.name
        
        ret_val += '('
        ret_val += ', '.join([param.datatype + ' ' + param.name 
                              for param in self.parameters])
        ret_val += ')'
            
        return ret_val
    
    def get_uml(self):
        ret_val = {'public':' + ', 'private':' - ', 'protected':' # ', '':'   '}[self.access]
                   
        ret_val += self.name

        ret_val += '('
        ret_val += ', '.join([param.name  + ': ' + param.datatype
                              for param in self.parameters])
        ret_val += ')'
    
        ret_val += ': ' + self.return_type
        
        if self.is_static:
            ret_val += ' ((static))'
            
        return ret_val

class Methods():
    def __init__(self):
        self.methods = []
        
    def add(self, method):
        self.methods.append(method)
    
    def count(self, selector=None):
        if selector:
            return sum([1 for method in self.methods if selector(method)])
        # no selector
        return len(self.methods)

    def get_names(self):
        return [method.name for method in self.methods]
    
    def get_all_local_variable_names(self):
        local_variable_names = set()
        for method in self.methods:
            local_variable_names.update(method.local_variables.get_names())
            
        return sorted(list(local_variable_names))
    
    def get_by_name(self, name):
        
        for method in self.methods:
            if method.name == name:
                return method
            
        return None
    
    def get_all_matching(self, selector):
        matches = Methods()
        
        for method in self.methods:
            if selector(method):
                matches.add(method)
        
        return matches
    
    def get_total_loop_count(self):
        return sum([method.get_loop_count() for method in self.methods])
        
    def get_total_decision_count(self):
        return sum([method.get_decision_count() for method in self.methods])
    
    def __iter__(self):
        return self.methods.__iter__()

class Variable():
    def __init__(self, var_node, var_name, container):
        self.ast_node = var_node
        self.container = container
        self.access = parse_access(var_node.modifiers)
        self.is_static = True if 'static' in var_node.modifiers else False
        self.datatype = parse_datatype(var_node.type)
        self.is_array = True if var_node.type.dimensions else False
        self.name = var_name
        self.is_param = False
        
    def get_decl(self):
        ret_val = ''
        
        if self.access:
            ret_val = self.access + ' '
            
        if self.is_static:
            ret_val += 'static '
            
        ret_val += self.datatype + ' ' + self.name
        
        return ret_val
        
    def get_uml(self):
        ret_val = {'public':' + ', 'private':' - ', 'protected':' # ', '':'   '}[self.access]
                   
        ret_val += self.name + ': ' + self.datatype
        
        if self.is_static:
            ret_val += ' ((static))'
            
        return ret_val
    
class Variables():
    def __init__(self):
        self.variables = []
        
    def add(self, variable):
        self.variables.append(variable)
        
    def get_names(self):
        return [variable.name for variable in self.variables]
        
    def get_by_name(self, name):
        for variable in self.variables:
            if variable.name == name:
                return variable
            
        return None

    def get_all_matching(self, selector):
        matches = Variables()
        
        for variable in self.variables:
            if selector(variable):
                matches.add(variable)
        
        return matches
        
    def count(self):
        return len(self.variables)
    
    def __iter__(self):
        return self.variables.__iter__()
    
class ProgramProfile():
    def __init__(self):
        self.files = JavaFiles()
            
    def add_file(self, file_name):
        self.files.add(JavaFile(file_name))
        
    def get_all_classes(self):
        classes = Classes()
        for file in self.files:
            for java_class in file.classes:
                classes.add(java_class)
                
        return classes
    
    def get_all_class_names(self):
        return self.files.get_all_class_names()

    def get_class_by_name(self, name):
        for file in self.files:
            for java_class in file.classes:
                if java_class.name == name:
                    return java_class
                
        return None
    
    def get_all_fields(self):
        fields = Variables()
        for java_class in self.get_all_classes():
            for field in java_class.fields:
                fields.add(field)
                
        return fields
    
    def get_all_field_names(self):
        return self.files.get_all_field_names()
    
    def get_all_methods(self):
        methods = Methods()
        for java_class in self.get_all_classes():
            for method in java_class.methods:
                methods.add(method)
                
        return methods
    
    def get_all_method_names(self):
        return self.files.get_all_method_names()
    
    def get_all_local_variable_names(self):
        return self.files.get_all_local_variable_names()
        
    def get_total_loop_count(self):
        return self.files.get_total_loop_count()
        
    def get_total_decision_count(self):
        return self.files.get_total_decision_count()
    
    def get_total_file_size(self):
        return self.files.get_total_file_size()

def make_profile(directory):
    """
    Returns a ProgramProfile object that contains
    a custom collection of JavaFile objects,
    and also hoists all classes, fields, methods, and names
    up to be accessible at the top level of the profile

    Parameters
    ----------
    directory : str
        a string containing the path where the .java files are located

    Returns
    -------
    ProgramProfile
        contains 
        a custom collection of JavaFile objects,
        and also hoists all classes, fields, methods, and names
        up to be accessible at the top level of the profile
    """
    cwd = os.getcwd()
    os.chdir(directory) # <-- point this to directory
    file_names = glob.glob('*.java')
    
    profile = ProgramProfile()
    for file_name in file_names:
        profile.add_file(file_name)
    
    os.chdir(cwd) # reset current working directory
    return profile
