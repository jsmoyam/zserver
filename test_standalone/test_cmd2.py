import cmd2

class MyApp(cmd2.Cmd):

    def __init__(self):
        # Enable the optional ipy command if IPython is installed by setting use_ipython=True
        super().__init__()
        # self._set_prompt()
        # self.intro = 'Sky shell'

        # To hide commands from displaying in the help menu, add them to the hidden_commands list
        # self.hidden_commands.append('py')
        # self.hidden_commands.append('pyscript')
        self.default_to_shell = True

    def do_foo(self, args):
        """This docstring is the built-in help for the foo command."""

        print('foo bar baz {}'.format(args))

if __name__ == '__main__':
    c = MyApp()
    c.cmdloop()