import cmd


class AHomePyShell(cmd.Cmd):
    intro = 'Welcome to the shell.   Type help or ? to list commands.\n'
    prompt = '>>'
    file = None

    # ----- basic turtle commands -----
    def do_quit(self, arg):
        'Close the HomePyServer'
        raise NotImplementedError

    def do_volume(self, arg):
        'Change the volum:  volume 20'
        raise NotImplementedError

    def do_pause(self, arg=None):
        'pause the sound for an optional amount of time, in minute:  pause 60'
        raise NotImplementedError


if __name__ == '__main__':
    pass