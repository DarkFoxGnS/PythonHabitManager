"""
This file contains information about the displayable menus of the application, some menus require custom driver code, thus they were redefined as a subclass with added functionality.
"""
from DBManager import DBManager
from Task import Status
import HabitManager, curses, time, math

unitTable = [
("day(s)",86400),
("hour(s)",3600),
("minute(s)",60),
("second(s)",1),
]

class Menu:
    """
    This is a class that contains the data and the functionality of a Menu that can be displayed by the DisplayManager class.
    """
    def __init__(this):
        """
        name: This is the name of the Menu displayed on the top of the screen.
        menuPointer: This is an integer that represents the currently selected option.
        display: This is a list of tuples in the form of (row, column, dataID) that will draw the content of data at dataID at row,column.
        data: A list of strings that can be modified or written on the screen.
        functions: A list of tuples in the form of ("DisplayText",function,arg) where the "DisplayText" will be written to the screen as an option, the function will be called with the argument of arg when the user selects it.
        """
        this.name = ""
        this.menuPointer = 0
        this.display = []
        this.functions = []
        this.menuType = None
        
    def load(this):
        """
        This function is called when the menu is first loaded into the display manager. Can be overwritten to add more functionality.
        """
        pass
       
    def update(this,character):
        """
        This function is called every frame of the application, and is to be used to handle the inputs of the current visible Menu. Can be overwritten to add further functionality.
        """
        pass
        
    def show(this,screen):
        """
        This function is called every frame of the application, and is to be used as a driver for the graphics in the current Menu.
        """
        pass
    
    def fromBack(this,value):
        """
        This function is called when a submenu is exited and the fucos is returned to this menu.
        """
        pass

class SimpleMenu(Menu):
    """
    This is a subclass of Menu providing simple controls for menu navigation.
    """
    def update(this,character):
        """
        Handles simple menu navigation. Provides support for up and down arrow keys and the enter key.
        """
        match character:
            case 259:
                if(this.menuPointer > 0):
                    this.menuPointer-=1
            case 258:
                if(this.menuPointer < len(this.functions)-1):
                    this.menuPointer+=1
            case 10:
                function = this.functions[this.menuPointer][1]
                arg = this.functions[this.menuPointer][2]
                if function == None:
                    return
                    
                if arg:
                    function(arg)
                else:
                    function()
    
    def show(this,screen):
        """
        Handles simple display of the this.display and this.functions list
        """
        row = 1
        localRow = 0
        indent = 2
        overFlowCompensation = 0
        for item in this.display:
            screen.addstr(item[0]+row,item[1],item[2])
            if (lenght := len(item[2])//HabitManager.screen_width) > 0:
                row+=lenght
                overFlowCompensation+=lenght
            localRow = item[0]
        row = localRow+overFlowCompensation
        
        curIndex = 0
        row+=2
        for item in this.functions:
            row +=1
            if this.menuPointer == curIndex:
                screen.addstr(row,indent, item[0],curses.A_REVERSE)
            else:
                screen.addstr(row,indent, item[0])
            curIndex +=1

class MainMenu(SimpleMenu):
    """
    This is a subclass of SimpleMenu providing live update to the notification counter in the main menu.
    """
    def __init__(this,data):
        """
        Adds data into the this.data
        Calls super().__init__()
        """
        super().__init__()
        this.data = data
    
    def show(this,screen):
        """
        Shows the notification count as well.
        Calls super().show(screen)
        """
        this.functions[3][0] = "Notifications ("+str(len(this.data))+")"
        
        super().show(screen)

class ListMenu(SimpleMenu):
    """
    This is a subclass of SimpleMenu providing support for list based menus (example: list of habits).
    """
    
    def __init__(this,data):
        """
        Calls super().__init__().
        Assigns data to this.data list of lists in the form of [display text, function pointer, args] it is used as the selectible display data.
        Creates this.tasks list, which can be used for holding the tasks array (Data is filled, this can be skipped, otherwise it is used as data[0] (display text)).
        Creates this.listPointer integer shows which screen we are on.
        Creates this.clearScreen boolean, it requests a screen clear.
        """
        super().__init__()
        this.data = data
        this.tasks = []
        this.listPointer = 0
        this.clearScreen = 0
    
    def cycleListUp(this):
        """
        This function is used mainly as a function pointer used for this.functions list.
        Increments this.listPointer by one.
        Calls this.load()
        """
        this.listPointer+= 1
        this.load()
        pass
    
    def cycleListDown(this):
        """
        This function is used mainly as a function pointer used for this.functions list.
        Decrements this.listPointer by one.
        Calls this.load()
        """
        this.listPointer-= 1
        this.load()
        pass
    
    def load(this):
        """
        Requests screen clear.
        Resets this.menuPointer to 0.
        If possible fills data with names from task.
        Fills functions from data to create the displayed list. 10 elements of data is used for one page.
        """
        this.clearScreen = 1
        this.menuPointer = 0
        
        for i in range(0,len(this.tasks)):#If tasks are not passed in, it will not run and data is used raw
            this.data[i][0] = this.tasks[i].getName()
        
        this.functions = [this.functions[0]]
        if this.listPointer > 0:
            this.functions += [("<Previous page>",this.cycleListDown,None)]
        
        displayCount = 10
        try:
            for i in range(0,displayCount):
                this.functions += [this.data[this.listPointer*displayCount+i]]
        except:
            pass
        
        if len(this.data) > (this.listPointer+1)*displayCount:
            this.functions += [("<Next page>",this.cycleListUp,None)]
    
    def fromBack(this,data):
        """
        Called when the display returns to this menu.
        Calls this.load()
        """
        this.load()
    
    def show(this,screen):
        """
        Provides am option to clear screen.
        Calls super().show(screen)
        """
        if this.clearScreen == 1:
            screen.clear()
            this.clearScreen = 0
        super().show(screen)

class PendingListMenu(ListMenu):
    """
    Special menu created for the Pending List Menu
    """
    def __init__(this,data):
        """
        input data is a array of arrays in the form of [name of task, function pointer, [task, Menus enum menuType]]
        Calls super().__init__() with a list as an argument, that is filltered on the respective task being pending from data[2][0]
        """
        temp = []
        for item in data:
            if item[2][0].getStatus() == Status.Pending:
                temp+=[item]
        super().__init__(temp)
    
    def fromBack(this,value):
        """
        Called when returning from the next menu.
        Refreshes the content of the displayed list, filters completed tasks.
        """
        temp = []
        for item in this.data:
            if item[2][0].getStatus() == Status.Pending:
                temp+=[item]
        this.data = temp
        this.load()
   
class TaskMenu(SimpleMenu):
    """
    A menu used for displaying peding tasks, and allowing them to be marked as completed.
    """
    def __init__(this):
        """
        Calls super().init()
        Creates this.task for storing task.
        """
        super().__init__()
        this.task = None
        
    def markComplete(this):
        """
        Marks current task as complete.
        Leaves this menu.
        """
        this.task.markCompleted()
        this.functions[0][1]()
        
    def load(this):
        """
        Calls super.load()
        Adds mark as complete function.
        Sets current menu name to the task name.
        """
        super().load()
        this.functions+=[["Mark as complete",this.markComplete,None]]
        this.name = this.task.getName()
        
    def show(this,screen):
        """
        Displays the task description.
        Displays the task deadline.
        Displays the task periodicity.
        Calls super().show(screen)
        """
        timer = ""
        tilltime = this.task.getDeadline()-time.time()
        if tilltime < 0:
            tilltime = 0
            this.task.evaluate()
        for item in unitTable:
            temp = math.floor(tilltime/item[1])
            tilltime-=temp*item[1]
            
            timer += str(temp)+" "+item[0]+" "
        
        
        this.display[1] = (1,2,this.task.getDescription())
        this.display[3] = (4,2,time.ctime(this.task.getDeadline()))
        this.display[5] = (7,2,timer)
        
        
        super().show(screen)

class AttributeMenu(SimpleMenu):
    """
    Special menu for displaying Attributes of a task.
    """
    def __init__(this):
        """
        Calls super().__init__()
        Defines this.task, will hold the current data.
        Defines this.saved is used to signal the user if the data is saved.
        Defines this.requestClear, used to signal that the screen needs a full clear.
        """
        super().__init__()
        this.task = None
        this.saved = True
        this.requestClear = False
    
    def load(this):
        """
        Adds Save function to the functions list.
        Sets this.tempName as the name of this.task
        Sets this.tempDescription as the description of this.task
        Sets this.tempDeadline as the deadline of this.task
        Sets this.tempPeriodicity as the periodicity of this.task
        Calls this.refreshText()
        """
        
        this.functions.insert(4,["Save",this.save,None])
        this.functions[6][2] = this.task
        this.tempName = this.task.getName()
        this.tempDescription = this.task.getDescription()
        this.tempDeadline = this.task.getDeadline()
        this.tempPeriodicity = this.task.getPeriodicity()
        this.refreshText()
        
    def save(this):
        """
        Sets task attributes as the temporary attributes.
        Request clear.
        Marks the content as saved.
        Calls this.refreshText()
        """
        this.task.setName(this.tempName)
        this.task.setDescription(this.tempDescription)
        this.task.setDeadline(this.tempDeadline)
        this.task.setPeriodicity(this.tempPeriodicity)
        
        this.requestClear = True
        this.saved = True
        this.refreshText()
        pass
    
    def refreshText(this):
        """
        Fills the functions list with the respective content to fill the page with relative data.
        """
        timer = ""
        tilltime = this.tempPeriodicity
        for item in unitTable:
            temp = math.floor(tilltime/item[1])
            tilltime-=temp*item[1]
            
            timer += str(temp)+""+item[0][0]+" "
    
        if this.saved:
            this.name = this.tempName
        else:
            this.name = this.tempName+"(Not saved)"
        
        if len(name := this.tempName) > 90:
            this.functions[0][0]=f"Name: {name[0:90]}..."
        else:
            this.functions[0][0]=f"Name: {name}"
            
        if len(description := this.tempDescription) > 90:
            this.functions[1][0]=f"Description: {description[0:90]}..."
        else:
            this.functions[1][0]=f"Description: {description}"
        this.functions[2][0]=f"Deadline: {time.ctime(this.tempDeadline)}"
        this.functions[3][0]=f"Periodicity: {timer}"
        
        #Load text and name into the arguments
        this.functions[0][2][1] = "Enter the name of the task:"
        this.functions[0][2][2] = this.task.getName()
        #Load text and description into the arguments
        this.functions[1][2][1] = "Enter the description of the task"
        this.functions[1][2][2] = this.task.getDescription()
        #Load text and formated deadline into the task
        this.functions[2][2][1] = "Enter the deadline of the task. Format(\"year-month-day hour:minute:second\") Example: \"2024-06-12 15:35:20\""
        timeStruct = time.localtime(this.task.getDeadline())
        timeStr = str(timeStruct.tm_year)+"-"+str(timeStruct.tm_mon)+"-"+str(timeStruct.tm_mday)+" "+str(timeStruct.tm_hour)+":"+str(timeStruct.tm_min)+":"+str(timeStruct.tm_sec)
        this.functions[2][2][2] = timeStr
        #Load text and fromated periodicity into the task
        this.functions[3][2][1] = "Enter the periodicity of the task. Format(\"?d ?h ?m ?s\") Example: \"5d 5h 0m 0s\""
        #To-Do Format text
        this.functions[3][2][2] = timer
        
    def fromBack(this,value):
        """
        Called when coming back from the next menu.
        Stores value in the respective temporary attribute.
        """
        this.saved = False
        match this.menuPointer:
            case 0: #Name
                this.tempName = value
            case 1: #Description
                this.tempDescription=value
                pass
            case 2: #Deadline
                try:
                    seconds = time.mktime(time.strptime(value,"%Y-%m-%d %H:%M:%S"))
                except:
                    seconds = 0
                this.tempDeadline = seconds
            case 3: #Periodicity
                seconds = 0
                try:
                    elements = value.split(" ")
                    for i in range(0,4):
                        seconds += int(elements[i][:-1])*unitTable[i][1]
                except:
                    pass
                this.tempPeriodicity = seconds
        this.refreshText()
        
    def show(this,screen):
        """
        Allows the screen to be cleared.
        Calls super().show(screen)
        """
        if this.requestClear:
            screen.clear()
            this.requestClear = False
        super().show(screen)
        
class NewAttributeMenu(AttributeMenu):
    """
    Functions close to AttributeMenu, but it saves every change constantly, since a new task cannot be reverted to the previous state.
    """
    def load(this):
        """
        Same as super().load(), but removes the added save option.
        """
        this.tempName = this.task.getName()
        this.tempDescription = this.task.getDescription()
        this.tempDeadline = this.task.getDeadline()
        this.tempPeriodicity = this.task.getPeriodicity()
        this.refreshText()
    
    def fromBack(this,value):
        """
        Called when returning from the next menu.
        Loads value into the respective task attribute.
        """
        super().fromBack(value)
        match this.menuPointer:
            case 0: #Name
                this.task.setName(value)
            case 1: #Description
                this.task.setDescription(value)
                pass
            case 2: #Deadline
                try:
                    seconds = time.mktime(time.strptime(value,"%Y-%m-%d %H:%M:%S"))
                except:
                    seconds = 0
                this.task.setDeadline(seconds)
            case 3: #Periodicity
                seconds = 0
                try:
                    elements = value.split(" ")
                    for i in range(0,4):
                        seconds += int(elements[i][:-1])*unitTable[i][1]
                except:
                    pass
                this.task.setPeriodicity(seconds)
        this.saved = True
        this.requestClear = True
        this.refreshText()
    
class NotificationsMenu(ListMenu):
    """
    Notifications menu were created to display notifications.
    """
    def __init__(this,notifications):
        """
        Creates this.notifications, which holds the passed in notifications list.
        Calls super().__init__(data) with data as a list of [notification,None,None]
        """
        this.notifications = notifications
        data = []
        for notification in notifications:
            data += [[notification,None,None]]
            
        super().__init__(data)
    
    def removeAll(this):
        """
        Removes all notifications from the notifications list.
        """
        this.data.clear()
        this.notifications.clear()
        this.menuPointer = 0
        this.listPointer = 0
        this.load()
        
    def load(this):
        """
        Calls super().load().
        Adds Remove all notifications button.
        """
        super().load()
        if len(this.data) > 0:
            this.functions += [["Remove all notifications",this.removeAll,None]]
    
    def update(this,character):
        """
        Handles simple menu navigation. Provides support for up and down arrow keys and the enter key.
        Allows the removal of items in the notifications list.
        """
        match character:
            case 259:
                if(this.menuPointer > 0):
                    this.menuPointer-=1
            case 258:
                if(this.menuPointer < len(this.functions)-1):
                    this.menuPointer+=1
            case 10:
                function = this.functions[this.menuPointer][1]
                arg = this.functions[this.menuPointer][2]
                if function == None:
                    displayCount = 10
                    index = 0
                    if this.listPointer > 0:
                        index = -1
                    index+= this.menuPointer+displayCount*this.listPointer-1
                    this.notifications.pop(index)
                    this.data.pop(index)
                    this.load()
                    return
                if arg:
                    function(arg)
                else:
                    function()

class InputMenu(SimpleMenu):
    """
    Special menu to record all inputs made on the keyboard, and use some of it to allow the user to input data into the software.
    """
    def __init__(this):
        """
        Calls super().__init__().
        Sets the name of the menu as Input.
        Defines this.text. Which will be used as a temporal holder to the textual data.
        Defines this.textPointer, which will mark the current position of the cursor.
        Defines this.requestClear to request screen clearing.
        """
        super().__init__()
        this.name = "Input"
        this.text = []
        this.textPointer = 0
        this.requestClear = False
        
    def show(this,screen):
        """
        Clears the screen if needed.
        Calls super().show(screen).
        Display this.text on the screen, along with the cursor.
        """
        if this.requestClear:
            screen.clear()
            this.requestClear = False
        super().show(screen)
        counter = 0
        screen.addstr("\r\n\r\n")
        if this.textPointer == 0:
            screen.addstr(" ",curses.A_REVERSE)
        for character in this.text:
            if counter == this.textPointer-1:
                screen.addstr(character)
                screen.addstr(" ",curses.A_REVERSE)
            else:
                screen.addstr(character)
            counter += 1
    
    def load(this):
        """
        Sets this.textPointer to the end of the text.
        """
        this.textPointer = len(this.text)
    
    def update(this,character):
        """
        Handles key inputs like backspace, cursor movement using the left and right key, delete, enter and appends all the pressed keys to the cursors location in this.text.
        Calls super().update(charater)
        """
        match character:
            case -1: #Curses will return -1 when no key was pressed
                pass
                
            case 8: #Backspace 
                deleteIndex = this.textPointer-1
                if deleteIndex < 0:
                    return
                this.text.pop(deleteIndex)
                this.requestClear = True
                this.textPointer-=1
                
            case 330: #Delete
                if this.textPointer+1 > len(this.text):
                    return
                this.text.pop(this.textPointer)
                this.requestClear = True
                
            case 260: #Left key
                if this.textPointer > 0:
                    this.textPointer-=1
            case 261: #Right key
                if this.textPointer < len(this.text):
                    this.textPointer+=1
            case 10: #Enter
                returnText = "".join(this.text)
                if len(returnText) == 0:
                    returnText = " "
                this.functions[0][2] = returnText
            case _: #Default
                this.text.insert(this.textPointer,chr(character))
                this.textPointer+=1
                
        super().update(character)

class AlterHabits(ListMenu):
    """
    This class is used to allow the tasks to be deleted from this.tasks and have this.data match that behaviour.
    """
    def fromBack(this,value):
        """
        Refresh this.data to match with this.tasks.
        Calls super().fromBack(value)
        """
        removable = [i for i in this.data if not i[2][0] in this.tasks]
        
        for item in removable:
            this.data.remove(item)
        
        super().fromBack(value)