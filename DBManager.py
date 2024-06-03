import sqlite3,time,math
from Task import Task

manager = None

class DBManager():
    def __init__(this):
        """
        Creates a singleton DBManager object.
        Connects to the Database
        Gets cursor, so it's able to make queries on the database.
        """
        global manager
        if manager:
            return None
        manager = this
        this.con = sqlite3.connect("Database.db")
        this.cur = this.con.cursor()
    
    def getData(this,request):
        """
        Receives data from the database and returns the list, based on the String SQL request.
        """
        this.cur.execute(request)
        response = this.cur.fetchall()
        return response
        
    def setData(this,command):
        """
        Executes commands on the database. Uses String SQL command as the command to execute.
        """
        this.cur.execute(command)
    
    def commit(this):
        """
        Commits the updates made to the database using the this.setData() function.
        """
        this.con.commit()
    
    def getManager():
        """
        Returns the singleton DBManager object.
        """
        return manager
    
    def remove(this,task):
        """
        Removes task from the database.
        """
        this.setData(f"DELETE FROM Tasks where id = {task.getId()}")
        this.setData(f"DELETE FROM History where id = {task.getId()}")
        this.commit()
    
    def loadData(this,list):
        """
        Loads data from the database into the list. The passed in list will be a list of Task objects.
        """
        data = this.getData("SELECT * FROM Tasks")
        for item in data:
            task = Task(item)
            history = this.getData(f"SELECT * FROM History WHERE id = {task.getId()}")
            task.setHistory(history)
            list += [task]
    
    def saveNewTask(this,task):
        """
        Saves a new task into the database, and gives the task a unique identifier.
        """
        this.setData(f"INSERT INTO Tasks (name,description,deadline,periodicity) VALUES (\"{task.getName()}\",\"{task.getDescription()}\",{task.getDeadline()},{task.getPeriodicity()});")
        task.setId(this.getData("SELECT COUNT(id) FROM Tasks")[0][0])
        
        for history in task.getHistory():
            this.setData(f"INSERT INTO History VALUES ({history[0]},{history[1]},{history[2]},{history[3]});")
        
        this.commit()
            
    def saveData(this,tasks):
        """
        Saves, and updates tasks into the database, by checking existence and concurances.
        """
        originalData = []
        this.loadData(originalData)
        for newtask in tasks:
            if newtask.getId() == -1:
                this.saveNewTask(newtask)
                continue
            for oldtask in originalData:
                if newtask.getId() != oldtask.getId():
                    #they are not the same
                    continue
                if newtask.getName() != oldtask.getName():
                    #update name in db
                    this.setData(f"UPDATE Tasks SET name =\"{newtask.getName()}\" where id = {oldtask.getId()};")
                if newtask.getDescription() != oldtask.getDescription():
                    #update description in db
                    this.setData(f"UPDATE Tasks SET description =\"{newtask.getDescription()}\" where id = {oldtask.getId()};")
                if newtask.getDeadline() != oldtask.getDeadline():
                    #update deadline in db
                    this.setData(f"UPDATE Tasks SET deadline =\"{newtask.getDeadline()}\" where id = {oldtask.getId()};")
                if newtask.getPeriodicity() != oldtask.getId():
                    #update periodicity in db
                    this.setData(f"UPDATE Tasks SET periodicity =\"{newtask.getPeriodicity()}\" where id = {oldtask.getId()};")
                if newtask.getHistory() != oldtask.getHistory():
                    difference = [history for history in newtask.getHistory() if history not in oldtask.getHistory()]
                    for history in difference:
                        this.setData(f"INSERT INTO History VALUES ({history[0]},{history[1]},{history[2]},{history[3]})")
        
        this.commit()
                
        
    
if(__name__ == "__main__"): #Used for unit testing the DBManager.py
    DBManager()
    data = []
    manager.loadData(data)
    print(data)
    print("Write sql query to start:")
    print(manager.getData(input()))
