import unittest,math

def LoadDatabaseTest():
    """
    Load data from test, print it to the screen.
    """
    import DBManager
    DBManager.DBManager()
    manager = DBManager.DBManager.getManager()
    data = []
    manager.loadData(data)
    for item in data:
        print(item)

def CustomQuaryDB():
    """
    Allows the user to write custom query and execute it on the database.
    """
    import DBManager
    DBManager.DBManager()
    manager = DBManager.DBManager.getManager()
    while True:
        print("Type Exit to exit and Back to return to the previous menu.")
        print("Enter SQL query to execute it on the database:")
        command = input()
        match command.casefold():
            case "exit":
                exit()
            case "back":
                return
            case _:
                response = manager.getData(command)
                for data in response:
                    print(data)

class TestTask(unittest.TestCase):
    """
    Test regarding to the Task object.
    """
    def test_task_initialization(self):
        """
        Test task creation with predefined data.
        """
        import Task
        testingData = [
        [0,"Name","Description",0,0],
        ["0","Name","Description",0,0],
        [0,1,"Description",0,0],
        [0,"Name",1,0,0],
        [0,"Name","Description","0",0],
        [0,"Name","Description",0,"0"],
        ["0",1,2,"0","0"]
        ]
        
        for item in testingData:
            task = Task.Task(item)
            self.assertIsNotNone(task)
            self.assertEqual(task.getId(),int(item[0]))
            self.assertEqual(task.getName(),str(item[1]))
            self.assertEqual(task.getDescription(),str(item[2]))
            self.assertEqual(task.getDeadline(),int(item[3]))
            self.assertEqual(task.getPeriodicity(),int(item[4]))         
    
    def test_task_setters(self):
        """
        Test setters and getters with predefined data.
        """
        import Task
        testingData = [
        [1,"2","3",4,5],
        ["1","2","3",4,5],
        [1,2,"3",4,5],
        [1,"2",3,4,5],
        [1,"2","3","4",5],
        [1,"2","3",4,"5"],
        ["1",2,3,"4","5"]
        ]
        
        for item in testingData:
            task = Task.Task([0,0,0,0,0])
            self.assertIsNotNone(task)
            
            task.setId(item[0])
            task.setName(item[1])
            task.setDescription(item[2])
            task.setDeadline(item[3])
            task.setPeriodicity(item[4])
            
            self.assertEqual(task.getId(),int(item[0]))
            self.assertEqual(task.getName(),str(item[1]))
            self.assertEqual(task.getDescription(),str(item[2]))
            self.assertEqual(task.getDeadline(),int(item[3]))
            self.assertEqual(task.getPeriodicity(),int(item[4])) 
    
    def test_task_random_data(self):
        """
        Test Task creation and setters with random data.
        """
        import Task, random
        for i in range(100):
            #create random data
            id = i
            name = str(random.random()*i)
            description = str(random.random()*i)
            deadline = random.randint(0,(i+1)*100)
            periodicity = random.randint(0,(i+1)*100)
            
            #create task
            task = Task.Task([id,name,description,deadline,periodicity])
            
            #asser task
            self.assertEqual(task.getId(),id)
            self.assertEqual(task.getName(),name)
            self.assertEqual(task.getDescription(),description)
            self.assertEqual(task.getDeadline(),deadline)
            self.assertEqual(task.getPeriodicity(),periodicity) 
            
            #create new random data
            id += random.randint(0,(i+1)*100)
            name += str(random.random()*i)
            description += str(random.random()*i)
            deadline += random.randint(0,(i+1)*100)
            periodicity += random.randint(0,(i+1)*100)
            
            #set random data to task
            task.setId(id)
            task.setName(name)
            task.setDescription(description)
            task.setDeadline(deadline)
            task.setPeriodicity(periodicity)
            
            #assert task
            self.assertEqual(task.getId(),id)
            self.assertEqual(task.getName(),name)
            self.assertEqual(task.getDescription(),description)
            self.assertEqual(task.getDeadline(),deadline)
            self.assertEqual(task.getPeriodicity(),periodicity) 
            
        
class TestAnalytics(unittest.TestCase): 
    """
    Tests regarding the Analytics module.
    """
    def test_analytics(self):
        """
        Test with predefined data.
        """
        import Analytics
        
        testData = [
        [0,0,0,0],
        [0,1,0,0],
        [0,0,0,0],
        [0,1,0,0],
        [0,0,0,0]
        ]
        
        self.assertEqual(Analytics.computeHistoryCount(testData),5)
        self.assertEqual(Analytics.computeCompleted(testData),2)
        self.assertEqual(Analytics.computeMissed(testData),3)
        self.assertEqual(Analytics.computeCompletedStreak(testData),1)
        self.assertEqual(Analytics.computeMissedStreak(testData),1)
        self.assertEqual(Analytics.computeSuccessRate(testData),2/5*100)
        self.assertEqual(Analytics.computeMissedRate(testData),3/5*100)

    def test_random_data(self):
        """
        Test with a month of randomized data.
        """
        import Analytics,random
        
        #run test 100 times to ensure constant success rate.
        for j in range(100):
            testData = []
        
            completed = 0
            failed = 0
            completedStreak = 0
            failedStreak = 0
            currentFailedStreak = 0
            currentCompletedStreak = 0
            allHistory = 0
            #test 1-6 whole month of random data, during evaluation the last two element of the history element can be ignored.
            for i in range(31*random.randint(1,6)):
                isCompleted = random.random()>0.5
                
                if isCompleted:
                    completed += 1
                    currentCompletedStreak += 1
                    currentFailedStreak = 0
                else:
                    failed += 1
                    currentFailedStreak += 1
                    currentCompletedStreak = 0
                
                if currentCompletedStreak > completedStreak:
                    completedStreak = currentCompletedStreak
                
                if currentFailedStreak > failedStreak:
                    failedStreak = currentFailedStreak
                
                testData.append([i,isCompleted,0,0])
                allHistory += 1
            
            self.assertEqual(Analytics.computeHistoryCount(testData),allHistory)
            self.assertEqual(Analytics.computeCompleted(testData),completed)
            self.assertEqual(Analytics.computeMissed(testData),failed)
            self.assertEqual(Analytics.computeCompletedStreak(testData),completedStreak)
            self.assertEqual(Analytics.computeMissedStreak(testData),failedStreak)
            self.assertEqual(Analytics.computeSuccessRate(testData),completed/allHistory*100)
            self.assertEqual(Analytics.computeMissedRate(testData),failed/allHistory*100)
        

#Only executes if the file is started. If the file is launched as a module, the it's ignored.
if __name__ == '__main__':
    while True:
        print("Select a option to start the testing:")
        print("1 Load Database, and display tasks.")
        print("2 SQL query in Database")
        print("3 Execute Unittests")
        option = input()
        
        print("\r\n")
        
        match option:
            case "1":
                LoadDatabaseTest()
            case "2":
                CustomQuaryDB()
            case "3":
                unittest.main()
            case _:
                print("Input not valid, please try again.\r\n\r\n")
                
        print("\r\n")

    
