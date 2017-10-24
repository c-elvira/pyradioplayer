import cmd


class AHomePyShell(cmd.Cmd):
    intro = 'Welcome to the shell.   Type help or ? to list commands.\n'
    prompt = '>>'
    file = None

    # ----- shell commands -----
    def do_quit(self, arg):
        'Close the HomePyServer'
        raise NotImplementedError

    def do_volume(self, arg):
        'Change the volume:  volume 20'
        raise NotImplementedError

    def do_pause(self, arg=None):
        'pause the sound for an optional amount of time, in minute:  pause 60'
        raise NotImplementedError

    def do_play(self, arg=None):
        'play music again aften it has been stopped, in minute:  play'
        raise NotImplementedError

    def do_listen(self, arg):
        """
        Change Media. For instance
        listen youtube url
        """
        raise NotImplementedError


if __name__ == '__main__':
    pass
