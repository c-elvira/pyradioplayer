import cmd
import time


class PyRadioShell(cmd.Cmd):
    intro = 'Welcome to the shell.   Type help or ? to list commands.\n'
    prompt = '>>'
    file = None

    # ----- basic turtle commands -----
    def do_ok(self, arg):
        'Move the turtle forward by the specified distance:  FORWARD 10'
        print('ok')

    def do_right(self, arg):
        'Turn turtle right by given number of degrees:  RIGHT 20'
        print('right')

    def do_left(self, arg=None):
        'Turn turtle left by given number of degrees:  LEFT 90'
        if arg == '':
            print('Error, arg is none')
        else:
            print('left ' + str(arg))


if __name__ == '__main__':
    time.sleep(1)
    PyRadioShell().onecmd('left')

    time.sleep(1)
    PyRadioShell().onecmd('left 10')
