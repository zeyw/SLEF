"""
Experiment package
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

Package encompassing the base classes for defining experiments in
trust networks
"""


from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from baseSQL import Base
from Network import Agent
from Network import AgentNetwork
from Network import ListNetworks
import Network
from beta_distribution.History import History
from mpmath import mpf
from subjective_logic.Opinion import Opinion
import pydot
import mpmath
import Gnuplot
import numpy
import tempfile
import os
import sys

## String for identifying the original network in the database
original_network_name = "original"

## String for identifying the bootsrapped network in the database
bootstrapped_network_name = "bootstrapped"

def abort_ro(*args,**kwargs):
    ''' the terrible consequences for trying 
        to flush to the db '''
    print >> sys.stderr, "No writing allowed, tsk!  We're telling mom!"
    return 

class ExperimentData(Base):
    """
    Class defining element typical of the experiment
    
    It should never directly called.
    
    @var chosen_agent: is the name of the agent chosen for exploring the network
    """
    __tablename__ = 'experimentdata'
    id = Column(Integer, primary_key=True)
    chosen_agent = Column(String(500))
    
    
    def __init__(self, agent_name=None):
        if agent_name!=None:
            self.chosen_agent = agent_name
        
        

class GenericExperiment(object):
    """
    Class defining the general methods for an experiment and the 
    interaction with the database
    
    It should be considered as an abstract class and never directly
    called.
    
    @var _original: should always contains the original network. If you
                    want to make it evolve, you should clone it before
                    and then operate on the cloned version
    """
    _dbname = ''
    _original = None
    _data = None
    
    def __init__(self, name, chosen_agent):
        try:
            with open(name+'.db'): self._protection = True
        except IOError:
            self._protection = False
        
        self._dbname = name
       
        self._create_session()

        if not self._protection:        
            self._original = AgentNetwork(original_network_name)
            self._session.add(self._original)
            
            self._data = ExperimentData(chosen_agent)
            self._session.add(self._data)
            
            self.save()
            
        else:
            print >> sys.stderr, "The loading begins..."
            
            self._original = self._session.query(AgentNetwork).filter_by(name = 'original').first()
            self._data = self._session.query(ExperimentData).first()
       
    def is_protected(self):
        return self._protection
    
    def _create_session(self):
        self._engine = create_engine("sqlite:///"+self._dbname+".db")
        Base.metadata.create_all(self._engine)
        Session = sessionmaker(bind=self._engine)
        self._session = Session()
        
        if self._protection:
            self._session.flush = abort_ro   # now it won't flush!
        
    def _refresh_session(self):
        self._close_session()
        self._create_session

    def save(self):
        self._session.commit()
        
    def add_agent(self, x):
        if isinstance(x, Agent):
            self._original.add_agent(x)
                        
    def _network_exploration(self, name_new_network, to_clone, discount, consensus):
        self._network_exploration_general(name_new_network, to_clone, [discount, consensus])
    
    def _network_exploration_general(self, name_new_network, to_clone, list_operators):
        self.save()
        n = AgentNetwork(name_new_network)
        self._session.add(n)
        to_clone.clone(n)
        self.save()
        
        n.get_agent_by_name(self._data.chosen_agent).explore_network_general(list_operators)
        return n

class BootstrapExperiment(GenericExperiment):
    """
    Class describing the experiment of bootstrapping a network by using the beta reputation
    system.
    
    You should be ready to inherit from this class.
    
    @var _bootstrapped_network: the new network computed after the bootstrapping
    """
    
    _bootstrapped_network = None
    
    def __init__(self,name,chosen_agent):
        super(BootstrapExperiment,self).__init__(name,chosen_agent)
        if self._protection:
            print >> sys.stderr, "...the loading continues with the bootstrap data..."
            self._bootstrapped_network = self._session.query(AgentNetwork).filter(AgentNetwork.name==bootstrapped_network_name).first()
    
    def bootstrap(self, bootstraptime):
        if not self._protection:
            self.save()
            self._bootstrapped_network = AgentNetwork(bootstrapped_network_name)
            self._session.add(self._bootstrapped_network) 
            self._original.clone(self._bootstrapped_network)
            self.save()
            
            for ag in self._bootstrapped_network.get_agents():
                ag.knowYourNeighbours(bootstraptime)
                
            self.save()

class DistancesBetweenTwo(object):
    """
    Class encompassing the data structures needed for computing the distances
    (and the ratio) between two opinions derived using some operators and the
    real opinion derived by looking inside an agent.
    
    It should be never called.
    """
    
    _agent = None
    _first_distances = None
    _second_distances = None
    _ratio = None
    _mean_std_ratio = None
    
    def __init__(self, ag):
        self._agent = ag
        self._first_distances = []
        self._second_distances = []
        self._ratio = None
        self._mean_std_ratio = []
    
    def get_agent(self):
        return self._agent
    
    def add_first_distance(self, value):
        self._first_distances.append(value)
        
    def add_second_distance(self, value):
        self._second_distances.append(value)
    
    def check(self):
        if len(self._first_distances) != len(self._second_distances):
            raise Exception("Error")
    
    def get_ratios(self):
        if self._ratio == None:
            self.check()
            self._ratio = []
    
            for i in range(len(self._second_distances)):
                if self._first_distances[i] != None and self._second_distances[i] != None:
                    if self._second_distances[i] >= self._first_distances[i]:
                        self._ratio.append(mpmath.log10(self._second_distances[i]/self._first_distances[i]))
                    else:
                        self._ratio.append(-mpmath.log10(self._first_distances[i]/self._second_distances[i]))
                        
        return self._ratio
        
    def get_mean_std_ratio(self):
        if self._mean_std_ratio == []:
            if self.get_ratios() == None or len(self.get_ratios()) == 0:
                self._mean_std_ratio = None
            else:
                self._mean_std_ratio = [numpy.average(numpy.array([float(r) for r in self.get_ratios()])), numpy.std(numpy.array([float(r) for r in self.get_ratios()]))]
            
        return self._mean_std_ratio


class ResultsExperimentBetweenTwo(object):
    """
    Class representing the differences, the ratio, mean, standard deviation when
    the distances between opinion derived using two set of operators and the real one
    has been computed.
    """
    _list_results = None
    _last_res = None
    _mean_std = None
    
    def __init__(self, list_agents):
        self._list_results = []
        self._last_res = None
        self._mean_std = []
        
        for ag in list_agents:
            self._list_results.append(DistancesBetweenTwo(ag))
    
    def _result_from_agent(self, ag):
        for res in self._list_results:
            if ag == res.get_agent():
                return res
    
    def add_first_distance(self, ag, value):
        self._result_from_agent(ag).add_first_distance(value)
        
        
    def add_second_distance(self, ag, value):
        self._result_from_agent(ag).add_second_distance(value)

    
    def get_ratios(self, ag):
        return self._result_from_agent(ag).get_ratios()
    
    def get_mean_std_ratio(self, ag):
        return self._result_from_agent(ag).get_mean_std_ratio()
    
    def _check_mean_std_ratio_none(self):
        for r in self._list_results:
            if r.get_mean_std_ratio() != None:
                return False
            
        return True
    
    def get_mean_std(self):
        """
        @return [mean, std]:    mean is the average across all the ratios
                                std is the standard deviation across all the ratios
        """
        if self._mean_std == []:
            if self._check_mean_std_ratio_none():
                self._mean_std = None
            else:
                self._mean_std = [numpy.average(numpy.array([r.get_mean_std_ratio()[0] for r in self._list_results if r.get_mean_std_ratio() != None])),
                                  numpy.std(numpy.array([r.get_mean_std_ratio()[0] for r in self._list_results if r.get_mean_std_ratio() != None]))
                                  ]
        
        return self._mean_std
    

class ExperimentBetweenTwo(GenericExperiment):
    """
    Class that provides the basics for an experiment where a comparison between two
    is required. BROKEN DO NOT USE!!!
     
    You should be ready to inherit from this class.
     
    @var _first_set: is the one that you hope will perform better
    @var _second_set: is the one that you hope will perform worse
    """
    _first_set = None
    _second_set = None
    _result = None
     
    def __init__(self,name,chosen_agent):
        super(ExperimentBetweenTwo,self).__init__(name,chosen_agent)
         
        if self._protection:
            print >> sys.stderr, "...loading continues with experiment between two..."
            self._first_set = self._session.query(ListNetworks).filter(ListNetworks.name=="First").first()
            self._second_set = self._session.query(ListNetworks).filter(ListNetworks.name=="Second").first()
            self._result = None
            #self._result = ResultsExperimentBetweenTwo(self._original.get_agents())
             
        else:
            self._first_set = ListNetworks("First")
            self._session.add(self._first_set)
            self._second_set = ListNetworks("Second")
            self._session.add(self._second_set)
            self._result = None
     
    def distance_ratio_results(self):
        """
        @return result (instance of ResultsExperimentBetweenTwo)
        """
         
        if self._result == None:
            self._result = ResultsExperimentBetweenTwo(self._original.get_agents())
             
        if self._result2 == None:
            self._result2 = ResultsExperimentBetweenTwo(self._original.get_agents())
             
        if self._result3 == None:
            self._result3 = ResultsExperimentBetweenTwo(self._original.get_agents())
         
        for ag in self._original.get_agents():
            if ag.name != self._data.chosen_agent:
                correct_opinion = Opinion(eval(ag.probability), mpf("1") - eval(ag.probability), "0", "1/2")
 
                for network in self._first_set.get_networks():
                    if network.get_agent_by_name(self._data.chosen_agent).get_opinion_agent(ag) != None:
                        #print correct_opinion.distance(network.get_agent_by_name(self._data.chosen_agent).get_opinion_agent(ag))
                        self._result.add_first_distance(ag, correct_opinion.distance(network.get_agent_by_name(self._data.chosen_agent).get_opinion_agent(ag)))
                    else:
                        self._result.add_first_distance(ag, None)
                 
               
                for network in self._second_set.get_networks():
                    if network.get_agent_by_name(self._data.chosen_agent).get_opinion_agent(ag) != None:
                        #print correct_opinion.distance(network.get_agent_by_name(self._data.chosen_agent).get_opinion_agent(ag))
                        self._result.add_second_distance(ag, correct_opinion.distance(network.get_agent_by_name(self._data.chosen_agent).get_opinion_agent(ag)))
                    else:
                        self._result.add_second_distance(ag, None)
     
        return self._result
    
    
class ExperimentBetweenTwoSameExploration(GenericExperiment):
    """
    Class that provides the basics for an experiment where a comparison between two
    is required (the two values should be computed during the same network exploration).
    
    You should be ready to inherit from this class.
    """
    _experiment_set = None
    _experiment_set2 = None
    _experiment_set3 = None
    _experiment_set4 = None
    _result = None
    _result2 = None
    _result3 = None
    _result4 = None
    
    _result_b = None
    _result2_b = None
    _result3_b = None
    _result4_b = None
    
    def __init__(self,name,chosen_agent):
        super(ExperimentBetweenTwoSameExploration,self).__init__(name,chosen_agent)
        
        if self._protection:
            print >> sys.stderr, "...loading continues with experiment between two..."
            self._experiment_set = self._session.query(ListNetworks).filter(ListNetworks.name=="Experiment2").first()
            self._experiment_set2 = self._session.query(ListNetworks).filter(ListNetworks.name=="Experiment2-2").first()
            self._experiment_set3 = self._session.query(ListNetworks).filter(ListNetworks.name=="Experiment2-3").first()
            self._experiment_set4 = self._session.query(ListNetworks).filter(ListNetworks.name=="Experiment2-4").first()
            self._result = None
            self._result2 = None
            self._result3 = None
            self._result4 = None
            
            self._result_b = None
            self._result2_b = None
            self._result3_b = None
            self._result4_b = None
            
            #self._result = ResultsExperimentBetweenTwo(self._original.get_agents())
            
        else:
            self._experiment_set = ListNetworks("Experiment2")
            self._experiment_set2 = ListNetworks("Experiment2-2")
            self._experiment_set3 = ListNetworks("Experiment2-3")
            self._experiment_set4 = ListNetworks("Experiment2-4")
            self._session.add(self._experiment_set)
            self._session.add(self._experiment_set2)
            self._session.add(self._experiment_set3)
            self._session.add(self._experiment_set4)
            self._result = None
            self._result2 = None
            self._result3 = None
            self._result4 = None
            
            self._result_b = None
            self._result2_b = None
            self._result3_b = None
            self._result4_b = None
    
    def distance_ratio_results(self):
        """
        @return result (instance of ResultsExperimentBetweenTwo)
        """
        
        if self._result == None:
            self._result = ResultsExperimentBetweenTwo(self._original.get_agents())
            
        if self._result2 == None:
            self._result2 = ResultsExperimentBetweenTwo(self._original.get_agents())
            
        if self._result3 == None:
            self._result3 = ResultsExperimentBetweenTwo(self._original.get_agents())
            
        if self._result4 == None:
            self._result4 = ResultsExperimentBetweenTwo(self._original.get_agents())
            
        
        if self._result_b == None:
            self._result_b = ResultsExperimentBetweenTwo(self._original.get_agents())
            
        if self._result2_b == None:
            self._result2_b = ResultsExperimentBetweenTwo(self._original.get_agents())
            
        if self._result3_b == None:
            self._result3_b = ResultsExperimentBetweenTwo(self._original.get_agents())
            
        if self._result4_b == None:
            self._result4_b = ResultsExperimentBetweenTwo(self._original.get_agents())    
        
        
        for ag in self._original.get_agents():
            if ag.name != self._data.chosen_agent:
                correct_opinion = Opinion(eval(ag.probability), mpf("1") - eval(ag.probability), "0", "1/2")

                for network in self._experiment_set.get_networks():
                    if network.get_agent_by_name(self._data.chosen_agent).get_opinion_agent(ag) != None:
                        opinions = network.get_agent_by_name(self._data.chosen_agent).get_opinion_agent(ag)
                        self._result.add_first_distance(ag, correct_opinion.distance(opinions[0]))
                        self._result.add_second_distance(ag, correct_opinion.distance(opinions[1]))
                        
                        self._result_b.add_first_distance(ag, correct_opinion.distance_expected_value(opinions[0]))
                        self._result_b.add_second_distance(ag, correct_opinion.distance_expected_value(opinions[1]))
                    else:
                        self._result.add_first_distance(ag, None)
                        self._result.add_second_distance(ag, None)
                        
                        self._result_b.add_first_distance(ag, None)
                        self._result_b.add_second_distance(ag, None)
                        
                for network in self._experiment_set2.get_networks():
                    if network.get_agent_by_name(self._data.chosen_agent).get_opinion_agent(ag) != None:
                        opinions = network.get_agent_by_name(self._data.chosen_agent).get_opinion_agent(ag)
                        self._result2.add_first_distance(ag, correct_opinion.distance(opinions[0]))
                        self._result2.add_second_distance(ag, correct_opinion.distance(opinions[1]))
                        
                        self._result2_b.add_first_distance(ag, correct_opinion.distance_expected_value(opinions[0]))
                        self._result2_b.add_second_distance(ag, correct_opinion.distance_expected_value(opinions[1]))
                    else:
                        self._result2.add_first_distance(ag, None)
                        self._result2.add_second_distance(ag, None)
                        
                        self._result2_b.add_first_distance(ag, None)
                        self._result2_b.add_second_distance(ag, None)
    
                for network in self._experiment_set3.get_networks():
                    if network.get_agent_by_name(self._data.chosen_agent).get_opinion_agent(ag) != None:
                        opinions = network.get_agent_by_name(self._data.chosen_agent).get_opinion_agent(ag)
                        self._result3.add_first_distance(ag, correct_opinion.distance(opinions[0]))
                        self._result3.add_second_distance(ag, correct_opinion.distance(opinions[1]))
                        
                        self._result3_b.add_first_distance(ag, correct_opinion.distance_expected_value(opinions[0]))
                        self._result3_b.add_second_distance(ag, correct_opinion.distance_expected_value(opinions[1]))
                    else:
                        self._result3.add_first_distance(ag, None)
                        self._result3.add_second_distance(ag, None)
                        
                        self._result3_b.add_first_distance(ag, None)
                        self._result3_b.add_second_distance(ag, None)
                        
                for network in self._experiment_set4.get_networks():
                    if network.get_agent_by_name(self._data.chosen_agent).get_opinion_agent(ag) != None:
                        opinions = network.get_agent_by_name(self._data.chosen_agent).get_opinion_agent(ag)
                        self._result4.add_first_distance(ag, correct_opinion.distance(opinions[0]))
                        self._result4.add_second_distance(ag, correct_opinion.distance(opinions[1]))
                        
                        self._result4_b.add_first_distance(ag, correct_opinion.distance_expected_value(opinions[0]))
                        self._result4_b.add_second_distance(ag, correct_opinion.distance_expected_value(opinions[1]))
                    else:
                        self._result4.add_first_distance(ag, None)
                        self._result4.add_second_distance(ag, None)
                        
                        self._result4_b.add_first_distance(ag, None)
                        self._result4_b.add_second_distance(ag, None)
        
        return [self._result, self._result2, self._result3, self._result4, self._result_b, self._result2_b, self._result3_b, self._result4_b]
        
        
    