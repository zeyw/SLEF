"""
Network package
Copyright (c) 2013 Federico Cerutti <federico.cerutti@acm.org>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

DESCRIPTION:

Package encompassing the classes for defining a trust network and 
saving it into the database
"""

from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from baseSQL import Base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from subjective_logic.Opinion import Opinion
import subjective_logic.Opinion
import subjective_logic.operators
from mpmath import mpf
import mpmath
from beta_distribution.History import History
import sys

## Table in the database for the many-to-many relationship between agents 
#  for describing when they are linked (neighbours)
links = Table("links", Base.metadata,
    Column("start", Integer, ForeignKey("agents.id"), primary_key=True),
    Column("end", Integer, ForeignKey("agents.id"), primary_key=True)
)

## Table in the database for the many-to-many relationship between a list of networks
#  and networks 
association_list_networks = Table("ass_listnetworks_networks", Base.metadata,
                                  Column('left_id', Integer, ForeignKey('listnetworks.id')),
                                  Column('right_id', Integer, ForeignKey('networks.id'))
)

## If you want to question about 'omega', you should ask this variable
question_omega = 'omega'

## If you want to question about the neighbours of an agent, you should ask this variable
question_everything = 'everything'

## The shared knowledege about omega
omega_value = True

## Default value for bootstrapping
default_time = 1000

## Use this variable if you want to have a 'dummy' consensus operator that forbids to use any
#  kind of consensus operators 
consensus_type_none = 'none_consensus'

## Variable identifying the Josang discount operator
discount_type_josang = 'josang'

## Variable identifying the Aberdeen discount operator
discount_type_aberdeen = 'aberdeen'
discount_type_aberdeen2 = 'aberdeen2'
discount_type_aberdeen3 = 'aberdeen3'

## Variable identifying the UAI2013 Referee discount operator
discount_type_uai = 'uai2013'

## Variable identifying the Josang discount operator
consensus_type_josang = 'josang_consensus'

## Variable identifying the Aberdeen consensus operator
consensus_type_aberdeen = 'aberdeen_consensus'


class ListNetworks(Base):
    """
    Data structure for encompassing a bunch of networks
    """
    __tablename__ = 'listnetworks'
    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    networks = relationship("AgentNetwork",
                            secondary=association_list_networks)
    
    def __init__(self, name):
        self.name = name
        
    def add_network(self, network):
        if isinstance(network, AgentNetwork):
            self.networks.append(network)
    
    def get_networks(self):
        return self.networks

class AgentNetwork(Base):
    """
    Data structure for a single network of agents.
    """
    __tablename__ = 'networks'
    id = Column(Integer, primary_key=True)
    name = Column(String(500))
    agents = relationship("Agent")
    
    def __init__(self, _name="original"):
        self.name = _name;

    
    def add_agent(self, x):
        if isinstance(x, Agent):
            self.agents.append(x)
            
    def get_agent_by_name(self, name):
        """
        @param name: name of the agent you are searching for
        @return the first found instance of Agent classes that has the name specified as parameter 
        """
        for ag in self.agents:
            if ag.name == name:
                return ag
            
    def get_agents(self):
        """
        @return a list containing all the agents in the network
        """
        return self.agents
            
    def clone(self, cloned):
        """
        @param cloned: OUT parameter
        
        This method requires as input an instance of AgentNetwork which will become an exact copy (not reference)
        of the current network.
        
        The reason why cloned cannot be created here and returned is related to the library used for saving these
        objects in the database that requires that the new object is referenced in the database before to fill in
        and in this package there is not direct access to the database session object. 
        """
        for ag in self.agents:
            cloned.add_agent(Agent(ag.name, eval(ag.probability)))
            
        for ag in self.agents:
            newag = cloned.get_agent_by_name(ag.name)
            for neigh in ag.neighbours:
                newag.addNeighbour(cloned.get_agent_by_name(neigh.name))
            
            for trust in ag.trusts:
                newag.trusts.append(TrustworthinessBetweenTwo(cloned.get_agent_by_name(trust.trustee.name),
                                                    trust.get_first_opinion(),
                                                    trust.get_second_opinion()))
            


class TrustworthinessBetweenTwo(Base):
    """
    Class representing the trustworthiness relationship between two agents
    @var trustee: the agent that should be trusted
    @var first_belief: the belief of the subjective logic opinion representing the trustworthiness degree of the trustee (first case)
    @var first_disbelief: the disbelief of the subjective logic opinion representing the trustworthiness degree of the trustee (first case)
    @var first_uncertainty: the uncertainty of the subjective logic opinion representing the trustworthiness degree of the trustee (first case)
    @var first_base: the base of the subjective logic opinion representing the trustworthiness degree of the trustee  (first case)
    @var second_belief: the belief of the subjective logic opinion representing the trustworthiness degree of the trustee (second case)
    @var second_disbelief: the disbelief of the subjective logic opinion representing the trustworthiness degree of the trustee (second case)
    @var second_uncertainty: the uncertainty of the subjective logic opinion representing the trustworthiness degree of the trustee (second case)
    @var second_base: the base of the subjective logic opinion representing the trustworthiness degree of the trustee  (second case)
    """
    __tablename__ = 'trustsbetweentwo'
      
    trustor_id = Column(Integer, ForeignKey('agents.id'), primary_key=True)
    trustee_id = Column(Integer, ForeignKey('agents.id'), primary_key=True)
    
    
    trustee = relationship("Agent",
                           primaryjoin="Agent.id==TrustworthinessBetweenTwo.trustee_id")

    first_belief = Column(String(500))
    first_disbelief = Column(String(500))
    first_uncertainty = Column(String(500))
    first_base = Column(String(500))
    
    second_belief = Column(String(500))
    second_disbelief = Column(String(500))
    second_uncertainty = Column(String(500))
    second_base = Column(String(500))

    def __init__(self, other, o1, o2=None):
        if isinstance(other, Agent) and isinstance(o1, Opinion):
            self.trustee = other
            self.first_belief = o1.getBelief().__repr__()
            self.first_disbelief = o1.getDisbelief().__repr__()
            self.first_uncertainty = o1.getUncertainty().__repr__()
            self.first_base = o1.getBase().__repr__()
            
            if o2 == None:
                o2 = o1
                
            if isinstance(o2, Opinion):
                self.second_belief = o2.getBelief().__repr__()
                self.second_disbelief = o2.getDisbelief().__repr__()
                self.second_uncertainty = o2.getUncertainty().__repr__()
                self.second_base = o2.getBase().__repr__()
                
        else:
            raise Exception("Agent and Two Opinion objects expected")
        
    def get_trustee(self):
        """
        @return: an instance of the class Agent representing the trustee in this trustworthiness relationship
        """
        return self.trustee
            
    def get_first_opinion(self):
        """
        @return: an instance of the subjective logic opinion representing the degree of trustworthiness of the trustee in the first case
        """
        return Opinion(eval(self.first_belief), eval(self.first_disbelief), eval(self.first_uncertainty), eval(self.first_base))
    
    def get_opinion(self):
        return self.get_first_opinion()

    def get_second_opinion(self):
        """
        @return: an instance of the subjective logic opinion representing the degree of trustworthiness of the trustee in the second case
        """
        return Opinion(eval(self.second_belief), eval(self.second_disbelief), eval(self.second_uncertainty), eval(self.second_base))


class InteractionHistory(Base):
    """
    Class saving the interaction with other agents
    @var agent_asked: the Agent which has been queried
    @var question: the question asked
    @var answer: the answer received
    """
    
    __tablename__ = 'interactionhistory'
    
    id = Column(Integer, primary_key = True)
    
    agent_asked_id = Column(Integer, ForeignKey('agents.id'))
    agent_asked = relationship("Agent",
                           primaryjoin="Agent.id==InteractionHistory.agent_asked_id")
    
    question = Column(String(500))
    answer = Column(String(50000))
    
    def __init__(self, ag_asked, quest, answ):
        if isinstance(ag_asked, Agent):
            self.agent_asked = ag_asked
            self.question = quest
            self.answer = answ
        else:
            raise Exception("Agent object expected")
    
    
class Agent(Base):
    """
    Class representing the data structure of an Agent
    @var probability: it is the probability that an agent will tell the _truth
    @var neighbours: the agents that this agent knows
    @var trusts: the list of trustworthiness degrees with other agents
    @var omega: each agent does not know that omega is a shared belief, so it will always refer to its own copy of the
                omega value
    @var interaction_history: the history of the interaction of this Agent with other agents 
    """
    __tablename__ = 'agents'

    id = Column(Integer, primary_key = True)
    network_id = Column(Integer, ForeignKey('networks.id'))
    name = Column(String(500))
    probability = Column(String(500))
    
    neighbours = relationship("Agent",
                        secondary=links,
                        primaryjoin=id==links.c.start,
                        secondaryjoin=id==links.c.end,
                        backref="back_neighbours"
    )
    
#     trusts = relationship("Trustworthiness",
#                           primaryjoin="Trustworthiness.trustor_id==Agent.id", 
#                           backref="trustor")
#      
    trusts = relationship("TrustworthinessBetweenTwo",
                          primaryjoin="TrustworthinessBetweenTwo.trustor_id==Agent.id", 
                          backref="trustor_between_two")
    
    omega = Column(Boolean)
    interaction_history = relationship("InteractionHistory")

    
    def __init__(self, _name, _probability):
        '''Parameters:
            _name: String
            _probability: String or a mpmath representing a number between 0 and 1
        '''
        self.name = _name
        self.probability = mpf(_probability).__repr__()
        self.omega = omega_value
    
    def __eq__(self, another):
        if isinstance(another, Agent):
            return self.name == another.name
        else:
            return NotImplemented

    def __ne__(self, another):
        result = self.__eq__(another)
        if result is NotImplemented:
            return result
        return not result
     
        
    def addNeighbour(self, neighbour):
        if (isinstance(neighbour, Agent)):
            self.neighbours.append(neighbour)
        else:
            raise Exception("Agent object expected")
        
        
    def _truth(self):
        if mpmath.rand() < eval(self.probability):
            return True
        else:
            return False
        
    def knowYourNeighbours(self, time=default_time):
        """
        Is the method for allowing the agent to bootstrap its opinions about the neighbours.
        
        ***CURRENTELY ONLY THE BETA REPUTATION SYSTEM BOOTSTRAPPING HAS BEEN IMPLEMENTED***
        """
        for ag in self.neighbours:
            positive = 0
            negative = 0
            for i in range(1,time):
                if self.query(ag, question_omega) == self.omega:
                    positive+=1
                else:
                    negative+=1
            self.trusts.append(TrustworthinessBetweenTwo(ag, History(positive, negative).to_Opinion()))
            
    def discount(self, ag_to_ask, ag_to_be_asked, discount_type = discount_type_josang):
        """
        @param ag_to_ask: agent that should be asked
        @param ag_to_be_asked: agent of which the opinion should be asked to ag_to_ask
        @param type: the type of discount to use (see the beginning of this package for seeing the alternatives)
        
        The result of the discounted opinion is added to the attribute "trust"
        """
        for t in self.trusts:
            if t.get_trustee() == ag_to_ask:
                if discount_type == discount_type_josang:
                    self.trusts.append(TrustworthinessBetweenTwo(ag_to_be_asked, 
                                            subjective_logic.operators.discount(t.get_opinion(), 
                                                     self._ask_about_another_agent(ag_to_ask, ag_to_be_asked))))
                elif discount_type == discount_type_aberdeen:
                    self.trusts.append(TrustworthinessBetweenTwo(ag_to_be_asked, 
                                            subjective_logic.operators.graphical_combination(t.get_opinion(), 
                                                     self._ask_about_another_agent(ag_to_ask, ag_to_be_asked))))
                elif discount_type == discount_type_aberdeen2:   
                    self.trusts.append(TrustworthinessBetweenTwo(ag_to_be_asked, 
                                            subjective_logic.operators.graphical_combination2(t.get_opinion(), 
                                                     self._ask_about_another_agent(ag_to_ask, ag_to_be_asked))))
                elif discount_type == discount_type_aberdeen3:   
                    self.trusts.append(TrustworthinessBetweenTwo(ag_to_be_asked, 
                                            subjective_logic.operators.graphical_combination3(t.get_opinion(), 
                                                     self._ask_about_another_agent(ag_to_ask, ag_to_be_asked))))
                elif discount_type == discount_type_uai:
                    self.trusts.append(TrustworthinessBetweenTwo(ag_to_be_asked, 
                                            subjective_logic.operators.discount_UAI_referee(t.get_opinion(), 
                                                     self._ask_about_another_agent(ag_to_ask, ag_to_be_asked))))
            
                
    
    def _ask_about_another_agent(self, ag_to_ask, ag_to_be_asked):
        return self.query(ag_to_ask,ag_to_be_asked)
    
    def query(self, other, question):
        answer = other.answer(question)
        self.interaction_history.append(InteractionHistory(other, repr(question), repr(answer)))
        return answer
        
    def answer(self, question):
        """
        This is the method that has to be called for asking something to an agent
        
        @param question: is the question that you want to ask. It can be 
                            (1) "question_omega" (questioning about the omega belief), or 
                            (2) "question_everything" (for asking which are its neighbours), or 
                            (3) an instance of the Agent class (for asking the opinion this agent has to the other)
                         
        This method returns:
            (1) either "omega_value" or "not omega_value" depending on the probability of lying
            (2) a list of neighbours that it knows that represents a subset (proper or improper) of the set of agents
                it knows according to the probability of lying. However it will never affirm to know an agent that actually
                it does not know (it can omit but not invent knowledge) 
            (3) it returns either its own opinion or a random opinion (which is required to be different form its own)
        """
        
        if isinstance(question, Agent):
            for rel in self.trusts:
                if rel.trustee == question:
                    if self._truth():
                        return rel.get_opinion()
                    else:
                        return subjective_logic.Opinion.get_random_opinion_different(rel.get_opinion())
        else:
            if question == question_omega:
                if self._truth():
                    return self.omega
                else:   
                    return not self.omega
            elif question == question_everything:
                ret = []
                for rel in self.trusts:
                    if self._truth():
                        if self._truth():
                            ret.append([rel.trustee, rel.get_opinion()])
                        else:
                            ret.append([rel.trustee, subjective_logic.Opinion.get_random_opinion_different(rel.get_opinion())])
                return ret
        
            
        
    def __repr__(self):
        return self.name
    
    
    def explore_network(self, discount_type, consensus_type):
        """
        Method used for backward compatibility, now deprecated
        See explore_network_general
        """
        return self.explore_network_general([discount_type, consensus_type])
    
    def explore_network_general(self, list_operators):
        """
        Method implementing the discovery of other agents in the network computing the derived trustworthiness degree according to
        the parameters.
        
        @param list_operators: a list (at most two elements) of element like [discount_type, consensus_type] 
                                where discount_type: "discount_type_josang" or "discount_type_aberdeen"
                                and consensus_type: "consensus_type_josang" or "consensus_type_aberdeen" or "consensus_type_none"
        """
        
        if len(list_operators) == 0 or len(list_operators) > 2:
            raise Exception("Error: list of at most two elements is needed")
        
        for op in list_operators:
            if len(op) != 2:
                raise Exception("Error: each element of the list must contain a discount operator and a consensus operator")
            
            if op[0] != discount_type_josang and op[0] != discount_type_aberdeen and op[0] != discount_type_aberdeen2 and op[0] != discount_type_aberdeen3 and op[0] != discount_type_uai:
                raise Exception("Error: unknown discount operator")
            
            if op[1] != consensus_type_josang and op[1] != consensus_type_aberdeen and op[1] != consensus_type_none:
                raise Exception("Error: unknown consensus operator")
        
        agent_known = [self]
        agent_asked = [self]
        
        for rel in self.trusts:
            agent_known.append(rel.trustee)
        
        while set(agent_known) != set(agent_asked):
            
            new_trusts = []
            for ag in (set(agent_known)).difference(set(agent_asked)):
            
                answ = self.query(ag,question_everything)
                agent_asked.append(ag)
                
                #print >> sys.stderr, repr(ag) + "\n" + repr(answ)
                
                
                if len(answ) > 0:
                    for [newagent, trust] in answ:
                        
                        if newagent not in set(agent_known):
                            inserted = False
                            if len(new_trusts) > 0:
                                for [oldagent, listtrust] in new_trusts:
                                    if newagent == oldagent:
                                        listtrust.append([ag, trust])
                                        inserted = True
                                        break
                                
                            if not inserted:
                                    new_trusts.append([newagent, [[ag, trust]]])
                                
                #print >> sys.stderr, "New trusts " + repr(new_trusts)
            
            for [newagent, listtrusts] in [[a,l] for [a,l] in new_trusts if a not in set(agent_known)]:
                
                agent_known.append(newagent)
                #print >> sys.stderr, "Computing " + repr(newagent)
                
                if len(listtrusts) >= 2:
                    list_t_w_first = []
                    list_t_w_second = []
                    for [ag, trust] in listtrusts:
                        
                        for rel in self.trusts:
                            if rel.trustee == ag:
                                discount_type = list_operators[0][0]
                                if (discount_type == discount_type_aberdeen):
                                    list_t_w_first.append([rel.get_opinion(), 
                                                 subjective_logic.operators.graphical_combination(rel.get_opinion(),trust)])
                                elif (discount_type == discount_type_aberdeen2):
                                    list_t_w_first.append([rel.get_opinion(), 
                                                 subjective_logic.operators.graphical_combination2(rel.get_opinion(),trust)])
                                elif (discount_type == discount_type_aberdeen3):
                                    list_t_w_first.append([rel.get_opinion(), 
                                                 subjective_logic.operators.graphical_combination3(rel.get_opinion(),trust)])
                                elif (discount_type == discount_type_josang):
                                    list_t_w_first.append([rel.get_opinion(), 
                                                 subjective_logic.operators.discount(rel.get_opinion(),trust)])
                                elif (discount_type == discount_type_uai):
                                    list_t_w_first.append([rel.get_opinion(), 
                                                 subjective_logic.operators.discount_UAI_referee(rel.get_opinion(),trust)])
                                    
                                if len(list_operators) == 2:
                                    discount_type = list_operators[1][0]
                                    if (discount_type == discount_type_aberdeen):
                                        list_t_w_second.append([rel.get_opinion(), 
                                                               subjective_logic.operators.graphical_combination(rel.get_opinion(),trust)])
                                    elif (discount_type == discount_type_aberdeen2):
                                        list_t_w_second.append([rel.get_opinion(), 
                                                               subjective_logic.operators.graphical_combination2(rel.get_opinion(),trust)])
                                    elif (discount_type == discount_type_aberdeen3):
                                        list_t_w_second.append([rel.get_opinion(), 
                                                               subjective_logic.operators.graphical_combination3(rel.get_opinion(),trust)])
                                    elif (discount_type == discount_type_josang):   
                                        list_t_w_second.append([rel.get_opinion(),   
                                                 subjective_logic.operators.discount(rel.get_opinion(),trust)])
                                    elif (discount_type == discount_type_uai):   
                                        list_t_w_second.append([rel.get_opinion(),   
                                                 subjective_logic.operators.discount_UAI_referee(rel.get_opinion(),trust)])
                    
                    opinion1 = None
                    opinion2 = None
                    
                    consensus_type = list_operators[0][1]
                    if (consensus_type == consensus_type_aberdeen):
                        opinion1 = subjective_logic.operators.graphical_discount_merge(list_t_w_first)
                    elif (consensus_type == consensus_type_josang):
                        opinion1 = subjective_logic.operators.consensus_on_a_list(list_t_w_first)
                    
                    if len(list_operators) == 2:
                        consensus_type = list_operators[1][1]
                        if (consensus_type == consensus_type_aberdeen):
                            opinion2 = subjective_logic.operators.graphical_discount_merge(list_t_w_first)
                        elif (consensus_type == consensus_type_josang):
                            opinion2 = subjective_logic.operators.consensus_on_a_list(list_t_w_first)
                    
                    if (len(list_operators) == 2 and opinion2 == None):
                        raise Exception("Error!")
                    
                    self.trusts.append(TrustworthinessBetweenTwo(newagent,opinion1,opinion2))
                        
                else:
                    ag = listtrusts[0][0]
                    trust = listtrusts[0][1]
                    for rel in self.trusts:
                        if rel.trustee == ag:
                            opinion1 = None
                            opinion2 = None
                            
                            discount_type = list_operators[0][0]
                            if (discount_type == discount_type_aberdeen):
                                opinion1 = subjective_logic.operators.graphical_combination(rel.get_opinion(),trust)
                            elif (discount_type == discount_type_aberdeen2):
                                opinion1 = subjective_logic.operators.graphical_combination2(rel.get_opinion(),trust)
                            elif (discount_type == discount_type_aberdeen3):
                                opinion1 = subjective_logic.operators.graphical_combination3(rel.get_opinion(),trust)
                            elif (discount_type == discount_type_josang):
                                opinion1 = subjective_logic.operators.discount(rel.get_opinion(),trust)
                            elif (discount_type == discount_type_uai):
                                opinion1 = subjective_logic.operators.discount_UAI_referee(rel.get_opinion(),trust)
                                
                            if (len(list_operators) == 2):
                                discount_type = list_operators[1][0]
                                if (discount_type == discount_type_aberdeen):
                                    opinion2 = subjective_logic.operators.graphical_combination(rel.get_opinion(),trust)
                                elif (discount_type == discount_type_aberdeen2):
                                    opinion2 = subjective_logic.operators.graphical_combination2(rel.get_opinion(),trust)
                                elif (discount_type == discount_type_aberdeen3):
                                    opinion2 = subjective_logic.operators.graphical_combination3(rel.get_opinion(),trust)
                                elif (discount_type == discount_type_josang):
                                    opinion2 = subjective_logic.operators.discount(rel.get_opinion(),trust)
                                elif (discount_type == discount_type_uai):
                                    opinion2 = subjective_logic.operators.discount_UAI_referee(rel.get_opinion(),trust)
                                    
                            if (len(list_operators) == 2 and opinion2 == None):
                                raise Exception("Error!")   
                            
                            self.trusts.append(TrustworthinessBetweenTwo(newagent,opinion1,opinion2))
                            
    
                            
    def get_opinion_agent(self, agent):
        """
        @param agent: the agent which we want to know the (real) opinion that this agent has of
        @return the real opinion
        
        To be used only for evaluating the computation, not for asking from another agent perspective (for that using the method query(agent, question) )
        """
        for tr in self.trusts:
            if tr.trustee == agent:
                return [tr.get_first_opinion(), tr.get_second_opinion()]
            
        return None