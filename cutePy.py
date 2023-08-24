# Kondylia Vergou, AM:4325, cse84325
import sys

##############################################################
#                     USEFUL STRUCTURES                      #
##############################################################
class Token:
    # properties : recognized_string , family , line_number
    def __init__(self, recognized_string, family, line_number):
        self.recognized_string = recognized_string
        self.family = family
        self.line_number = line_number

class Quad:
    def __init__(self, tag, operator, operand_1, operand_2, operand_3):
        self.tag = tag
        self.operator = operator
        self.operand_1 = operand_1
        self.operand_2 = operand_2
        self.operand_3 = operand_3

    def to_string(self):
        return str(self.tag) + ': ' + str(self.operator) + ', ' + \
            str(self.operand_1) + ', ' + str(self.operand_2) + ', ' + str(self.operand_3) + '\n'

class Entity:
    def __init__(self, name, family, datatype):
        self.name = name
        self.family = family
        self.datatype = datatype

class Variable(Entity):
    def __init__(self, name, family, datatype, offset):
        super().__init__(name, family, datatype)
        self.offset = offset

    def to_string(self):
        return "\tEntity: " + self.name + "\t\tfamily: " + self.family + "\t\tdatatype: " + self.datatype + \
            "\t\toffset: " + str(self.offset) + "\n"

class TemporaryVariable(Entity):
    def __init__(self, name, family, datatype, offset):
        super().__init__(name, family, datatype)
        self.offset = offset

    def to_string(self):
        return "\tEntity: " + self.name + "\t\tfamily: " + self.family + "\t\tdatatype: " + self.datatype + \
            "\t\toffset: " + str(self.offset) + "\n"

class FormalParameter(Entity):
    def __init__(self, name, family, datatype, mode):
        super().__init__(name, family, datatype)
        self.mode = mode

    def to_string(self):
        return "\t\tEntity: " + self.name + "\t\tfamily: " + self.family + "\t\tdatatype: " + self.datatype + \
            "\t\tmode: " + self.mode + "\n"

class Parameter(FormalParameter):
    def __init__(self, name, family, datatype, mode, offset):
        super().__init__(name, family, datatype, mode)
        self.offset = offset

    def to_string(self):
        return "\tEntity: " + self.name + "\t\tfamily: " + self.family + "\t\tdatatype: " + self.datatype + \
            "\t\tmode: " + self.mode +"\t\toffset: " + str(self.offset) + "\n"

class Function(Entity):
    def __init__(self, name, family, datatype):
        super().__init__(name, family, datatype)
        self.starting_quad = 0
        self.framelength = 0
        self.formal_parameters = []

    def to_string(self):
        return "\tEntity: " + self.name + "\t\tfamily: " + self.family + "\t\tdatatype: " + self.datatype + \
            "\t\tstarting_quad: " + str(self.starting_quad) +"\t\tframelength: " + str(self.framelength) +\
            "\n\t\tformal_parameters: " + self.formal_parameters_to_string()

    def formal_parameters_to_string(self):
        formal_parameters_str = "\n"
        for formal_parameter in self.formal_parameters:
            formal_parameters_str += formal_parameter.to_string()
        return formal_parameters_str

class Scope:
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.entities = []

    def to_string(self):
        return "Scope: " + self.name + "\t\tlevel: " + str(self.level) + "\n"
##############################################################
#                                                            #
#                     LEXICAL ANALYZER                       #
#                                                            #
##############################################################
class LexicalAnalyzer:
    def __init__(self):
        self.current_line = 1
        self.token = Token("recognized_string", "family", 1)

    def read_character(self):
        return lexical_analysis_file.read(1).decode("ascii")

    def backtrack(self, char):
        # No need for backtracking when eof
        if char != "":
            lexical_analysis_file.seek(-1, 1)

    def error(self, message):
        print("[Error] Line " + str(self.current_line) + ": " + message)
        quit()

    def next_token(self):
        char = self.read_character()

        # White Characters
        while char == "\n" or (char == "\r" and self.read_character() == "\n") \
                or char == " " or char == "\t":
            if char == " " or char == "\t":
                char = self.read_character()
                continue
            char = self.read_character()
            self.current_line += 1
            self.token.line_number = self.current_line

        # Identifier or Keyword
        if char.isalpha():
            self.token.recognized_string = self.create_identifier_or_keyword_string(char)
            self.token.family = self.is_identifier_or_keyword()
        elif char == "_":
            self.token.recognized_string = self.create_keyword_string_starting_with_symbols(char, "__name__")
        elif char == '"':
            self.token.recognized_string = self.create_keyword_string_starting_with_symbols(char, '"__main__"')

        # Number
        elif char.isnumeric():
            self.token.recognized_string = self.create_number_string(char)
            self.token.family = "number"

        # Add Operators
        elif char == "+" or char == "-":
            self.token.recognized_string = char
            self.token.family = "addOperator"

        # Mul Operators
        elif char == "*":
            self.token.recognized_string = char
            self.token.family = "mulOperator"
        elif char == "/":
            self.token.recognized_string = self.create_operator_string_from_symbols(char, "/")
            self.token.family = "mulOperator"
            if self.token.recognized_string == "/":
                self.error("Invalid '/'")

        # Relation Operators
        elif char == "<":
            self.token.recognized_string = self.create_operator_string_from_symbols(char, "=")
            self.token.family = "relOperator"
        elif char == ">":
            self.token.recognized_string = self.create_operator_string_from_symbols(char, "=")
            self.token.family = "relOperator"
        elif char == "!":
            self.token.recognized_string = self.create_operator_string_from_symbols(char, "=")
            self.token.family = "relOperator"
            if self.token.recognized_string == "!":
                self.error("Invalid '!'")

        # Equality Symbol
        elif char == "=":
            self.token.recognized_string = self.create_operator_string_from_symbols(char, "=")
            # Relation Operator
            self.token.family = "relOperator"

            # Assignment
            if self.token.recognized_string == "=":
                self.token.family = "assignment"

        # Grouping Symbols
        elif char == "(" or char == ")" or char == "[" or char == "]":
            self.token.recognized_string = char
            self.token.family = "groupSymbol"

        # Hashtag Symbol
        elif char == "#":
            self.token.recognized_string = char
            char = self.read_character()

            # Grouping Symbols
            if char == "{" or char == "}":
                self.token.recognized_string += char
                self.token.family = "groupSymbol"

            # Comments
            elif char == "$":
                self.parse_comments(char)
                return self.next_token()

            # Identifier '#declare'
            elif char == "d":
                self.backtrack(char)
                self.token.recognized_string = self.create_keyword_string_starting_with_symbols("#", "#declare")
            else:
                self.error("Invalid '#'")

        # Delimiters
        elif char == ";" or char == "," or char == ":":
            self.token.recognized_string = char
            self.token.family = "delimiter"

        # EOF
        elif char == "":
            self.token.recognized_string = char
            self.token.family = "eof"

        # Illegal Character
        else:
            self.error("Invalid '" + char + "'")

        # Return Token
        return self.token

    def create_identifier_or_keyword_string(self, char):
        string_length = 0
        recognized_string = ""
        while char.isalpha() or char.isdigit() or char == "_":
            if string_length > 30:
                self.error("Identifier or Keyword over 30 characters")
                quit()
            recognized_string += char
            string_length += 1
            char = self.read_character()
        self.backtrack(char)
        return recognized_string

    def is_identifier_or_keyword(self):
        keyword_list = ["while", "if", "else", "not", "and", "or"
                        "def", "return", "print", "int", "input"]
        if self.token.recognized_string in keyword_list:
            return "keyword"
        return "identifier"

    def create_number_string(self, char):
        number_limit = 2 ** 32 - 1
        recognized_string = ""
        while char.isnumeric():
            recognized_string += char
            char = char = self.read_character()
            if char.isalpha():
                self.error("Invalid Number , Contains letters")
            if int(recognized_string) < -number_limit or int(recognized_string) > number_limit:
                self.error("Invalid Number, Over the limit")
        self.backtrack(char)
        return recognized_string

    def create_keyword_string_starting_with_symbols(self, char, keyword):
        recognized_string = ""
        for letter in keyword:
            recognized_string += char
            if char != letter:
                self.error("Invalid '" + recognized_string + "'")
            char = self.read_character()
        self.backtrack(char)
        self.token.family = "keyword"
        return recognized_string

    def create_operator_string_from_symbols(self, char, other_symbol):
        recognized_string = char
        char = self.read_character()
        if char == other_symbol:
            recognized_string += char
        else:
            self.backtrack(char)
        return recognized_string

    def parse_comments(self, char):
        while self.token.recognized_string != "#$":
            while char != "#":
                if char == "\n":
                    self.current_line += 1
                char = self.read_character()
                if not char:
                    self.error("Expected '#$', Comments never closed, Reached the end of the file")
            char = self.read_character()
            # End of the Comments
            if char == "$":
                self.token.recognized_string += char

##############################################################
#                                                            #
#                  INTERMEDIATE CODE HANDLER                 #
#                                                            #
##############################################################
class IntermediateCodeHandler:
    def __init__(self):
        self.quad_counter = 1
        self.quad_list = []
        self.temp_counter = 0
        self.temp_list = []
        self.temp_prefix = "%0"

    def generate_quad(self, operator, operand_1, operand_2, operand_3):
        quad = Quad(self.quad_counter, operator, operand_1, operand_2, operand_3)
        self.quad_list.append(quad)
        self.quad_counter += 1
        return quad

    def next_quad(self):
        return self.quad_counter

    def new_temp(self, symbol_table):
        self.temp_counter += 1
        temp = self.temp_prefix + str(self.temp_counter)
        self.temp_list.append(temp)
        temporary_variable_entity = TemporaryVariable(temp, "TEMPORARY_VARIABLE", "INT", symbol_table.calculate_offset())
        symbol_table.add_entity(temporary_variable_entity)
        return temp

    def empty_list(self):
        empty_list = []
        return empty_list

    def make_list(self, label):
        make_list = [label]
        return make_list

    def merge_list(self, list1, list2):
        merge_list = list1 + list2
        return merge_list

    def backpatch(self, tag_list, label):
        for tag in tag_list:
            self.quad_list[tag-1].operand_3 = label

##############################################################
#                                                            #
#                        SYMBOL TABLE                        #
#                                                            #
##############################################################
class SymbolTable:
    def __init__(self):
        self.scope_level = 0
        self.scopes = []

    def add_scope(self, name):
        new_scope = Scope(name, self.scope_level)
        self.scopes.append(new_scope)
        self.scope_level += 1

    def delete_scope(self):
        self.scope_level -= 1
        self.scopes.pop()

    def add_entity(self, entity):
        self.scopes[-1].entities.append(entity)

    def add_formal_parameter(self, formal_parameter):
        self.scopes[-2].entities[-1].formal_parameters.append(formal_parameter)

    def update_starting_quad(self, intermediate_code_handler):
        self.scopes[-2].entities[-1].starting_quad = intermediate_code_handler.next_quad()

    def update_framelength(self):
        self.scopes[-2].entities[-1].framelength = self.calculate_offset()

    def calculate_offset(self):
        count_entities = 0
        min_offset = 12
        var_size = 4
        for entity in self.scopes[-1].entities:
            if entity.family == "GLOBAL_VARIABLE" or entity.family == "VARIABLE" \
                    or entity.family == "TEMPORARY_VARIABLE" or entity.family == "PARAMETER":
                count_entities += 1
        offset = min_offset + count_entities * var_size
        return offset

    def search_entity(self, name):
        for scope in self.scopes:
            for entity in scope.entities:
                if entity.name == name:
                    return scope, entity
        print("[Error] Entity " + str(name) + " doesn't exist in Symbol Table")
        quit()

    def generate_symbol_table_file(self):
        header =  "#" * 100 + "\n\t\t\t\t\t\tSymbol Table Until Scope: " + self.scopes[-1].name + "\n"
        symbol_table_file.write(header)
        for scope in self.scopes:
            symbol_table_file.write(scope.to_string())
            for entity in scope.entities:
                symbol_table_file.write(entity.to_string())
            symbol_table_file.write("\n")
        footer = "\n"
        symbol_table_file.write(footer)

##############################################################
#                                                            #
#                    TARGET CODE HANDLER                     #
#                                                            #
##############################################################
class TargetCodeHandler:
    def __init__(self):
        self.initialization_flag = True
        self.frame_pointer_mover_flag = True
        self.param_count = 0
        self.quad_count = 0

    def produce(self, assembly_command):
        target_code_file.write("\t" + assembly_command + "\n")

    def produce_label(self, label, label_suffix):
        target_code_file.write(label + label_suffix + ":\n")

    def gnlvcode(self, var, symbol_table):
        scope, entity = symbol_table.search_entity(var)
        scope_level_diff = symbol_table.scopes[-1].level - scope.level
        self.produce("lw t0, -4(sp)")
        for i in range(0, scope_level_diff):
            self.produce("lw t0, -4(t0)")
        self.produce("addi t0, t0 " + str(entity.offset))

    def loadvr(self, var, reg, symbol_table):
        if var.lstrip("-").isdigit():
            self.produce("li " + reg + ", " + var)
        else:
            scope, entity = symbol_table.search_entity(var)
            if entity.family == "GLOBAL_VARIABLE":
                self.produce("lw " + reg + ", -" + str(entity.offset) + "(gp)")
            # PARAMETER, VARIABLE, TEMPORARY_VARIABLE OF CURRENT FUNC
            elif symbol_table.scopes[-1].level == scope.level:
                self.produce("lw " + reg + ", -" + str(entity.offset) + "(sp)")
            # PARAMETER, VARIABLE OF ANCESTOR FUNC
            elif symbol_table.scopes[-1].level > scope.level:
                self.gnlvcode(var, symbol_table)
                self.produce("lw " + reg + ", (t0)")

    def storerv(self, reg, var, symbol_table):
        scope, entity = symbol_table.search_entity(var)
        if entity.family == "GLOBAL_VARIABLE":
            self.produce("sw " + reg + ", -" + str(entity.offset) + "(gp)")
        # PARAMETER, VARIABLE, TEMPORARY_VARIABLE OF CURRENT FUNC
        elif symbol_table.scopes[-1].level == scope.level:
            self.produce("sw " + reg + ", -" + str(entity.offset) + "(sp)")
        # PARAMETER, VARIABLE OF ANCESTOR FUNC
        elif symbol_table.scopes[-1].level > scope.level:
            self.gnlvcode(var, symbol_table)
            self.produce("sw " + reg + ", (t0)")

    def generate_target_code_file(self, intermediate_code_handler, symbol_table):
        ARITHM_OP = ['+', '-', '*', '//']
        ARITHM_OP_IN_TARGET_CODE = ['add', 'sub', 'mul', 'div']
        REL_OP = ['<', '>', '==', '<=', '>=', '!=']
        REL_OP_IN_TARGET_CODE = ['blt', 'bgt', 'beq', 'ble', 'bge', 'bne']

        if self.initialization_flag:
            self.produce("\t.data")
            self.produce('str_nl: .asciz "\\n"')
            self.produce(".text\n")
            self.produce_label("L", "0")
            self.initialization_flag = False

        for quad in intermediate_code_handler.quad_list[self.quad_count:]:
            self.quad_count += 1
            self.produce_label("L", str(quad.tag))

            # BEGIN_BLOCK
            if quad.operator == "begin_block":
                self.produce_label("L", quad.operand_1)
                if "main_" in quad.operand_1:   #MAIN FUNCTION
                    scope, main_function_entity = symbol_table.search_entity(quad.operand_1)
                    self.produce("addi sp,sp " + str(main_function_entity.framelength))
                    self.produce("mv gp,sp")
                else:   #LOCAL FUNCTION
                    self.produce("sw ra,(sp)")
            # END_BLOCK FOR LOCAL FUNCTIONS
            elif quad.operator == "end_block" and "main_" not in quad.operand_1:
                self.produce("lw ra,(sp)")
                self.produce("jr ra")
            # JUMP FOR IF, WHILE
            elif quad.operator == "jump":
                self.produce("j L" + str(quad.operand_3))
            # JUMP FOR RELATIONAL OPERATORS
            elif quad.operator in REL_OP:
                self.loadvr(quad.operand_1, "t1", symbol_table)
                self.loadvr(quad.operand_2, "t2", symbol_table)
                self.produce(REL_OP_IN_TARGET_CODE[REL_OP.index(quad.operator)] + " t1, t2, L" + str(quad.operand_3))
            # ASSIGNMENT
            elif quad.operator == "=":
                self.loadvr(quad.operand_1, "t0", symbol_table)
                self.storerv("t0", quad.operand_3, symbol_table)
            # ARITHMETIC COMMANDS
            elif quad.operator in ARITHM_OP:
                self.loadvr(quad.operand_1, "t1", symbol_table)
                self.loadvr(quad.operand_2, "t2", symbol_table)
                self.produce(ARITHM_OP_IN_TARGET_CODE[ARITHM_OP.index(quad.operator)] + " t1, t2, t1")
                self.storerv("t1", quad.operand_3, symbol_table)
            # INPUT
            elif quad.operator == "in":
                self.produce("li a7, 5")
                self.produce("ecall")
                self.storerv("a0", quad.operand_1, symbol_table)
            # OUTPUT
            elif quad.operator == "out":
                self.loadvr(quad.operand_1, "a0", symbol_table)
                self.produce("li a7, 1")
                self.produce("ecall")
                self.produce("la a0, str_nl")
                self.produce("li a7, 4")
                self.produce("ecall")
            # RETURN
            elif quad.operator == "ret":
                self.loadvr(quad.operand_1, "t1", symbol_table)
                self.produce("lw t0, -8(sp)")
                self.produce("sw t1, (t0)")
            # PARAMETER
            elif quad.operator == "par":
                if self.frame_pointer_mover_flag:
                    for i in range(quad.tag, len(intermediate_code_handler.quad_list)):
                        if intermediate_code_handler.quad_list[i].operator == "call":
                            function_name = intermediate_code_handler.quad_list[i].operand_1
                            break
                    scope, function_entity = symbol_table.search_entity(function_name)
                    self.produce("addi fp, sp, " + str(function_entity.framelength))
                    self.frame_pointer_mover_flag = False

                self.param_count += 1
                if quad.operand_2 == "CV":
                    param_offset = 12 + (self.param_count - 1)*4
                    self.loadvr(quad.operand_1, "t0", symbol_table)
                    self.produce("sw t0, -" + str(param_offset) + "(fp)")
                elif quad.operand_2 == "RET":
                    scope, variable_entity = symbol_table.search_entity(quad.operand_1)
                    self.produce("addi t0, sp, -" + str(variable_entity.offset))
                    self.produce("sw t0, -8(fp)")
            # CALL
            elif quad.operator == "call":
                scope, function_entity = symbol_table.search_entity(quad.operand_1)
                if self.frame_pointer_mover_flag:
                    self.produce("addi fp, sp, " + str(function_entity.framelength))
                self.frame_pointer_mover_flag = True
                self.param_count = 0

                caller_scope, caller_function_entity = symbol_table.search_entity(symbol_table.scopes[-2].entities[-1].name)
                # SIBLING CALLER FUNCTION
                if scope.level == caller_scope.level:
                    self.produce("lw t0, -4(sp)")
                    self.produce("sw t0, -4(fp)")
                # PARENT CALLER FUNCTION
                else:
                    self.produce("sw sp, -4(fp)")
                self.produce("addi sp, sp, " + str(function_entity.framelength))
                self.produce("jal L" + function_entity.name)
                self.produce("addi sp,sp, -" + str(function_entity.framelength))
            # HALT
            elif quad.operator == "halt":
                self.produce("li a0,0")
                self.produce("li a7,93")
                self.produce("ecall")

##############################################################
#                                                            #
#                           PARSER                           #
#               PERFORMS LEXICAL & SYNTAX ANALYSIS           #
#            CREATES INTERMEDIATE CODE & SYMBOL TABLE        #
#                    GENERATES TARGET CODE                   #
#                                                            #
##############################################################
class Parser:
    ADD_OP = ["+", "-"]
    MUL_OP = ["*", "//"]

    def __init__(self):
        self.token = Token("recognized_string", "family", 1)
        self.lexical_analyzer = LexicalAnalyzer()
        self.intermediate_code_handler = IntermediateCodeHandler()
        self.symbol_table = SymbolTable()
        self.target_code_handler = TargetCodeHandler()

    def get_token(self):
        return self.lexical_analyzer.next_token()

    def error(self, message):
        print("[Error] Line " + str(self.lexical_analyzer.current_line) + ": " + message)
        quit()

    def check_token_recognized_string(self, recognized_string):
        if self.token.recognized_string != recognized_string:
            self.error("Expected '" + recognized_string + "', Invalid '" + self.token.recognized_string + "'")

    def check_token_recognized_string_with_message(self, recognized_string, message):
        if self.token.recognized_string != recognized_string:
            self.error("Expected '" + recognized_string +
                       "', Invalid '" + self.token.recognized_string + "', " + message)

    def check_token_family(self, family):
        if self.token.family != family:
            self.error("Expected family '" + family + "', Invalid family '" + self.token.family + "'")

    def is_simple_statement(self):
        return self.token.recognized_string in ("print", "return") or self.token.family == "identifier"

    def is_structured_statement(self):
        return self.token.recognized_string in ("if", "while")

    def is_expression(self):
        return self.token.recognized_string in self.ADD_OP or self.token.family == 'number' \
            or self.token.recognized_string == "(" or self.token.family == 'identifier'

    def syntax_analyzer(self):
        self.token = self.get_token()
        self.start_rule()
        print("Compilation successfully completed!")

    def start_rule(self):
        self.symbol_table.add_scope("main")
        self.target_code_handler.generate_target_code_file(self.intermediate_code_handler, self.symbol_table)
        self.def_main_part()
        self.call_main_part()
        self.symbol_table.generate_symbol_table_file()
        self.symbol_table.delete_scope()

    def def_main_part(self):
        self.def_main_function()
        while self.token.recognized_string == "def":
            self.def_main_function()

    def def_main_function(self):
        self.check_token_recognized_string("def")
        self.token = self.get_token()
        self.check_token_family("identifier")
        main_function_name = self.token.recognized_string
        function_entity = Function(main_function_name, "FUNCTION", "INT")
        self.symbol_table.add_entity(function_entity)
        self.symbol_table.add_scope(main_function_name)
        self.target_code_handler.produce("j L" + main_function_name)
        self.token = self.get_token()
        self.check_token_recognized_string("(")
        self.token = self.get_token()
        self.check_token_recognized_string_with_message(")", "Parenthesis never closed")
        self.token = self.get_token()
        self.check_token_recognized_string(":")
        self.token = self.get_token()
        self.check_token_recognized_string("#{")
        self.token = self.get_token()
        self.declarations("main_declarations")
        while self.token.recognized_string == "def":
            self.def_function()
        self.symbol_table.update_starting_quad(self.intermediate_code_handler)
        self.intermediate_code_handler.generate_quad("begin_block", main_function_name, "_", "_")
        self.statements()
        self.symbol_table.update_framelength()
        self.intermediate_code_handler.generate_quad("end_block", main_function_name, "_", "_")
        self.check_token_recognized_string("#}")
        self.token = self.get_token()
        self.symbol_table.generate_symbol_table_file()
        self.target_code_handler.generate_target_code_file(self.intermediate_code_handler, self.symbol_table)
        self.symbol_table.delete_scope()

    def def_function(self):
        self.check_token_recognized_string("def")
        self.token = self.get_token()
        self.check_token_family("identifier")
        function_name = self.token.recognized_string
        function_entity = Function(function_name, "FUNCTION", "INT")
        self.symbol_table.add_entity(function_entity)
        self.symbol_table.add_scope(function_name)
        self.token = self.get_token()
        self.check_token_recognized_string("(")
        self.token = self.get_token()
        self.id_list("def_function")
        self.check_token_recognized_string_with_message(")", "Parenthesis never closed")
        self.token = self.get_token()
        self.check_token_recognized_string(":")
        self.token = self.get_token()
        self.check_token_recognized_string("#{")
        self.token = self.get_token()
        self.declarations("declarations")
        while self.token.recognized_string == "def":
            self.def_function()
        self.symbol_table.update_starting_quad(self.intermediate_code_handler)
        self.intermediate_code_handler.generate_quad("begin_block", function_name, "_", "_")
        self.statements()
        self.symbol_table.update_framelength()
        self.intermediate_code_handler.generate_quad("end_block", function_name, "_", "_")
        self.check_token_recognized_string("#}")
        self.token = self.get_token()
        self.symbol_table.generate_symbol_table_file()
        self.target_code_handler.generate_target_code_file(self.intermediate_code_handler, self.symbol_table)
        self.symbol_table.delete_scope()

    def declarations(self, caller_function):
        while self.token.recognized_string == "#declare":
            self.declaration_line(caller_function)

    def declaration_line(self, caller_function):
        self.token = self.get_token()  # consume #declare
        self.id_list(caller_function)

    def statements(self):
        self.statement()
        while self.is_simple_statement() or self.is_structured_statement():
            self.statement()

    def statement(self):
        if self.is_simple_statement():
            self.simple_statement()
        elif self.is_structured_statement():
            self.structured_statement()
        else:
            self.error("Expected start of simple or structured statement, "
                         "Illegal '" + self.token.recognized_string + "'")

    def simple_statement(self):
        if self.token.family == "identifier":
            self.assignment_stat()
        elif self.token.recognized_string == "print":
            self.print_stat()
        else: # "return"
            self.return_stat()

    def structured_statement(self):
        if self.token.recognized_string == "if":
            self.if_stat()
        else: # "while"
            self.while_stat()

    def assignment_stat(self):
        target = self.token.recognized_string
        self.token = self.get_token()  # consume identifier
        self.check_token_recognized_string("=")
        self.token = self.get_token()
        if self.is_expression():
            source = self.expression()
            self.check_token_recognized_string(";")
            self.intermediate_code_handler.generate_quad("=", source, "_", target)
            self.token = self.get_token()
        elif self.token.recognized_string == "int":
            self.token = self.get_token()
            self.check_token_recognized_string("(")
            self.token = self.get_token()
            self.check_token_recognized_string("input")
            self.token = self.get_token()
            self.check_token_recognized_string("(")
            self.intermediate_code_handler.generate_quad('in', target, '_', '_')
            self.token = self.get_token()
            self.check_token_recognized_string_with_message(")", "Parenthesis never closed")
            self.token = self.get_token()
            self.check_token_recognized_string_with_message(")", "Parenthesis never closed")
            self.token = self.get_token()
            self.check_token_recognized_string(";")
            self.token = self.get_token()
        else:
            self.error("Expected start of expression or 'int', "
                         "Illegal '" + self.token.recognized_string + "'")

    def print_stat(self):
        self.token = self.get_token() # consume print
        self.check_token_recognized_string("(")
        self.token = self.get_token()
        expression_place = self.expression()
        self.intermediate_code_handler.generate_quad('out', expression_place, '_', '_')
        self.check_token_recognized_string_with_message(")", "Parenthesis never closed")
        self.token = self.get_token()
        self.check_token_recognized_string(";")
        self.token = self.get_token()

    def return_stat(self):
        self.token = self.get_token() # consume return
        self.check_token_recognized_string("(")
        self.token = self.get_token()
        expression_place = self.expression()
        self.intermediate_code_handler.generate_quad('ret', expression_place, '_', '_')
        self.check_token_recognized_string_with_message(")", "Parenthesis never closed")
        self.token = self.get_token()
        self.check_token_recognized_string(";")
        self.token = self.get_token()

    def if_stat(self):
        self.token = self.get_token()  # consume if
        self.check_token_recognized_string("(")
        self.token = self.get_token()
        condition_true, condition_false = self.condition()
        self.check_token_recognized_string_with_message(")", ", Parenthesis never closed")
        self.token = self.get_token()
        self.check_token_recognized_string(":")
        self.token = self.get_token()
        self.intermediate_code_handler.backpatch(condition_true, self.intermediate_code_handler.next_quad())
        self.structured_statement_block()
        if_list = self.intermediate_code_handler.make_list(self.intermediate_code_handler.next_quad())
        self.intermediate_code_handler.generate_quad("jump", "_", "_", "_")
        self.intermediate_code_handler.backpatch(condition_false, self.intermediate_code_handler.next_quad())
        if self.token.recognized_string == 'else':
            self.token = self.get_token()
            self.check_token_recognized_string(":")
            self.token = self.get_token()
            self.structured_statement_block()
        self.intermediate_code_handler.backpatch(if_list, self.intermediate_code_handler.next_quad())

    def while_stat(self):
        self.token = self.get_token()  # consume while
        self.check_token_recognized_string("(")
        self.token = self.get_token()
        cond_quad = self.intermediate_code_handler.next_quad()
        condition_true, condition_false = self.condition()
        self.intermediate_code_handler.backpatch(condition_true, self.intermediate_code_handler.next_quad())
        self.check_token_recognized_string_with_message(")", "Parenthesis never closed")
        self.token = self.get_token()
        self.check_token_recognized_string(":")
        self.token = self.get_token()
        self.structured_statement_block()
        self.intermediate_code_handler.generate_quad("jump", "_", "_", cond_quad)
        self.intermediate_code_handler.backpatch(condition_false, self.intermediate_code_handler.next_quad())

    def structured_statement_block(self):
        if self.is_simple_statement() or self.is_structured_statement():
            self.statement()
        elif self.token.recognized_string == "#{":
            self.token = self.get_token()
            self.statements()
            self.check_token_recognized_string("#}")
            self.token = self.get_token()
        else:
            self.error("Expected start of statement or '#{, Illegal '" + self.token.recognized_string + "'")

    def id_list(self, caller_function):
        if self.token.family == "identifier":
            self.id_list_for_symbol_table(caller_function, self.token.recognized_string)
            self.token = self.get_token()
            while self.token.recognized_string == ",":
                self.token = self.get_token()
                self.check_token_family("identifier")
                self.id_list_for_symbol_table(caller_function, self.token.recognized_string)
                self.token = self.get_token()

    def id_list_for_symbol_table(self, caller_function, entity_name):
        if caller_function == "main_declarations":
            variable_entity = Variable(entity_name, "GLOBAL_VARIABLE", "INT", self.symbol_table.calculate_offset())
            self.symbol_table.add_entity(variable_entity)
        elif caller_function == "declarations":
            variable_entity = Variable(entity_name, "VARIABLE", "INT", self.symbol_table.calculate_offset())
            self.symbol_table.add_entity(variable_entity)
        elif caller_function == "def_function":
            formal_parameter_entity = FormalParameter(entity_name, "FORMAL_PARAMETER", "INT", "CV")
            self.symbol_table.add_formal_parameter(formal_parameter_entity)
            parameter_entity = Parameter(entity_name, "PARAMETER", "INT", "CV", self.symbol_table.calculate_offset())
            self.symbol_table.add_entity(parameter_entity)

    def expression(self):
        optional_sign = self.optional_sign()
        term = self.term()
        operand_1 = optional_sign + term
        while self.token.recognized_string in self.ADD_OP:
            add_operator = self.token.recognized_string
            self.token = self.get_token()
            operand_2 = self.term()
            w = self.intermediate_code_handler.new_temp(self.symbol_table)
            self.intermediate_code_handler.generate_quad(add_operator, operand_1, operand_2, w)
            operand_1 = w
        expression_place = operand_1
        return expression_place

    def term(self):
        operand_1 = self.factor()
        while self.token.recognized_string in self.MUL_OP:
            mul_operator = self.token.recognized_string
            self.token = self.get_token()
            operand_2 = self.factor()
            w = self.intermediate_code_handler.new_temp(self.symbol_table)
            self.intermediate_code_handler.generate_quad(mul_operator, operand_1, operand_2, w)
            operand_1 = w
        term_place = operand_1
        return term_place

    def factor(self):
        if self.token.family == "number":
            factor_place = self.token.recognized_string
            self.token = self.get_token()
        elif self.token.recognized_string == "(":
            self.token = self.get_token()
            factor_place = self.expression()
            self.check_token_recognized_string_with_message(")", "Parenthesis never closed")
            self.token = self.get_token()
        elif self.token.family == "identifier":
            id = self.token.recognized_string
            self.token = self.get_token()
            factor_place = self.idtail(id)
        else:
            self.error("Expected number or '(' or an identifier, Illegal '" + self.token.recognized_string + "'")
        return factor_place

    def idtail(self, id):
        if self.token.recognized_string == "(":
            self.token = self.get_token()
            self.actual_par_list()
            w = self.intermediate_code_handler.new_temp(self.symbol_table)
            self.intermediate_code_handler.generate_quad('par', w, 'RET', '_')
            self.intermediate_code_handler.generate_quad('call', id, '_', '_')
            self.check_token_recognized_string_with_message(")", "Parenthesis never closed")
            self.token = self.get_token()
            return w
        return id #in this case it is not a function but another variable

    def actual_par_list(self):
        if self.is_expression():
            expression_place = self.expression()
            self.intermediate_code_handler.generate_quad('par', expression_place, 'CV', '_')
            while self.token.recognized_string == ",":
                self.token = self.get_token()
                expression_place = self.expression()
                self.intermediate_code_handler.generate_quad('par', expression_place, 'CV', '_')

    def optional_sign(self):
        if self.token.recognized_string in self.ADD_OP:
            optional_sign_place = self.token.recognized_string
            self.token = self.get_token()
            return optional_sign_place
        return ""

    def condition(self):
        condition_true, condition_false = self.bool_term()
        while self.token.recognized_string == "or":
            self.token = self.get_token()
            self.intermediate_code_handler.backpatch(condition_false,
                                                     self.intermediate_code_handler.next_quad())
            bool_term_true, bool_term_false = self.bool_term()
            condition_true = self.intermediate_code_handler.merge_list(condition_true, bool_term_true)
            condition_false = bool_term_false
        return condition_true, condition_false

    def bool_term(self):
        bool_term_true, bool_term_false =self.bool_factor()
        while self.token.recognized_string == "and":
            self.token = self.get_token()
            self.intermediate_code_handler.backpatch(bool_term_true,
                                                     self.intermediate_code_handler.next_quad())
            bool_factor_true, bool_factor_false =self.bool_factor()
            bool_term_false = self.intermediate_code_handler.merge_list(bool_term_false, bool_factor_false)
            bool_term_true = bool_factor_true
        return bool_term_true, bool_term_false

    def bool_factor(self):
        if self.token.recognized_string == "not":
            self.token = self.get_token()
            self.check_token_recognized_string("[")
            self.token = self.get_token()
            bool_factor_false, bool_factor_true = self.condition()
            self.check_token_recognized_string_with_message("]", "Bracket never closed")
            self.token = self.get_token()
        elif self.token.recognized_string == "[":
            self.token = self.get_token()
            bool_factor_true, bool_factor_false = self.condition()
            self.check_token_recognized_string_with_message("]", "Bracket never closed")
            self.token = self.get_token()
        elif self.is_expression():
            bool_factor_true = self.intermediate_code_handler.make_list(self.intermediate_code_handler.next_quad())
            operand_1 = self.expression()
            self.check_token_family("relOperator")
            rel_operator = self.token.recognized_string
            self.token = self.get_token()
            operand_2 = self.expression()
            self.intermediate_code_handler.generate_quad(rel_operator, operand_1, operand_2, "_")
            bool_factor_false = self.intermediate_code_handler.make_list(self.intermediate_code_handler.next_quad())
            self.intermediate_code_handler.generate_quad("jump", "_", "_", "_")
        else:
            self.error("Expected 'not', '[' or expression, Illegal '" + self.token.recognized_string + "'")
        return bool_factor_true, bool_factor_false

    def call_main_part(self):
        self.check_token_recognized_string("if")
        self.token = self.get_token()
        self.check_token_recognized_string("__name__")
        self.token = self.get_token()
        self.check_token_recognized_string("==")
        self.token = self.get_token()
        self.check_token_recognized_string('"__main__"')
        self.token = self.get_token()
        self.check_token_recognized_string(":")
        self.token = self.get_token()
        self.main_function_call()
        while self.token.family == "identifier":
            self.main_function_call()
        self.intermediate_code_handler.generate_quad("halt", "_", "_", "_")
        self.target_code_handler.generate_target_code_file(self.intermediate_code_handler, self.symbol_table)

    def main_function_call(self):
        self.check_token_family("identifier")
        self.token = self.get_token()
        self.check_token_recognized_string("(")
        self.token = self.get_token()
        self.check_token_recognized_string_with_message(")", "Parenthesis never closed")
        self.token = self.get_token()
        self.check_token_recognized_string(";")
        self.token = self.get_token()

##############################################################
#                       USEFUL METHODS                       #
##############################################################
def print_tokens():
    token = Token("", "", 0)
    print("##### Lexical Analyzer Results #####")
    while token.family != "eof":
        parser.get_token()
        token = parser.lexical_analyzer.token
        print(token.recognized_string + "\t family: " + token.family + "\t line: " + str(token.line_number))
    print("######################################")

def generate_intermediate_code_file():
    for quad in parser.intermediate_code_handler.quad_list:
        intermediate_code_file.write(quad.to_string())

def open_files(filename):
    lex_file = open(filename, "rb")
    int_file = open(filename[:-3] + 'int', 'w')
    symb_file = open(filename[:-3] + "symb", "w")
    tc_file = open(filename[:-3] + "asm", "w")
    return lex_file, int_file, symb_file, tc_file

def close_files():
    lexical_analysis_file.close()
    intermediate_code_file.close()
    symbol_table_file.close()
    target_code_file.close()

if __name__ == "__main__":
    lexical_analysis_file, intermediate_code_file, symbol_table_file, target_code_file = open_files(sys.argv[1])

    parser = Parser()

    # To check the lexical analyser's result
    # Run the following function
    #print_tokens()

    parser.syntax_analyzer()

    generate_intermediate_code_file()

    close_files()



