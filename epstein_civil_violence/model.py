from mesa import Model
from mesa.time import RandomActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector

from .agent import Cop, Citizen, Radicalizer


class EpsteinCivilViolence(Model):
    #Model source:
    #http://www.pnas.org/content/99/suppl_3/7243.full
  
  

    def __init__(
        self,
        height=40,
        width=40,
        citizen_density=0.7,
        cop_density=0.054,
        radicalizer_density=0.02,
        citizen_vision=7,
        cop_vision=7,
        legitimacy=0.8,
        food_scarcity = .45
        max_jail_term=1000,
        active_threshold=0.1,
        arrest_prob_constant=2.3,
        movement=True,
        max_iters=1000,
    ):
        super().__init__()
        self.height = height
        self.width = width
        self.citizen_density = citizen_density
        self.cop_density = cop_density
        self.radicalizer_density = radicalizer_density 
        self.citizen_vision = citizen_vision
        self.cop_vision = cop_vision
        self.legitimacy = legitimacy
        self.max_jail_term = max_jail_term
        self.active_threshold = active_threshold
        self.arrest_prob_constant = arrest_prob_constant
        self.movement = movement
        self.food_scarcity=food_scarcity
        self.max_iters = max_iters
        self.iteration = 0
        self.schedule = RandomActivation(self)
        self.grid = Grid(height, width, torus=True)
        model_reporters = {
            "Quiescent": lambda m: self.count_type_citizens(m, "Quiescent"),
            "Active": lambda m: self.count_type_citizens(m, "Active"),
            "Jailed": lambda m: self.count_jailed(m),
            "Radicals": lambda m: self.count_radical(m),
            "Terrorist Attacks": lambda m: self.count_attacks(m),
        }
        agent_reporters = {
            "x": lambda a: a.pos[0],
            "y": lambda a: a.pos[1],
            "breed": lambda a: a.breed,
            "jail_sentence": lambda a: getattr(a, "jail_sentence", None),
            "condition": lambda a: getattr(a, "condition", None),
            "arrest_probability": lambda a: getattr(a, "arrest_probability", None),
            
        }
        self.datacollector = DataCollector(
            model_reporters=model_reporters, agent_reporters=agent_reporters
        )
        unique_id = 0
        if self.cop_density + self.citizen_density+ self.radicalizer_density > 1:
            raise ValueError("Cop density + citizen density must be less than 1")
        for (contents, x, y) in self.grid.coord_iter():
            if self.random.random() < self.cop_density and self.random.random()> self.radicalizer_density :
                cop = Cop(unique_id, self, (x, y), vision=self.cop_vision)
                unique_id += 1
                self.grid[y][x] = cop
                self.schedule.add(cop)
            elif self.random.random() < self.radicalizer_density:
                rad = Radicalizer(unique_id, self, (x, y), vision=self.cop_vision,food_scarcity=self.food_scarcity)
                unique_id += 1
                self.grid[y][x] = rad
                self.schedule.add(rad)
            elif self.random.random() < (self.cop_density + self.citizen_density+self.radicalizer_density):
                citizen = Citizen(
                    unique_id,
                    self,
                    (x, y),
                    hardship=self.random.random(),
                    regime_legitimacy=self.legitimacy,
                    risk_aversion=self.random.random(),
                    threshold=self.active_threshold,
                    vision=self.citizen_vision,
                )
                unique_id += 1
                self.grid[y][x] = citizen
                self.schedule.add(citizen)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)
        self.iteration += 1
        if self.iteration > self.max_iters:
            self.running = False

    @staticmethod
    def count_type_citizens(model, condition, exclude_jailed=True):
        #count Quiescent && Active.
        count = 0
        for agent in model.schedule.agents:
            if agent.breed == "cop":
                continue
            if agent.breed == "radicalizer":
                continue
            if exclude_jailed and agent.jail_sentence:
                continue
            if agent.condition == condition:
                count += 1
        return count
    
    @staticmethod
    def count_radical(model):
        #count Quiescent && Active.
        count = 0
        for agent in model.schedule.agents:
            if agent.breed == "citizen" and agent.radicalized:
                count += 1
        return count

    @staticmethod
    def count_jailed(model):
       # count jailed 
       
        count = 0
        for agent in model.schedule.agents:
            if agent.breed == "citizen" and agent.jail_sentence:
                count += 1
        return count
    
    @staticmethod
    def count_attacks(model):
       # count jailed 
       
        count = 0
        for agent in model.schedule.agents:
            if agent.breed == "citizen"
                count = count + agent.attacks
        return count
