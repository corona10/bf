from rpython.rlib.jit import JitDriver, purefunction

def get_location(pc, program, bracket_map):
    return "%s_%s_%s" % (
            program[:pc], program[pc], program[pc+1:]
            )

jitdriver = JitDriver(greens=['pc', 'program', 'bracket_map'],
                      reds=['tape'], get_printable_location=get_location)

import os
import sys

class Tape:
    def __init__(self):
        self.the_tape = [0]
        self.pos = 0

    def get(self):
        return self.the_tape[self.pos]

    def set(self, v):
        self.the_tape[self.pos] = v

    def inc(self):
        self.the_tape[self.pos] += 1

    def dec(self):
        self.the_tape[self.pos] -= 1

    def advance(self):
        self.pos += 1
        if len(self.the_tape) <= self.pos:
            self.the_tape.append(0)

    def devance(self):
        self.pos -= 1


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()


@purefunction
def get_matching_bracket(bracket_map, pc):
    return bracket_map[pc]


def mainloop(program, bracket_map):
    tape = Tape()
    pc = 0
    while pc < len(program):
        jitdriver.jit_merge_point(pc=pc, tape=tape, program=program,
               bracket_map=bracket_map)
        code = program[pc]
        if code == '>':
            tape.advance()
        elif code == '<':
            tape.devance()
        elif code == '+':
            tape.inc()
        elif code == '-':
            tape.dec()
        elif code == '.':
            os.write(1, chr(tape.get()))
        elif code == ',':
            tape.set(ord(os.read(0, 1)[0]))
        elif code == '[' and tape.get() == 0:
            pc = get_matching_bracket(bracket_map, pc)
        elif code == ']' and tape.get() != 0:
            pc = get_matching_bracket(bracket_map, pc)

        pc += 1


def parse(program):
    parsed = []
    bracket_map = {}
    leftstack = []

    pc = 0
    for c in program:
        if c in '[]<>+-,.':
            parsed.append(c)
            if c == '[':
                leftstack.append(pc)
            elif c == ']':
                left = leftstack.pop()
                right = pc
                bracket_map[left] = right
                bracket_map[right] = left
            pc += 1

    return ''.join(parsed), bracket_map


def run(f):
    program, m = parse(f.read())
    mainloop(program, m)


def entry_point(argv):
    try:
        fname = argv[1]
    except IndexError as e:
        print('Please execute with a file name')
        return 1
    with open(fname, 'r') as f:
        run(f)
    return 0


def target(*args):
    return entry_point, None


if __name__ == '__main__':
    entry_point(sys.argv)
