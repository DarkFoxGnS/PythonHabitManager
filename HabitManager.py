try:
    import curses
except:
    print("Curses module is not present, please install it using \"pip install windows-curses\" or launch windows-curses install.bat")
    exit()
import time,math,Menu,Task,Analytics
from enum import Enum
from DBManager import DBManager
from DisplayManager import DisplayManager

target_fps = 20 #The software will target 20 frames per second
target_ms = math.floor(1000/target_fps) #This variable is used to ensure constant performance
screen_width = 120 #Defines the display width of the CLI
screen_height = 30 #Defines the display height of the CLI
displayManager = None #Holds the instance of the DisplayManager
dbmanager = None #Holds the instance of the DBManager
tasks = [ ] #A list that will store the tasks
notifications = [ ] #A list that stores the pending notifications, like completion streaks and missed habits

class Menus(Enum):
    """
    This enum holds menu identification related variables
    The enum is safer,faster and more readeable than other methods of identification for menus
    """
    MainMenu = 0 #Main menu
    Habits = 1 #Habits submenu
    ManageHabits = 2 #Habits management submenu
    CheckAnalytics = 3 #Analytics submenu
    PendingHabits = 4 #Pending habits list
    CompletedHabits = 5 #Completed habits list
    AlterHabits = 6 #Habits alteration list
    AddHabits = 7 #Habits alteration menu with a new task
    CompletedAnalytics = 8 #Calculates completed tasks analytics
    MissedAnalytics = 9 #Calculates missed tasks analytics
    SpecificAnalyticsList = 10 #List tasks for analytics
    PendingTask = 11 #Allows a pending task to be completed
    Notifications = 12 #Notification list
    ChangeHabit = 13 #Habits alteration menu
    InputMenu = 14 #Handles letter key inputs and basic text modification
    SpecificAnalytics = 15 #Renders specific task analytics

def exitApp():
    """
    Saves tasks, then exits.
    """
    saveTasks()
    exit()

def loadMenu(menuType):
    """
    It loads a menu based on a Menus enum menuType
    """
    menu = getMenuObject(menuType)
    load(menu)

def loadInputField(input):
    """
    It takes a tuple (Menus menuType,description,text) as an input,
    """
    menu = getMenuObject(input[0])
    menu.display = [
        [0,2,"Use the left and right key to move the cursor, press Enter to comfirm"],
        [1,2,input[1]]
        ]
    menu.text = [*input[2]]
    load(menu)

def loadMenuWithTask(input):
    """
    It provides the ability to load a menu with a task. It takes a tuple (task,menuType) the menu used must support task variable to use this, the Menu class do not support it by default.
    """
    task = input[0]
    menuType = input[1]
    menu = getMenuObject(menuType)
    menu.task = task
    load(menu)

def load(menu):
    """
    This is used to load an already initializated menu. It adds the menu to the end of the stack and then calls the load function of the menu
    """
    displayManager.screen.clear()
    displayManager.stack.append(menu)
    displayManager.currentStack = displayManager.stack[len(displayManager.stack)-1]
    displayManager.currentStack.load()

def back():
    """
    This is called to step back one step in the stack. This does not provide the ability to send back value
    """
    displayManager.screen.clear()
    del displayManager.stack[len(displayManager.stack)-1]
    displayManager.currentStack = displayManager.stack[len(displayManager.stack)-1]
    displayManager.currentStack.fromBack(None)

def backWithValue(value):
    """
    This is called to step back one step in the stack. This provides a way to send data back down the stack.
    """
    displayManager.screen.clear()
    del displayManager.stack[len(displayManager.stack)-1]
    displayManager.currentStack = displayManager.stack[len(displayManager.stack)-1]
    displayManager.currentStack.fromBack(value)

def saveTasks():
    """
    This is used to save all task in the tasks list.
    """
    dbmanager.saveData(tasks)

def saveBack():
    """
    This is used when we want to force a saving, but also backing
    """
    saveTasks()
    back()

def saveTask(task):
    """
    Adds task to the tasks list.
    """
    tasks.append(task)
    dbmanager.saveNewTask(task)
    for task in tasks:
        task.evaluate()
    saveTasks()
    back()

def deleteTask(task):
    tasks.remove(task)
    dbmanager.remove(task)
    del task
    back()

def calculateCompletedAnalytics(menu):
    """
    Requires a menu object as an input.
    Calculates highest completed streak, the name of the habit that achieved that streak, all habits, and the completion rate.
    Set these data as display of the menu object.
    """
    highestStreak = 0
    highestStreakTask = "None"
    completedTasks = 0
    historyCount = 0
    
    for task in tasks:
    
        history = task.getHistory()
        streak = 0
        
        historyCount += Analytics.computeHistoryCount(history)
        completedTasks += Analytics.computeCompleted(history)
        streak = Analytics.computeCompletedStreak(history)
        
        if streak > highestStreak:
            highestStreak = streak
            highestStreakTask = task.getName()
    
    menu.display.append([0,2,"Highest completion streak habit: "+highestStreakTask])
    menu.display.append([1,2,"Highest completion streak: "+str(highestStreak)])
    menu.display.append([2,2,"Completed habit count: "+str(completedTasks)])
    menu.display.append([3,2,"All habit count(completed+missed): "+str(historyCount)])
    if historyCount > 0:
        menu.display.append([4,2,f"Completion rate ({completedTasks}/{historyCount}): {str(completedTasks/historyCount*100)}%"])
    
def calculateMissedAnalytics(menu):
    """
    Requires a menu object as an input.
    Calculates highest missed streak, the name of the habit that achieved that streak, all habits, and the completion rate.
    Set these data as display of the menu object.
    """
    highestStreak = 0
    highestStreakTask = "None"
    missedTasks = 0
    historyCount = 0
    
    for task in tasks:
    
        history = task.getHistory()
        streak = 0
        
        historyCount += Analytics.computeHistoryCount(history)
        missedTasks += Analytics.computeMissed(history)
        streak = Analytics.computeMissedStreak(history)
        
        if streak > highestStreak:
            highestStreak = streak
            highestStreakTask = task.getName()
    
    menu.display.append([0,2,"Highest missing streak habit: "+highestStreakTask])
    menu.display.append([1,2,"Highest missing streak: "+str(highestStreak)])
    menu.display.append([2,2,"Misssed habit count: "+str(missedTasks)])
    menu.display.append([3,2,"All habit count(completed+missed): "+str(historyCount)])
    if historyCount > 0:
        menu.display.append([4,2,f"Missing rate({missedTasks}/{historyCount}): {str(missedTasks/historyCount*100)}%"])

def calculateTaskAnalytics(task):
    """
    Requires a task object as an input.
    Calculates the highest missed streak, the highest completed streak, all habits, and the completion rate, first and last deadline.
    Set these data as display of the menu object.
    """
    menu = getMenuObject(Menus.SpecificAnalytics)
    menu.name = task.getName()
    
    history = task.getHistory()
    
    highestStreak = Analytics.computeCompletedStreak(history)
    completedTasks = Analytics.computeCompleted(history)
    missedTasks = Analytics.computeMissed(history)
    completionRate = Analytics.computeMissedRate(history)
    historyCount = Analytics.computeHistoryCount(history)
    firstDeadline = history[0][2]
    lastDeadline = history[len(history)-1][2]
    
    
    
    load(menu)
    
    menu.display.append([0,2,"Highest completion streak: "+str(highestStreak)])
    menu.display.append([1,2,"Completed habit count: "+str(completedTasks)])
    menu.display.append([2,2,"Misssed habit count: "+str(missedTasks)])
    menu.display.append([3,2,"All habit count(completed+missed): "+str(historyCount)])
    menu.display.append([4,2,f"Completion rate({completedTasks}/{historyCount}): {str(completedTasks/historyCount*100)}%"])
    menu.display.append([5,2,"First deadline: "+time.ctime(firstDeadline)])
    menu.display.append([6,2,"Last deadline: "+time.ctime(lastDeadline)])
    
def getMenuObject(menuType):
    """
    Returns an initializated Menu object (or and instance of one of the subclasses) set up with the respective menu related data, based on the Menus enum menuType
    """
    menu = Menu.SimpleMenu()#A simple menu is initializated, since it's suitable for handling most of the situations.
    menu.menuType = menuType
    defaultBack = True #Used to signal if the default back will be used. Some menus may use the backWithValue function
    match menuType:
        case Menus.MainMenu:#This menu is shown first when the program is started
            menu = Menu.MainMenu(notifications)
            menu.name="MainMenu"
            menu.display = [
            [0,2,"Select an option using the up and down arrows, and access it using the enter key."]
            ]
            menu.functions = [
            ["Access Habits",loadMenu,Menus.Habits],
            ["Manage Habits",loadMenu,Menus.ManageHabits],
            ["Check Analytics",loadMenu,Menus.CheckAnalytics],
            ["Notifications",loadMenu,Menus.Notifications]
            ]
            
        case Menus.Habits:#This submenu is used for selecting all habbit completion related submenus
            menu.name = "Habits"
            menu.display = [
            [0,2,"This menu provides an option to check your habits, and to mark your active habits as completed."]
            ]
            menu.functions = [
            ["Check Pending Habits",loadMenu,Menus.PendingHabits],
            ["Check Completed Habits",loadMenu,Menus.CompletedHabits]
            ]
            
        case Menus.PendingHabits:#This submenu shows the screen where the user can select pending habits from a list.
            data = []
            for task in tasks:
                data += [[task.getName(),loadMenuWithTask,(task,Menus.PendingTask)]]
            
            menu = Menu.PendingListMenu(data)
            menu.name = "Pending Habits"
            menu.display = [
            [0,2,"Select one of your pending habits:"]
            ]
            
        case Menus.ManageHabits:#This menu lists the habit management related submenus
            menu.name = "Manage Habits"
            menu.display = [
            [0,2,"In this menu you can add, remove or alter existing habits:"]
            ]
            menu.functions = [
            ["Add new habit",loadMenu,Menus.AddHabits],
            ["Alter existing habit",loadMenu,Menus.AlterHabits]
            ]
            
        case Menus.PendingTask:#This menu shows the description and the remaining time of the task to the user.
            menu = Menu.TaskMenu()
            menu.display = [
            [0,2,"Description:"],
            [1,2,"<description>"],
            [3,2,"Expires at:"],
            [4,2,"<time>"],
            [6,2,"Time remaining:"],
            [7,2,"<remaining time>"]
            ]
            menu.functions=[["Back",saveBack,None]]
            defaultBack = False
        
        case Menus.CompletedHabits:#This submenu shows the screen where the user sees their already completed habits.
            data = []
            for task in tasks:
                if task.getStatus() != Task.Status.Pending:
                    data += [
                    [task.getName()+" - "+task.getStatus().name,None,None]
                    ]
                
            menu = Menu.ListMenu(data)
            menu.name = "Completed Habits"
            menu.display = [
            [0,2,"Here you can see you completed habits:"]
            ]
            
        case Menus.Notifications:#This submenu shows the available notifications.
            menu = Menu.NotificationsMenu(notifications)
            menu.name = "Notifications"
            menu.display = [
            [0,2,"You can delete your notifications by selecting them and pressing Enter."]
            ]
            
        case Menus.AlterHabits:#This submenu lists the tasks.
            data = []
            for task in tasks:
                data += [["<Task name>",loadMenuWithTask,[task,Menus.ChangeHabit]]]
            
            menu = Menu.AlterHabits(data)
            menu.tasks = tasks
            menu.name = "Alter Habits"
            menu.display = [
            [0,2,"Select a habit to start modifying it:"]
            ]
        
        case Menus.ChangeHabit:#Display the attributes of a specific task, and allows modification of the attributes of the task.
            menu = Menu.AttributeMenu()
            menu.functions+=[
            ["Name:<name>",loadInputField,[Menus.InputMenu,"<description>","<text>"]],
            ["Description:<description>",loadInputField,[Menus.InputMenu,"<description>","<text>"]],
            ["Starting time:<starting time>",loadInputField,[Menus.InputMenu,"<description>","<text>"]],
            ["Periodicity:<periodicity>",loadInputField,[Menus.InputMenu,"<description>","<text>"]],
            ["Back",saveBack,None],
            ["Delete",deleteTask,"<Task to delete>"]
            ]
            
            defaultBack = False
            
        case Menus.InputMenu:#Handles input from the keyboard.
            menu = Menu.InputMenu()
            menu.functions = [
            ["Comfirm",backWithValue,"<value>"]
            ]
            defaultBack = False
        
        case Menus.AddHabits:#Creates a new habits, and displays it's attributes, allows for modification of the attributes.
            menu = Menu.NewAttributeMenu()
            menu.functions+=[
            ["Name:<name>",loadInputField,[Menus.InputMenu,"<description>","<text>"]],
            ["Description:<description>",loadInputField,[Menus.InputMenu,"<description>","<text>"]],
            ["Starting time:<starting time>",loadInputField,[Menus.InputMenu,"<description>","<text>"]],
            ["Periodicity:<periodicity>",loadInputField,[Menus.InputMenu,"<description>","<text>"]],
            ]
            task = Task.Task((-1,"","",0,0))
            task.bindNotifications(notifications)
            menu.task = task
            menu.functions.append(["Add new task",saveTask,task])
        
        case Menus.CheckAnalytics:#Analytics submenu.
            menu.name = "Analytics"
            menu.display = [
            [0,2,"In this menu you can access your statistics and analytics."]
            ]
            menu.functions =[
            ["Completed analytics",loadMenu,Menus.CompletedAnalytics],
            ["Missed analytics",loadMenu,Menus.MissedAnalytics],
            ["Habit related analytics",loadMenu,Menus.SpecificAnalyticsList]
            ]
        
        case Menus.CompletedAnalytics:#Displays the analytics related to completed tasks.
            menu.name = "Completed Habit Analytics"
            calculateCompletedAnalytics(menu)
        
        case Menus.MissedAnalytics:#Displays the analytics related to missed tasks.
            menu.name = "Missed Habit Analytics"
            calculateMissedAnalytics(menu)
        
        case Menus.SpecificAnalyticsList:#Displays analytics related to a specific task.
            data = []
            for task in tasks:
                data.append([task.getName(),calculateTaskAnalytics,task])
            
            menu = Menu.ListMenu(data)
            menu.name = "Specific Habit Analytics"
            menu.display = [
            [0,2,"Select one of your habits to get specific analytics:"]
            ]
        
        case Menus.SpecificAnalytics:#This menu is reserved for further data modification if required.
            pass
        case _:#It is mainly used for development purposes, so the application does not go into an unsafe state.
            menu.name = "Not Yet Implemented"
    
    #This part appends the function list with a back option, or with an exit option if the user is on the main menu.
    
    
    if not defaultBack:#If no back is required by default, that means that it was solved otherwise, like passing back data.
        return menu
        
    if menuType != Menus.MainMenu:#Simple check to which kind of data to append.
        menu.functions += [["Back",back,None]]
    else:
        menu.functions += [["Exit",exitApp,0]]
            
    return menu

def main(screen):
    """
    This is the main function of the program, it fills the value of the variables:
        -displayManager
        -dbmanager
        -tasks
    It evaluates the tasks on launch, and prepares the curses window.
    
    After then it starts running the main loop:
        -Calls update on the displayManager
        -refreshes the screen
        -stops the thread to wait for 20 frames per second
        -every 1200 frames (roughly 1 minute) call evaluate on all tasks
    """
    
    curses.resize_term(screen_height,screen_width)
    curses.curs_set(False)
    screen.nodelay(1)
    screen.addstr("Loading...")
    screen.refresh()
    
    global displayManager
    global dbmanager
    displayManager = DisplayManager(screen)
    dbmanager = DBManager()
    dbmanager.loadData(tasks)
    
    screen.addstr("\nUpdating...")
    screen.refresh()
    for task in tasks:
        task.bindNotifications(notifications)
        task.evaluate()
    screen.addstr("\nSaving...")
    screen.refresh()
    saveTasks()
    
    loadMenu(Menus.MainMenu)
    
    counter = 0
    while True: #Main Loop
        frameStart = time.time()
        displayManager.update()
        screen.refresh()
        
        if counter == target_fps*60:
            counter = 0
            for task in tasks:
                task.evaluate()
                saveTasks()
        counter+=1
        
        curses.napms(target_ms-math.floor(time.time()-frameStart))
        
        

if(__name__ == "__main__"): #Only executed if the main the file is launched. This makes pydoc generation easier.
    curses.wrapper(main)#Curses will create a command line interface, and passes it to the function and calls it.