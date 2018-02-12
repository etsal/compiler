import sys
import ply.lex as ply_lex
from ply.lex import LexToken
import compiler.parser.tokrules as tokrules
from compiler.parser.tokrules import tokens, reserved

class DanaLexer(object):
    tokens = tokens

    def __init__(self, **kwargs):
        self.lexer = ply_lex.lex(module=tokrules, **kwargs)
        self.drivers = list()
        self.tabs = 0
        self.new_stmt = False
        self.saved = None
    

    def input(self, s):
        return self.lexer.input(s)

    # Compute the column of a token - needed for the offside rule
    def col(self, pos):
        newline = max(0, self.lexer.lexdata.rfind('\n', 0, pos))
        return (pos - newline) + 1 
        
    def token(self):
        # If we have saved a token for later, we pop it now
        t = self.saved
        self.saved = None
        if not t:
            t = self.lexer.token()

        # Pop all remaining scopes if the file has ended
        if t is None:
            if self.drivers:
                self.drivers.pop()
                self.saved = t
                return self.emit_autoend()        
            return t
                        
        # Try to pop scopes if in a new line
        if self.new_stmt:
            self.new_stmt = False
            next_col = self.col(t.lexpos)
            if self.drivers and next_col <= self.drivers[-1]:
                self.drivers.pop()
                self.saved = t
                self.new_stmt = True
                return self.emit_autoend()

        # Save driver columns 
        if t.type in ["DEF", "IF", "ELIF", "ELSE", "LOOP"]:
            self.drivers.append(self.col(t.lexpos))
        

        return t


    @property
    def tabs(self):
        return self.lexer.tabs

    @tabs.setter
    def tabs(self, value):
        self.lexer.tabs = value

    @property
    def new_stmt(self):
        return self.lexer.new_stmt

    @new_stmt.setter
    def new_stmt(self, value):
        self.lexer.new_stmt = value

    @property
    def lineno(self):
        return self.lexer.lineno
        
    @property
    def lexpos(self):
        return self.lexer.lexpos


    def emit_autoend(self):
        tok = LexToken()
        tok.type = "AUTO_END"
        tok.value = ""
        tok.lineno = self.lineno
        tok.lexpos = self.lexpos
        return tok


def lex():
    return DanaLexer()
