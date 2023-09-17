import inspect

class PyDefUtils:
    @staticmethod
    def is_class(thing):
        if inspect.isclass(thing):
            return True
        else:
            return False

    @staticmethod
    def is_module(thing):
        if inspect.ismodule(thing):
            return True
        else:
            return False

    @staticmethod
    def is_valid_name(name):
        valids = ["__new__", "__init__"]
        if name.startswith("__"):
            if name in valids:
                return True
            else:
                return False
        else:
            return True

    @staticmethod
    def is_method(thing):
        if (inspect.ismethod(thing) or inspect.isfunction(thing) or inspect.ismethoddescriptor(thing)) and PyDefUtils.is_valid_method(thing) and not PyDefUtils.is_field(thing):
            return True
        else:
            return False

    @staticmethod
    def is_valid_method(thing):
        invalids = ["dictproxy", "NoneType", "PyCapsule", "tuple", "frozenset", "set", "object"]
        if not type(thing).__name__ in invalids:
            return True
        else:
            return False

    @staticmethod
    def is_function(thing):
        if inspect.isfunction(thing) or inspect.ismethoddescriptor(thing) or type(thing).__name__ == "function" or type(thing).__name__ == "builtin_function_or_method":
            return True
        else:
            return False

    @staticmethod
    def is_data(thing):
        datas = ['int', 'float', 'str', 'long', 'complex', 'bool', 'Nonetype']
        if type(thing).__name__ in datas or inspect.isdatadescriptor(thing):
            return True
        else:
            return False

    @staticmethod
    def is_field(field):
        if inspect.isdatadescriptor(field) or PyDefUtils.is_data(field):
            return True
        else:
            return False

class PyFieldInfo:
    def __init__(self, name, obj):
        self.name = name
        self.val = str(obj)
        self.type = type(obj)

class PyFunctionInfo:
    def __init__(self, method):
        print(method)
        print(type(method))
        self.name = method.__name__
        self.args = []
        self.defaults = []
        self.extract(method)

    def extract(self, method):
        try:
            args = inspect.getargspec()
            self.args = args[0]
            self.defaults = args.defaults
        except:
            pass
        
class PyClassInfo:
    def __init__(self, cls):
        self.name = cls.__name__
        self.members = dir(cls)
        self.fields = []
        self.methods = []
        self.bases = []
        self.extract(cls)

    def extract(self, cls):
        # base class(es)
        for base in cls.__bases__:
            self.bases.append(PyClassInfo(base))

        # fields
        for field in self.members:
            try:
                field_obj = getattr(cls, field)
            except:
                return
            if PyDefUtils.is_field(field_obj):
                self.fields.append(PyFieldInfo(field, field_obj))

        # methods
        for method in self.members:
            method_obj = getattr(cls, method)
            if PyDefUtils.is_method(method_obj):
                self.methods.append(PyFunctionInfo(method_obj))

class PyModuleInfo:
    def __init__(self, module):
        self.name = module.__name__
        self.members = []
        self.extract(module)

    def extract(self, module):
        if not inspect.ismodule(module):
            raise ValueError("Given object is not a module")
        for member in dir(module):
            member_obj = getattr(module, member)
            if PyDefUtils.is_data(member_obj):
                self.members.append(PyFieldInfo(member, member_obj))
            if PyDefUtils.is_class(member_obj):
                self.members.append(PyClassInfo(member_obj))
            if PyDefUtils.is_function(member_obj):
                self.members.append(PyFunctionInfo(member_obj))
            #if PyDefUtils.is_module(member_obj):
                #self.members.append(PyModuleInfo(member_obj))
            

class PyDefDumper:
    mods_to_dump = None
    classes_to_dump = None
    
    def __init__(self):
        self.mods_to_dump = []
        self.classes_to_dump = []
    
    def is_class(self, thing):
        if inspect.isclass(thing):
            return True
        else:
            return False

    def is_module(self, thing):
        if inspect.ismodule(thing):
            return True
        else:
            return False

    def is_valid_name(self, name):
        valids = ["__new__", "__init__"]
        if name.startswith("__"):
            if name in valids:
                return True
            else:
                return False
        else:
            return True

    def is_method(self, thing):
        if inspect.ismethod(thing) or inspect.isfunction(thing) or inspect.ismethoddescriptor(thing):
            return True
        else:
            return False
        
    def is_function(self, thing):
        if inspect.isfunction(thing) or type(thing).__name__ == "function" or type(thing).__name__ == "builtin_function_or_method":
            return True
        else:
            return False

    def is_data(self, thing):
        datas = ['int', 'float', 'str', 'long', 'complex', 'bool', 'Nonetype']
        if type(thing).__name__ in datas:
            return True
        else:
            return False

    def is_field(self, field):
        if inspect.isdatadescriptor(field) or self.is_data(field):
            return True
        else:
            return False
        
    def dump_class_inheritance(self, bases):
        inheritance = "("
        multiple = True if len(bases) > 1 else False
        if multiple:
            for idx in xrange(0,len(bases)):
                if idx == len(bases)-1: # is last?
                    inheritance += bases[idx].__name__ + "):\n"
                else:
                    inheritance += bases[idx].__name__ + ", "
        else:
            inheritance += bases[0].__name__ + "):\n"
        return inheritance

    def dump_method_args(self, method):
        args = []
        try:
            args = inspect.getargspec(method)
            print(args)
            return args[0]
        except:
            pass
        return args

    def dump_class_methods(self, cls, members):
        memberdef = ""
        for member in members:
            if self.is_method(getattr(cls, member)) and self.is_valid_name(member) and not self.is_field(getattr(cls, member)):
                memberdef += "\tdef " + member + '('
                args = self.dump_method_args(getattr(cls, member))
                if not args:
                    memberdef += "):\n\t\tpass # ...\n\n"
                else:
                    for idx in xrange(0,len(args)):
                        if idx == len(args)-1:
                            memberdef += args[idx] + "):\n\t\tpass # ...\n\n"
                        else:
                            memberdef += args[idx] + ", "
        return memberdef

    def dump_class_fields(self, cls, members):
        fielddef = ""
        for field in members:
            fld = getattr(cls, field)
            if self.is_field(fld) and self.is_valid_name(field):
                if self.is_data(fld):
                    fielddef += "\t" + field + " = " + str(fld) + "\n"
                else:
                    fielddef += "\t" + field + " = " + type(fld).__name__ + "\n"
        if len(fielddef) > 2:
            fielddef += '\n'
        return fielddef
            

    def dump_class(self, cls):
        entries = dir(cls)
        classdef = "class " + cls.__name__
        if cls.__bases__:
            classdef += self.dump_class_inheritance(cls.__bases__)
        else:
            classdef = classdef + ":\n"
        classdef += self.dump_class_fields(cls, entries)
        classdef += self.dump_class_methods(cls, entries)
        return classdef
            
    def dump_lib(self, lib, name=""):
        name = lib.__name__ if not name else name
        libfile = open(name + ".def.py" , "w")
        entries = dir(lib)
        
        for entry in entries:
            obj = getattr(lib, entry)
            if self.is_data(obj) and self.is_valid_name(entry):
                libfile.write(entry + " = " + str(obj) + '\n')
            if self.is_class(obj):
                self.classes_to_dump.append(obj)
            elif self.is_module(obj):
                self.mods_to_dump.append(obj)
        print('\n')
        if self.classes_to_dump:
            for cls in self.classes_to_dump:
                libfile.write(self.dump_class(cls))
        if self.mods_to_dump:
            for mod in self.mods_to_dump:
                libfile.write("# Submodule not dumped: " + mod.__name__ + "\n")
        libfile.flush()
        libfile.close()
