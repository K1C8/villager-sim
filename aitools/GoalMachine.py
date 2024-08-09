"""
CS5150 Game AI Final Project
Team Member: Jianyan Chen, Ruidi Huang, Xin Qi
Aug 2024

This is an UNUSED file from the original repo.

This program implements a simple goal-oriented action planning (GOAP) system for AI.
The GoalMachine class allows you to define general goals for the AI to accomplish 
and specific actions that the AI can carry out. The AI then determines which actions 
make the most sense to achieve its goals.
"""

class GoalMachine(object):
    """
    Another method for AI, this way you can set general goals for the AI
    to accomplish and specific actions it can carry out, and the AI will
    determine which actions would make the most sense.
    """

    def __init__(self):
        self.discontentment = 0
        self.max_goal_discontentment = 10
        self.goals = {}
        self.actions = []

    def add_goal(self, goal):
        """
        Adds a goal to the GoalMachine.

        Args:
            goal (Goal): The goal to be added.
        """
        self.goals[goal.name] = goal

    def add_action(self, action):
        """
        Adds an action to the GoalMachine.

        Args:
            action (Action): The action to be added.
        """
        self.actions.append(action)
        
    def do_action(self, action):
        """
        Executes the given action, updating the necessity of the goals based on the action's effects.

        Args:
            action (Action): The action to be performed.
        """
        if action is not None:
            # Update goals based on the effects of the action
            for effect in action.effects:
                self.goals[effect].necessity += action.effects[effect]
                
            # Update all goals based on the passage of time
            for goal in self.goals:
                self.goals[goal].update(action.time)
        else:
            print("No action selected!")

    def do_reverse_action(self, action):
        """
        Reverses the effects of the given action. Useful for simulating actions without committing to them.

        Args:
            action (Action): The action whose effects should be reversed.
        """
        # Reverse the effects of the action on goals
        for effect in action.effects:
            self.goals[effect].necessity -= action.effects[effect]
            
        # Reverse the time update for all goals
        for goal in self.goals:
            self.goals[goal].reverse_update(action.time)
            
    def calculate_discontentment(self):
        """
        Calculates the total discontentment of the AI based on the current state of all goals.

        Returns:
            float: The total discontentment.
        """
        discontentment = 0
        for goal in self.goals:
            discontentment += (self.goals[goal].necessity * self.goals[goal].necessity)

        return discontentment
    
    def determine_best_action(self):
        """
        Goes through all the possible actions, and determines which would be the most effective
        Returns:
            Action: The action that results in the lowest discontentment.
        """
        
        # Initialize discontentment
        lowest_discontentment = (len(self.goals) * self.max_goal_discontentment) ** 2
        best_action = None
        current_discontentment = self.calculate_discontentment()
        
        for possible_action in self.actions:
            
            self.do_action(possible_action)
                
            new_possible_discontentment = self.calculate_discontentment()
            
            if new_possible_discontentment < lowest_discontentment: 
                # and new_possible_discontentment < current_discontentment:
                lowest_discontentment = new_possible_discontentment
                best_action = possible_action
                
            # Reverse the action to simulate the next one
            self.do_reverse_action(possible_action)
        
        """
        if best_action is not None:
            self.do_action(best_action)
        """ 
        return best_action

class Goal(object):
    """One thing the AI is trying to accomplish."""

    def __init__(self, name, time_delta=0):
        """necessity is how bad the goal should be accomplished, time_delta
            is how much it should change over time"""
        self.name = name
        self.necessity = 0
        self.time_delta = time_delta
        
    def set_necessity(self, value):
        """
        Sets the necessity value of the goal.

        Args:
            value (float): The new necessity value.
        """
        self.necessity = value

    def update(self, time_passed):
        """
        Updates the necessity of the goal based on the time passed.

        Args:
            time_passed (float): The amount of time passed since the last update.
        """
        self.necessity += self.time_delta * time_passed
        
    def reverse_update(self, time_passed):
        """
        Reverses the necessity change based on the time passed.

        Args:
            time_passed (float): The amount of time passed since the last update.
        """
        self.necessity -= self.time_delta * time_passed

class Action(object):
    """One thing the AI can do to work towards it's goals."""

    def __init__(self, name, effects, time=0):
        """'effects' will be a dictionary of pairs of goal strings with
            values of how they will affect them. For example:
            {"eat": -2} will decrease the value of the "eat" goal by 2. Time
            is how long the action will take (all relative)"""
            
        self.name = name
        self.effects = effects
        self.time = time
        
    def set_time(self, time):
        """
        Sets the time required to complete the action.

        Args:
            time (float): The new time value.
        """
        self.time = time

    def execute(self):
        """Overwritable"""
        pass

if __name__ == "__main__":
    gm = GoalMachine()
    
    goal1 = Goal("eat", .5)
    goal2 = Goal("bathroom", .5)
    
    goal1.set_necessity(2)
    goal2.set_necessity(2)

    action1 = Action("snack", {"eat":-1}, 0.25)
    action2 = Action("use_bathroom", {"eat":+2, "bathroom":-2}, 1)
    action3 = Action("do nothing", {}, .25)

    gm.add_goal(goal1)
    gm.add_goal(goal2)

    gm.add_action(action1)
    gm.add_action(action2)
    gm.add_action(action3)

    iterations = 10
    print("ITERATIONS: ", iterations)

    for i in range(iterations):
        print("\nCURRENT ITERATION:", i+1)

        for g in gm.goals:
            print(gm.goals[g].name, gm.goals[g].necessity)

        print("\nCurrent Discontentment:", gm.calculate_discontentment())
        best_action1 = gm.determine_best_action()
        print("Best Action would be:", best_action1.name)
        
        print("Applying Best Action:")
        gm.do_action(best_action1)
        
        print("New discontentment:", gm.calculate_discontentment(), "\n")

        for g in gm.goals:
            print(gm.goals[g].name, gm.goals[g].necessity)
