import time,curses

singleton = None

class DisplayManager:
    
    def __init__(this,screen):
        """
        Defines:
            this.stack, a list that will hold menu objects to represent the menu stack.
            this.currentStack, it represents the current menu in the stack.
            this.screen, this is curses.screen object used to display on the command line.
            Assigns screen to this.screen
        """
        global singleton
        if singleton:
            return None
        singleton = this
        this.stack = []
        this.currentStack = None
        this.screen = screen
    
    def show(this):
        """
        Displays the Stack on the screen in the first row.
        Displays the current time on the screen in the first row.
        Calls currentStack.show(screen)
        """
        this.screen.addstr(0,0,this.getStack())
        this.screen.addstr(0,96, str(time.ctime(time.time())))
        
        this.currentStack.show(this.screen)
    
    def handleKeyboard(this):
        """
        Returns the keycode of the pressed key.
        Returns -1 if no key was pressed in this frame.
        """
        return this.screen.getch()
    
    def getStack(this):
        """
        Returns the stack where all the names of the menus are stringed together.
        If the string is larger than 90 characters, then the last 90 characters are showed only.
        """
        stack = ' '.join([str(elem.name)+">" for elem in this.stack])
        if len(stack) >= 90:
            stack ="..."+stack[-90:]
        return stack
    
    def update(this):
        """
        Calls this.handleKeyboard()
        Calls currentStack.update(character)
        Calls this.show()
        """
        character = this.handleKeyboard()
        this.currentStack.update(character)
        this.show()