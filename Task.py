import time,math
from enum import Enum

class Status(Enum):
    Failed = 0
    Completed = 1
    Pending = 2

class Task():
    def __init__(this,data):
        """
        The data input should be a 5 element list or tuple containing the following:
            -id: The id of the task. -1 represents that the task is newly created. The Id is uniquely assigned by the SQL database uppon saving.
            -name: The name of the task
            -description: The description of the task
            -deadline: The deadline of the task in seconds since epoch. The newly created task will start counting from this time.
            -periodicity: The periodicity of the task represented in seconds since epoch.
        This method also creates 3 other variables:
            -__history: A private array for storing history in the form of [id,success,deadline,date of completion or failure]
            -__status: The current status of the task, it will mostly either take the for of pending or success.
            -notifications: This is a reference to the notifications list defined in the main file. It is used to push new notifications to the list.
        """
        this.__id = int(data[0])
        this.__name = str(data[1])
        this.__description = str(data[2])
        this.__deadline = int(data[3])
        this.__periodicity = int(data[4])
        
        this.__history = []
        this.__status = Status.Pending
        this.notifications = None
    
    
    def __str__(this):
        """
        Override the __str__ method to make debugging easier.
        """
        return "Type:"+super().__str__()+", ID:"+str(this.__id)+", Name:"+str(this.__name)
    
    def bindNotifications(this,notifications):
        """
        Bind the notifications list to the task, so it can push notifications to the list.
        """
        this.notifications = notifications
    
    def evaluate(this):
        """
        This function is called on the start of the program, and every 1 minute of the program running. It's job is to handle the evaluation of the tasks.
        """
        curtime = time.time()
            
        if len(this.__history)>0:
            lastHistory = this.__history[len(this.__history)-1]
            if(lastHistory[1] == Status.Completed.value and lastHistory[2] == this.__deadline):
                this.__status = Status.Completed
                
        while curtime > this.__deadline and this.__periodicity != 0 and this.__deadline != 0:
            if this.__status != Status.Completed:
                this.__history.append([this.__id,Status.Failed.value,this.__deadline,this.__deadline])
                this.notifications.insert(0,f"You missed \"{this.__name}\" at {time.ctime(this.__deadline)}")
            this.__status = Status.Pending
            this.__deadline += this.__periodicity
            
    def markCompleted(this):
        """
        This is called to mark this task completed. And push the completion history, and compute the completion streak. If the user achieves a streak, it is pushed to the notifications.
        It does not progress the deadline. That is done during evaluation.
        """
        this.__history.append([this.__id,Status.Completed.value,this.__deadline,math.floor(time.time())])
        this.__status = Status.Completed
        streak = 0
        if len(this.__history) > 0:
            for i in range(len(this.__history)-1,-1,-1):
                if this.__history[i][1] == 1:
                    streak+=1
                else:
                    break
        if streak > 1:
            this.notifications.insert(0,f"Congratulations, you are on a streak with {streak} completions in a row in {this.__name}")
            
    def getId(this):
        """
        Returns the id of the task.
        """
        return this.__id
    
    def getName(this):
        """
        Returns the name of the task.
        """
        return this.__name
    
    def getDescription(this):
        """
        Returns the description of the task.
        """
        return this.__description
    
    def getDeadline(this):
        """
        Returns the deadline of the task.
        """
        return this.__deadline
    
    def getPeriodicity(this):
        """
        Returns the periodicity of the task.
        """
        return this.__periodicity
    
    def getHistory(this):
        """
        Returns the history list [id, success, deadline is seconds since epoch, completion date in seconds since epoch] of the task.
        """
        return this.__history
        
    def getStatus(this):
        """
        Returns the status of the task.
        """
        return this.__status
    
    def setId(this,value):
        """
        Set the id of the task.
        """
        this.__id = int(value)
    
    def setName(this,value):
        """
        Set the name of the task.
        """
        this.__name = str(value)
    
    def setDescription(this,value):
        """
        Set the description of the task.
        """
        this.__description = str(value)
    
    def setDeadline(this,value):
        """
        Set the deadline of the task.
        """
        this.__deadline = int(value)
    
    def setPeriodicity(this,value):
        """
        Set the periodicity of the task.
        """
        this.__periodicity = int(value)
    
    def setHistory(this,value):
        """
        Set (replace) the history list of the task.
        """
        this.__history = value
        
    