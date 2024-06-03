def computeHistoryCount(history):
    """
    Inputs history list of a Task, in the form of [id, success, deadline,date]
    Returns lenght of the history list.
    """
    return len(history)
    
def computeCompleted(history):
    """
    Inputs history list of a Task, in the form of [id, success, deadline,date]
    Returns the amount of completed history in the history list.
    """
    return len([i for i in history if i[1] == 1])

def computeMissed(history):
    """
    Inputs history list of a Task, in the form of [id, success, deadline,date]
    Returns the amount of missed history in the history list.
    """
    return len([i for i in history if i[1] == 0])
    
def computeCompletedStreak(history_):
    """
    Inputs history_ list of a Task, in the form of [id, success, deadline,date]
    Returns the largest streak of successed tasks in the history.
    """
    streak = 0
    highestStreak = 0
    for history in history_:
        if history[1] == 1:
            streak +=1
        else:
            streak = 0
        if streak > highestStreak:
            highestStreak = streak
    
    return highestStreak

def computeMissedStreak(history_):
    """
    Inputs history_ list of a Task, in the form of [id, success, deadline,date]
    Returns the largest streak of missed tasks in the history.
    """
    streak = 0
    highestStreak = 0
    for history in history_:
        if history[1] == 0:
            streak +=1
        else:
            streak = 0
        if streak > highestStreak:
            highestStreak = streak
    
    return highestStreak

def computeSuccessRate(history):
    """
    Inputs history list of a Task, in the form of [id, success, deadline,date]
    Returns a float representing the success rate of the history. On a scale of 0-100
    """
    all = computeHistoryCount(history)
    success = computeCompleted(history)
    if all == 0:
        return 0
    else:
        return success/all*100

def computeMissedRate(history):
    """
    Inputs history list of a Task, in the form of [id, success, deadline,date]
    Returns a float representing the missed rate of the history. On a scale of 0-100
    """
    all = computeHistoryCount(history)
    missed = computeMissed(history)
    if all == 0:
        return 0
    else:
        return missed/all*100