# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 16:11:29 2022

@author: Utilizador
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Dec 10 20:25:14 2022

@author: queir
"""
#%%
import numpy as np
import random



#%%
class Model():
    R: int = 20  # the Reward payoff (Both Countries apply low import tariffs)
    P: int = 1  # the Punishment payoff (Both countries apply tariffs to imports)
    S: int = 0  # the Sucker/Loss payoff (Country allow imports but face other countries import bareers)
    T: int = 21  # the Temptation payoff (Country applies customs bareers, but can freely export)
    
    # Simulation modes
    CRISIS: str="Crisis"
    GLOBALIZATION: str="Globalization"
    
    #Blocks 
    BLOCK_A: str = "Western"
    BLOCK_B: str = "Eastern"
    BLOCK_C: str = "Non-Aligned"

    # The probability that a random event changes a year's decision
    ERROR_MARGIN: int = 5 
    
    #Impact of current GDP in the wealth Variation after each period of trade.
    #It is a devider, so the higher the value the lower the growth.
    DIV_SELF_WEALTH: int=2900 # original 7800
  
    
    ##Other parameters to adjust the model
    
    #Recent Capitalism
    RECENT_CAPITALISM : float = 2.8
    
    #Positive GDP Growth effect that some countries experience in particular epochs
    MIRACLE_EFFECT : float = 2.6 # 1.7
    #Positive GDP Growth Anomaly in countries with large population 
    LARGE_POPULATION_EFFECT: float = 1.8 # 1.2
    #Negative GDP Growth Anomaly in countries with either very High or Very Low demographic growth
    DEMOG_GROWTH_ANOMALLY_EFFECT: float = 1.5 # 1.2
    
    COOPERATE, DEFECT = 0, 1
    St_names = ["C", "D"]

    @staticmethod
    def applyRandomness(decisions, countries):
        "returns a new decisions tuple after applying randomness effect"
        st = list(decisions)
        
        for i in range(len(decisions)):
            # Changes the decision if random number is smaller than the Error Margin
            if random.uniform(0, 100) < Model.ERROR_MARGIN : 
                print(f"Reverse decision by {countries[i]}.")
                st[i] = abs(st[i] - 1)
        
        return tuple(st)
    
    # Decides payoff of the strategy in each clash for each country
    @staticmethod
    def score(decisions):
        "returns a score tuple based on the decisions."
        for ii in enumerate(decisions) :
            
            # in case decision is to cooperate
            if decisions[0] == Model.COOPERATE:
                return (Model.R, Model.R) if decisions[1] == Model.COOPERATE else (Model.S, Model.T)
            # in case decision is to defect
            else:
                return (Model.T, Model.S) if decisions[1] == Model.COOPERATE else (Model.P, Model.P)
      
        
    #informs the used strategies in this battle
    @staticmethod
    def strategies_names(decisions):
        "returns an array with decision of bothe countries in the present clash"
        return [Model.St_names[st] for st in decisions]

#%%
class Strategy():
    #def __init__(self):
    def decision(self, _=None):
        "Strategy: Always cooperate"
        return Model.COOPERATE    
        

class Strategy_Random(Strategy):
    
    def decision(self, _=None):
        "Strategy: Random play"
        return np.random.default_rng().integers(2)
            
class Strategy_Defector(Strategy):
    def decision(self_, _=None):
        "Strategy: Always defect (Judas)"
        return Model.DEFECT
        
class Strategy_Jesus(Strategy):
    pass


class Strategy_CopyCat(Strategy):
    def decision(self, other):
        "Strategy: Copy Cat"
        return other.history[-1] if len(other.history) else Model.COOPERATE

class Strategy_CopyKitten(Strategy):
    def decision(self, other):
        "Strategy: Copy Kitten"
        if len(other.history)>1 : 
            last = other.history[-2:]
            return Model.DEFECT if last[0] == last[1] == 1 else Model.COOPERATE
        
        return Model.COOPERATE


#%%
class Country():
    def __init__(self, name="Wonderland", wealth=1000, strategy=Strategy_Jesus(),block=Model.BLOCK_C,
                 demographicGrowthAnomaly=False, largePopulation=False, recentCapitalism=False):
        
        self.name = name
        self.strategy = strategy
        self.block = block
        self.history = []
        
        self.wealth = wealth
        self.initialWealth = wealth
        self.currentRoundWealth=0
        
        self.demographicGrowthAnomaly = demographicGrowthAnomaly
        self.largePopulation = largePopulation
        self.recentCapitalism = recentCapitalism
        
  
    
    def finishBiLateralTrading(self):
        "Clears the history of last round, adds the current round Wealth to the wealth and reinitates the currentRoundWealth"
        self.history = []
        self.wealth+=self.currentRoundWealth
        self.currentRoundWealth = 0
        
        
    
    def updateWealth(self, score):
        "Caclulates and updates the country wealth based on the score and model parameters."
        
        # Considering the Demographic Anomaly Growth DIVIDER efect ()
        div = Model.DIV_SELF_WEALTH * Model.DEMOG_GROWTH_ANOMALLY_EFFECT if self.demographicGrowthAnomaly else Model.DIV_SELF_WEALTH
        
        # Considering the Large Population MULTIPLIER efect
        div = div / Model.LARGE_POPULATION_EFFECT if self.largePopulation else div
        
        # Considering the "miracle" MULTIPLIER efect
        div = div / Model.RECENT_CAPITALISM if self.recentCapitalism else div
    
        #Defining the wealth multiplier    
        whealthMultiplier = (self.initialWealth + self.currentRoundWealth) / div
                
        #Updates current round welath
        self.currentRoundWealth += score*whealthMultiplier
        
    def decision(self, other):
          "Return decision 0 - Cooperate or 1 - Defect, based on country's strategy"
             
          return self.strategy.decision(other) 
    
    def decisionCrisis(self, otherCountry):
         "Return decision 1 - Deffect if countries are from opposite blocks, or the standar decision if not."
              
         if (self.block==Model.BLOCK_A) & (otherCountry.block==Model.BLOCK_B):
            return Model.DEFECT
        
         if (self.block==Model.BLOCK_B) & (otherCountry.block==Model.BLOCK_A):
            return Model.DEFECT
        
         return self.decision(otherCountry)
    
    

#%%
def BiLateralTrading(country_1, country_2, numberOfYears, mode):
    "Runs a trading simulation between two countries, over a given number of years."
    
    #Initiate the scores
    #scores = [0, 0]
    
    
    print(f"\nBiLateralTrading between {country_1.name} and {country_2.name} during {numberOfYears} years.")
    
    for ii in range(numberOfYears):
        
        # Depending on the BiLateralTrading mode it calculates decision based on standard strategies or Crisis strategies
        if (mode==Model.GLOBALIZATION) :
            baseDecision= country_1.decision(country_2), country_2.decision(country_1)
        else:
            baseDecision=country_1.decisionCrisis(country_2), country_2.decisionCrisis(country_1)
        
        # Applys randomness
        decisions = Model.applyRandomness(
            baseDecision,(country_1.name,country_2.name))
        
        # Calculate the score based on the countries' decisions clash
        score = Model.score(decisions)
        
                
        print (f"Strategies: {Model.strategies_names(decisions)}")
        for ii, country in enumerate((country_1, country_2)):
            country.history.append(decisions[ii])
            #scores[ii] += score[ii]
            country.updateWealth(score[ii])
        print (f"\tRound score:  {score}")
        #print (f"\tGlobal score: {scores}")
        
    
    print("\n")
    for country in (country_1, country_2):
        country.finishBiLateralTrading()
        print (f"{country.name} wealth is now: {round(country.wealth)} Billion dollars")
        
    
       

#%% World Leage

def WorldCommerce(yearStart, yearEnd, mode):
    numberOfYears = yearEnd-yearStart
    
    # importing the countries for the simulation
    countries = (getCountries1980() if yearStart == 1980 else getCountries2020())
    
   
    # Running the simulation
    print("\n# World Commerce Simulation has started #")
    for selfCountry in countries:
        for otherCountry in countries:
            if (selfCountry.name != otherCountry.name):
                BiLateralTrading(selfCountry, otherCountry, numberOfYears, mode)
   
    #Displaying final output of the simulation
    globalInitialWealth=0
    globalFinalWealth=0
    avgGrowth=0
    print(f"\n## Final Wealth - From {yearStart} to {yearEnd}. Environment: {mode}. ##\n\n")
    print("{0:15} | GDP {1:12} | GDP {2:12} | Variation".format("Country name", yearStart, yearEnd))
    print("-----------------------------------------------------------------")
    
    for country in countries:
        #print("cname: {0:50} started with \t${round(country.oldWealth)} and finished with \t${round(country.wealth)}.".format(country.name)
        globalInitialWealth += country.initialWealth
        globalFinalWealth += country.wealth
        countryVar=round((country.wealth/country.initialWealth - 1)  * 100)
        avgGrowth+= countryVar
        
        print("{0:15} | {1:9} Bi USD | {2:9} Bi USD | {3}%".format(country.name, country.initialWealth, round(country.wealth), countryVar))
        
        #print("{0:15} started with {1:5} Bi USD and finished with {2:5} Bi Usd. Variation: {3}%".format(country.name, country.oldWealth, round(country.wealth), countryVar))
    
    variationWealthRel= (globalFinalWealth/globalInitialWealth - 1) * 100
    print("-----------------------------------------------------------------")
    print ("{0:15} | {1:9} Bi USD | {2:9} Bi USD | {3}%".format("World", globalInitialWealth, round(globalFinalWealth), round(variationWealthRel)))
    avgGrowth = avgGrowth/len(countries)
    print (f"\nThe Average growth was: {round(avgGrowth)}%.")
    
   
 #%%   
def getCountries1980(): 
    return [
        Country(name="Australia", wealth=399, strategy=Strategy_CopyKitten(), block=Model.BLOCK_A),
        Country(name="Canada", wealth=276, strategy=Strategy_CopyKitten(),block=Model.BLOCK_A),
        Country(name="United States", wealth=2857, strategy=Strategy_CopyKitten(), block=Model.BLOCK_A),
        Country(name="China", wealth=304, strategy=Strategy_CopyKitten(), block=Model.BLOCK_B, largePopulation=True, recentCapitalism=True),
        Country(name="North Korea", wealth=10, strategy=Strategy_Defector(), block=Model.BLOCK_B),
        Country(name="European Union", wealth=3716,strategy=Strategy_CopyKitten(), block=Model.BLOCK_A,demographicGrowthAnomaly=True),
        Country(name="Africa", wealth=90,strategy=Strategy_Random(), demographicGrowthAnomaly=True),
        Country(name="South America", wealth=611,strategy=Strategy_Random()),
        Country(name="India", wealth=253,strategy=Strategy_CopyCat(), block=Model.BLOCK_B, largePopulation=True),
        Country(name="Middle-east", wealth=554,strategy=Strategy_Random()),
        Country(name="Japan", wealth=1127,strategy=Strategy_CopyKitten(), block=Model.BLOCK_A, demographicGrowthAnomaly=True),
        Country(name="Switzerland", wealth=122,strategy=Strategy_CopyKitten()),
        Country(name="Central America", wealth=10,strategy=Strategy_Random()),
        Country(name="Ex-USSR", wealth=33,strategy=Strategy_CopyCat(), block=Model.BLOCK_B, recentCapitalism=(True)),
        
        ]
   
#%%   
def getCountries2020(): 
    return [
        Country(name="Australia", wealth=2699, strategy=Strategy_CopyKitten(), block=Model.BLOCK_A),
        Country(name="Canada", wealth=1645, strategy=Strategy_CopyKitten(),block=Model.BLOCK_A),
        Country(name="United States", wealth=21060, strategy=Strategy_CopyKitten(), block=Model.BLOCK_A),
        Country(name="China", wealth=14944, strategy=Strategy_CopyKitten(), block=Model.BLOCK_B, largePopulation=True),
        Country(name="North Korea", wealth=17, strategy=Strategy_Defector(), block=Model.BLOCK_B),
        Country(name="European Union", wealth=17932,strategy=Strategy_CopyKitten(), block=Model.BLOCK_A,demographicGrowthAnomaly=True),
        Country(name="Africa", wealth=183,strategy=Strategy_Random(), demographicGrowthAnomaly=True),
        Country(name="South America", wealth=3540,strategy=Strategy_Random()),
        Country(name="India", wealth=3029,strategy=Strategy_CopyCat(), block=Model.BLOCK_B, largePopulation=True),
        Country(name="Middle-east", wealth=4709,strategy=Strategy_Random()),
        Country(name="Japan", wealth=5031,strategy=Strategy_CopyKitten(), block=Model.BLOCK_A, demographicGrowthAnomaly=True),
        Country(name="Switzerland", wealth=739,strategy=Strategy_CopyKitten(), block=Model.BLOCK_A),
        Country(name="Central America", wealth=52,strategy=Strategy_Random()),
        Country(name="Ex-USSR", wealth=800,strategy=Strategy_CopyCat(), block=Model.BLOCK_B),
        ]
        


#%% 
WorldCommerce(1980,2020,Model.GLOBALIZATION)    

#%% 
WorldCommerce(2020,2040,Model.GLOBALIZATION)    

#%% 
WorldCommerce(2020,2040,Model.CRISIS)    
                                   









   