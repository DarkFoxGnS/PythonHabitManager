import unittest,math

def LoadDatabaseTest():
    import DBManager
    DBManager.DBManager()
    manager = DBManager.DBManager.getManager()
    data = []
    manager.loadData(data)
    for item in data:
        print(item)

def CustomQuaryDB():
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
    def test_task_initialization(self):
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

class TestAnalytics(unittest.TestCase): 
    def test_analytics(self):
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

def AssertTask():
    import Task
    unittest.assertEqual(1,1)

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

    
