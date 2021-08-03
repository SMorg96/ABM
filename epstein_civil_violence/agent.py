import math

from mesa import Agent


class Citizen(Agent):
    
    #rebel or quiet
    #Summary of rule: If grievance - risk > threshold, rebel.
  

    def __init__(
        self,
        unique_id,
        model,
        pos,
        hardship, #Agent's 'perceived hardship (i.e., physical or economicprivation).'
        regime_legitimacy,
        food_scarcity,
        risk_aversion,
        threshold,
        vision,
        education_level,
    ):
       #create citizen
        super().__init__(unique_id, model)
        self.breed = "citizen"
        self.pos = pos
        self.hardship = hardship
        self.food_scarcity = food_scarcity
        self.regime_legitimacy = regime_legitimacy
        self.risk_aversion = risk_aversion
        self.threshold = threshold
        self.condition = "Quiescent" #deterministic function of greivanceand  perceived risk
        self.vision = vision
        self.jail_sentence = 0
        self.radicalized = False
        self.grievance = self.hardship * (1 - self.regime_legitimacy) #deterministic function of hardship and regime_legitimacy;
        self.attacks = 0
        self.arrest_probability = None
        self.education_level = self.random.randint(0, 3)
       

    def step(self):
        #activate?
        #move if neccesary 
       
        if self.jail_sentence:
            self.jail_sentence -= 1
            return  # no other changes or movements if agent is in jail.
        self.update_neighbors()
        self.update_estimated_arrest_probability()
        net_risk = self.risk_aversion * self.arrest_probability
        if (
            self.condition == "Quiescent"
            and (self.grievance - net_risk) > self.threshold
        ):
            self.condition = "Active"
        elif (
            self.condition == "Quiescent" and self.radicalized ==True
        ):
            self.condition = "Active"
            attack = self.random.randint(0, 10)
            if (
                attack == 9
            ):
                self.attacks = self.attacks +1
        elif (
            self.condition == "Active" and (self.grievance - net_risk) <= self.threshold
        ):
            self.condition = "Quiescent"
            
        if self.model.movement and self.empty_neighbors:
            new_pos = self.random.choice(self.empty_neighbors)
            self.model.grid.move_agent(self, new_pos)

    def update_neighbors(self):
        self.neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=False, radius=1
        )
        self.neighbors = self.model.grid.get_cell_list_contents(self.neighborhood)
        self.empty_neighbors = [
            c for c in self.neighborhood if self.model.grid.is_cell_empty(c)
        ]

    def update_estimated_arrest_probability(self):
     
        cops_in_vision = len([c for c in self.neighbors if c.breed == "cop"])
        actives_in_vision = 1.0  # citizen counts herself
        for c in self.neighbors:
            if (
                c.breed == "citizen"
                and c.condition == "Active"
                and c.jail_sentence == 0
            ):
                actives_in_vision += 1
        self.arrest_probability = 1 - math.exp(
            -1 * self.model.arrest_prob_constant * (cops_in_vision / actives_in_vision)
        )


class Cop(Agent):
    # Summary of rule: Inspect local vision and arrest a random active agent.
   

    def __init__(self, unique_id, model, pos, vision):
        #new Cop
    
        super().__init__(unique_id, model)
        self.breed = "cop"
        self.pos = pos
        self.vision = vision
        

    def step(self):
        
        #check neighbors and arrest a random active agent.
        self.update_neighbors()
        active_neighbors = []
        for agent in self.neighbors:
            if (
                agent.breed == "citizen"
                and agent.condition == "Active"
                and agent.jail_sentence == 0
            ):
                active_neighbors.append(agent)
        if active_neighbors:
            arrestee = self.random.choice(active_neighbors)
            sentence = self.random.randint(0, self.model.max_jail_term)
            arrestee.jail_sentence = sentence
        if self.model.movement and self.empty_neighbors:
            new_pos = self.random.choice(self.empty_neighbors)
            self.model.grid.move_agent(self, new_pos)

    def update_neighbors(self):
        self.neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=False, radius=1
        )
        self.neighbors = self.model.grid.get_cell_list_contents(self.neighborhood)
        self.empty_neighbors = [
            c for c in self.neighborhood if self.model.grid.is_cell_empty(c)
        ]
class Radicalizer(Agent):
    # Summary of rule: Inspect local vision and arrest a random active agent.
   

    def __init__(self, unique_id, model, pos, vision,food_scarcity):
        #new Cop
    
        super().__init__(unique_id, model)
        self.breed = "radicalizer"
        self.pos = pos
        self.vision = vision
        self.food_scarcity = food_scarcity
        self.motivation = (1 - self.food_scarcity)

    def step(self):
        
        #check neighbors and arrest a random active agent.
        self.update_neighbors()
        active_neighbors = []
        for agent in self.neighbors:
            if (
                agent.breed == "citizen"
                and agent.condition == "Quiescent"
                and agent.education_level == 3
                and self.motivation < .6
            ):
                active_neighbors.append(agent)
        if active_neighbors:
            converted = self.random.choice(active_neighbors)
           
            converted.radicalized = True
        if self.model.movement and self.empty_neighbors:
            new_pos = self.random.choice(self.empty_neighbors)
            self.model.grid.move_agent(self, new_pos)

    def update_neighbors(self):
        self.neighborhood = self.model.grid.get_neighborhood(
            self.pos, moore=False, radius=1
        )
        self.neighbors = self.model.grid.get_cell_list_contents(self.neighborhood)
        self.empty_neighbors = [
            c for c in self.neighborhood if self.model.grid.is_cell_empty(c)
        ]
    

