# -*- coding: utf-8 -*-

import ast
from collections import defaultdict
   
class FuncDef():
    def __init__(self, func_name):
        self.func_name = func_name
        self.def_source_line_num = None # 1-based line index of function header
        self.param_names = []
        self.has_return = False
        self.return_line_nums = [] # 1-based line indexes
        self.call_line_nums = [] # 1-based line indexes
        self.source = None
        self.local_variables = Variables()
        self.ast_node = None
        self.functions_called = []

class FuncDefs():
    def __init__(self):
        self.func_defs = []
        
    def add(self, func_def):
        self.func_defs.append(func_def)
    
    def count(self, selector=None):
        if selector:
            return sum([1 for func_def in self.func_defs if selector(func_def)])
        # no selector
        return len(self.func_defs)

    def get_names(self):
        return [func_def.func_name for func_def in self.func_defs]
    
    def get_by_name(self, func_name):
        
        for func_def in self.func_defs:
            if func_def.func_name == func_name:
                return func_def
            
        return None
    
    def get_all_matching(self, selector):
        matches = FuncDefs()
        
        for func_def in self.func_defs:
            if selector(func_def):
                matches.add(func_def)
        
        return matches
    
    def __iter__(self):
        return self.func_defs.__iter__()

class While():
    def __init__(self):
        self.source_line_num = None # 1-based line index of while header
        self.condition = None # condition is a str
        self.source = None
        self.ast_node = None
        
class Whiles():
    def __init__(self):
        self.loops = []
        
    def add(self, loop):
        self.loops.append(loop)
    
    def count(self):
        return len(self.loops)

    def get_all_matching(self, selector):
        matches = Whiles()
        
        for loop in self.whiles:
            if selector(loop):
                matches.add(loop)
        
        return matches
    
    def __iter__(self):
        return self.loops.__iter__()

class If():
    def __init__(self):
        self.source_line_num = None # 1-based line index of while header
        self.condition = None # condition is a str
        self.has_else = False
        self.source = None
        self.ast_node = None

# NOTE: ast treats all elifs as nested if nodes        
class Ifs():
    def __init__(self):
        self.decisions = []
        
    def add(self, decision):
        self.decisions.append(decision)
    
    def count(self): 
        return len(self.decisions)

    def get_all_matching(self, selector):
        matches = Ifs()
        
        for decision in self.decisions:
            if selector(decision):
                matches.add(decision)
        
        return matches
    
    def __iter__(self):
        return self.decisions.__iter__()
    
class Variable():
    def __init__(self, name):
        self.name = name
        self.def_source_line_num = None
        self.assign_source_line_nums = []
        self.ref_source_line_nums = []
        self.is_param = False
        self.is_global = None
        
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
    def __init__(self, source_lines):
        # source lines is 1-based (first line [index 0] is blank)
        self.source_lines = source_lines
        self.func_defs = FuncDefs()
        self.whiles = Whiles()
        self.ifs = Ifs()
        self.global_variables = Variables()
        self.refs_to_undefined_variables = []
        self.calls_to_undefined_functions = []
        self.errors = [] # a list of strings describing errors found during tree traversal
        self.compiles = None
        
    def count_total_lines(self):
        return len(self.source_lines) - 1
    
    def count_code_lines(self):
        count = 0
        
        for line in self.source_lines:
            line = line.strip()
            if len(line) == 0 or line.startswith('#'):
                continue
            count += 1
        
        return count

    def count_blank_lines(self):
        count = 0
        
        for line in self.source_lines:
            if len(line.strip()) == 0:
                count += 1
        
        return count - 1
    
    def count_comment_lines(self):
        count = 0
        
        for line in self.source_lines:
            if line.strip().startswith('#'):
                count += 1
        
        return count

class _Profiler(ast.NodeVisitor):
    def __init__(self, source):
        self.source_lines = [''] + source.split('\n')
        
        self.profile = ProgramProfile(self.source_lines)
        
        # maps the names of functions whose defs we have not yet visited,
        # to a list of line numbers on which that function is called
        self.calls_to_undefined_functions = defaultdict(list)
        
        # maps the names of variables whose defs we have not yet visited,
        # to a list of line numbers on which that variable is referenced
        self.refs_to_undefined_variables = defaultdict(list)
        
        self.curr_func_def_stack = []
                
    def visit_FunctionDef(self, node):
        source_line_num = node.lineno
        function_name = node.name
        arg_list = node.args.args
        
        func_def = FuncDef(function_name)
        func_def.ast_node = node
        func_def.def_source_line_num = source_line_num
        for arg in arg_list:
            arg_name = arg.arg
            func_def.param_names.append(arg_name)
            # capture this parameter as a Variable object in this func_def's scope
            variable = Variable(arg_name)
            variable.is_param = True
            variable.is_global = False
            variable.def_source_line_num = source_line_num
            func_def.local_variables.add(variable)
        
        # make sure we capture all calls to this function that
        # we happened to visit before we visited this func def node
        func_def.call_line_nums.extend(self.calls_to_undefined_functions[function_name])
        del self.calls_to_undefined_functions[function_name]
        
        func_def.source = self._get_struct_source(func_def.def_source_line_num, 'def')
        
        self.profile.func_defs.add(func_def)
        
        # drill in to find any return statement(s) for this func_def
        self.curr_func_def_stack.append(func_def)
        self.generic_visit(node)
        self.curr_func_def_stack.pop()
        
    def visit_Return(self, node):
        func_def = self.curr_func_def_stack[-1]
        func_def.has_return = True
        func_def.return_line_nums.append(node.lineno)
        
        self.generic_visit(node)
        
    def visit_Call(self, node):
        line_num = node.lineno
        # if this is a call to a function in a module (i.e. math.sin)...
        if isinstance(node.func, ast.Attribute):
            function_name =  node.func.attr
        else:
            function_name = node.func.id

        func_def = self.profile.func_defs.get_by_name(function_name)

        if func_def: # we have laready visited this functions def node
            func_def.call_line_nums.append(line_num)
        else: # this is a call to an (as yet) undefined function
            self.calls_to_undefined_functions[function_name].append(line_num)
            
        if self.curr_func_def_stack:
                curr_func_def = self.curr_func_def_stack[-1]
                if function_name not in curr_func_def.functions_called:
                    curr_func_def.functions_called.append(function_name)       
        self.generic_visit(node)
   
    # keyword global imports global names into the local scope
    def visit_Global(self, node):
        # if we are currently in a func_def
        # then this ?should? be importing a list of global varibales into the local scope
        if self.curr_func_def_stack:
            curr_func_def = self.curr_func_def_stack[-1]
            local_variable_names = curr_func_def.local_variables.get_names()
            # for each name listed in the global declaration ...
            for name in node.names:
                # if the name is already in the local variables ...
                if name in local_variable_names:
                    # then this is an error
                    self.profile.errors.append(
                            '{0} is assigned before global declaration on line {1}'
                            .format(name, node.lineno))

                # else we can try to find this variable in the global variables ...
                elif name in self.profile.global_variables.get_names():
                    # and import this global varibale into the local scope
                    variable =  self.profile.global_variables.get_by_name(name)
                    curr_func_def.local_variables.add(variable)
                else: # we have not *yet* encountered a global definition for this varibale
                    # we should do a look ahead to see if we find a local assignment for this variable
                    # which will create the global variable
                    if self._node_contains_assign(curr_func_def.ast_node, name):
                         variable = Variable(name)
                         variable.is_global = True
                         self.profile.global_variables.add(variable)
                         # import this global variable into the local scope
                         curr_func_def.local_variables.add(variable)
                    else: # We can ignore this because it does nothing
                        pass
        else: # if we are not in a func_def, then this global means ?nothing?
            # so we cna ignore it
            pass
        
    # in order to visit all Call nodes
    # we must recursivly visit all
    # Assign, While, and If nodes

    def visit_While(self, node):
        loop = While()
        loop.source_line_num = node.lineno
        loop.ast_node = node
        
        loop_header = self.source_lines[loop.source_line_num]
        cond_start = loop_header.find('while') + 5
        cond_end = loop_header.rfind(':')
        loop.condition = loop_header[cond_start:cond_end].strip()
        
        loop.source = self._get_struct_source(loop.source_line_num, 'while')
        
        self.profile.whiles.add(loop)
        
        self.generic_visit(node)

    def visit_If(self, node):
        # NOTE: ast treats all elifs as nested if nodes   
        
        decision = If()
        decision.source_line_num = node.lineno
        decision.ast_node = node
        
        decision_header = self.source_lines[decision.source_line_num]
        cond_start = decision_header.find('if') + 2
        cond_end = decision_header.rfind(':')
        decision.condition = decision_header[cond_start:cond_end].strip()
        
        decision.has_else = node.orelse != []
        
        keyword = 'if' if decision_header.lstrip().startswith('if') else 'elif'
        decision.source = self._get_struct_source(decision.source_line_num, keyword)
         
        self.profile.ifs.add(decision)
        self.generic_visit(node)
        
    def visit_Assign(self, node):
        source_line_num = node.lineno
        
        # find this varibale, and append source line number to variable's list of assignment lines
        # or create this varibale, and assign source line number to variable's def line
        for target in node.targets:
            variable_name = target.id
            
            # if we are currently in a func_def
            # then this ?must? be a local variable (or a global varibale imported into the local scope)
            if self.curr_func_def_stack:
                curr_func_def = self.curr_func_def_stack[-1]
                variable = curr_func_def.local_variables.get_by_name(variable_name)
                
                if variable: # we found a local variable with this name
                    variable.ref_source_line_nums.append(source_line_num)
                else: # this is a new local variable
                    variable = Variable(variable_name)
                    variable.def_source_line_num = source_line_num
                    variable.is_global = False
                    curr_func_def.local_variables.add(variable)
            else: # we are not in a func_def and this is a global variable
                variable = self.profile.global_variables.get_by_name(variable_name)
                
                if variable:
                    variable.assign_source_line_nums.append(source_line_num)
                else: # this is a new variable global variable being defined
                    variable = Variable(variable_name)
                    variable.def_source_line_num = source_line_num
                    variable.is_global = True
                    self.profile.global_variables.add(variable)
                    
                    # make sure we capture all references to this variable that
                    # we happened to visit before we visited this assign node
                    variable.ref_source_line_nums.extend(self.refs_to_undefined_variables[variable_name])
                    del self.refs_to_undefined_variables[variable_name]
            
            # capture this assignment in an object ???
        
        self.generic_visit(node) # in case expr is complex
        
    def _node_contains_assign(self, func_def_node, variable_name):
        for sub_node in func_def_node.body:
            if isinstance(sub_node, ast.Assign):
                target_names = [target.id for target in sub_node.targets]
                if variable_name in target_names: # in which case we have a (referenced before assignment) error
                    return True
        
        return False
    
    def visit_Name(self, node):
        # only look at names in the context of an evaluation
        if  isinstance(node.ctx, ast.Load):
            source_line_num = node.lineno
            variable_name = node.id
            
            # if we are currently in a func_def
            if self.curr_func_def_stack:
                # then we can check the local scope for this variable
                curr_func_def = self.curr_func_def_stack[-1]
                variable = curr_func_def.local_variables.get_by_name(variable_name)
            
                # and if we find it...
                if variable:
                    # then all is okay, and we can recored the reference
                    variable.ref_source_line_nums.append(source_line_num)   
                    
                    # if we did not find it in the locals (right now)
                    # we will still need to look ahead at this func_def's nodes
                    # for an assign node that defines this as a local variable
                elif self._node_contains_assign(curr_func_def.ast_node, variable_name): 
                    self.profile.errors.append("local variable '" +  variable_name + 
                                                           " is referenced before assignment on line " + str(source_line_num))
                else: # we did not find any 'defs for this variable in this func_def,
                    # so, we can look globally
                    variable = self.profile.global_variables.get_by_name(variable_name)
                
                    if variable: # we found a global variable with this name
                        variable.assign_source_line_nums.append(source_line_num)
                    else: # this is an (as yet) undefined variable
                        self.refs_to_undefined_variables[variable_name].append(source_line_num)
            else: # we are not in a func_def
                variable = self.profile.global_variables.get_by_name(variable_name)
                
                if variable: # we found a global variable with this name
                    variable.assign_source_line_nums.append(source_line_num)
                else: # this is an (as yet) undefined variable
                    self.refs_to_undefined_variables[variable_name].append(source_line_num)
    
    def _get_struct_source(self, header_lineno, struct_keyword):
        """
        Returns a str containing the raw source code text for the 
        def, while, if, or elif structure that starts on header_lineno
    
        Parameters
        ----------
        header_lineno : int
            the 1-based line index of the header line for the desired structure
        struct_keyword : str
            a str containing the keyword that identifies the desired structure 
            ('def', 'while', 'if', or 'elif')
    
        Returns
        -------
        ProgramProfile
            contains 
            a custom collection of FuncDef objects,
            a custom collection of While objects, and
            a custom collection if If objects
            for all such structures defined in source_code
        """
        line_index = header_lineno
        source_line = self.source_lines[line_index]
        source = source_line
        header_indent = source_line[0:source_line.find(struct_keyword)]
        
        if line_index == len(self.source_lines) - 1:
            return source.rstrip() # strip extra trailing whitspace
        
        line_index += 1
        source_line = self.source_lines[line_index]
        line_is_empty = source_line.strip() == ''
        line_starts_with_indent = source_line.startswith(header_indent)
        line_is_longer_than_indent = len(source_line) > len(header_indent)
        line_has_indented_content = line_is_longer_than_indent and source_line[len(header_indent)] in ' \t'
        
        while line_is_empty or line_starts_with_indent and line_has_indented_content:
            source += '\n' + source_line
            line_index += 1
            if line_index >= len(self.source_lines) - 1:
                return source.rstrip() # strip extra trailing whitspace
            
            source_line = self.source_lines[line_index]
            line_is_empty = source_line.strip() == ''
            line_starts_with_indent = source_line.startswith(header_indent)
            line_is_longer_than_indent = len(source_line) > len(header_indent)
            line_has_indented_content = line_is_longer_than_indent and source_line[len(header_indent)] in ' \t'
        
        return source.rstrip() # strip extra trailing whitspace

def make_profile(source_code):
    """
    Returns a ProgramProfile object that contains
    a custom collection of FuncDef objects,
    a custom collection of While objects, and
    a custom collection if If objects
    for all such structures defined in source_code

    Parameters
    ----------
    source_code : str
        a string containing the source code

    Returns
    -------
    ProgramProfile
        contains 
        a custom collection of FuncDef objects,
        a custom collection of While objects, and
        a custom collection if If objects
        for all such structures defined in source_code
    """
    
    profiler = _Profiler(source_code)
    
    # if the source code cannot be parsed to an AST
    # or if the source code does not compile ...
    # then return an empty profile with just the source lines
    # and its compiles attribute set to False
    try:
        tree = ast.parse(source_code)
        compile(source_code, '<string>', 'exec')
    except Exception:
        profiler.profile.compiles = False
        return profiler.profile
        
    profiler.profile.compiles = True
    profiler.visit(tree)
    
    profiler.profile.refs_to_undefined_variables = dict(profiler.refs_to_undefined_variables)
    profiler.profile.calls_to_undefined_functions = dict(profiler.calls_to_undefined_functions)
    
    return profiler.profile
