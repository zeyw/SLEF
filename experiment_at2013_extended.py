"""
experiment_at2013_same_exploration package
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

Package encompassing the experiment developed for the paper 

Subjective Logic Operators in Trust Assessment: An Empirical Study

by F. Cerutti, L. M. Kaplan, T. J. Norman, N. Oren, and A. Toniolo

ISF Journal, 2014
"""


import os

import experimental_framework.Experiment
from experimental_framework.Network import Agent
import mpmath
import sys

class AberdeenExperimentBothOperatorsSameExploration(experimental_framework.Experiment.BootstrapExperiment,experimental_framework.Experiment.ExperimentBetweenTwoSameExploration):
    """
    Class describing the experiment. It inherits both from BootstrapExperiment and ExperimentBetweenTwoSameExploration
    """
    
    def __init__(self, name, chosen_agent):
        super(AberdeenExperimentBothOperatorsSameExploration,self).__init__(name,chosen_agent)
        
        
    def run_experiment(self):
        josang_network_name = "josang"
        aberdeen_network_name = "aberdeen"
        aberdeen_network_name2 = "aberdeen2"
        aberdeen_network_name3 = "aberdeen3"
        uai_network_name1 = "uai1"
        uai_network_name2 = "uai2"
        
        self._experiment_set.add_network(self._network_exploration_general(aberdeen_network_name + " AND " + josang_network_name, 
                                                                           self._bootstrapped_network, 
                                                                           [[experimental_framework.Network.discount_type_aberdeen,experimental_framework.Network.consensus_type_aberdeen],
                                                                            [experimental_framework.Network.discount_type_josang,experimental_framework.Network.consensus_type_josang]
                                                                            ]))
        self._experiment_set2.add_network(self._network_exploration_general(aberdeen_network_name2 + " AND " + josang_network_name, 
                                                                           self._bootstrapped_network, 
                                                                           [[experimental_framework.Network.discount_type_aberdeen2,experimental_framework.Network.consensus_type_aberdeen],
                                                                            [experimental_framework.Network.discount_type_josang,experimental_framework.Network.consensus_type_josang]
                                                                            ]))
        self._experiment_set3.add_network(self._network_exploration_general(aberdeen_network_name3 + " AND " + josang_network_name, 
                                                                           self._bootstrapped_network, 
                                                                           [[experimental_framework.Network.discount_type_aberdeen3,experimental_framework.Network.consensus_type_aberdeen],
                                                                            [experimental_framework.Network.discount_type_josang,experimental_framework.Network.consensus_type_josang]
                                                                            ]))
        self._experiment_set4.add_network(self._network_exploration_general(uai_network_name1 + " AND " + josang_network_name, 
                                                                           self._bootstrapped_network, 
                                                                           [[experimental_framework.Network.discount_type_uai,experimental_framework.Network.consensus_type_aberdeen],
                                                                            [experimental_framework.Network.discount_type_josang,experimental_framework.Network.consensus_type_josang]
                                                                            ]))
        


def experiment(path):
    csv = open(path+'/summary.csv','w')
    numagents = 50
    for perclink in range(5, 26, 5):
        #for num_b in range(25,251,25):
        for num_b in range(2,30,3):
            agents = []
            for i in range(numagents):
                agents.append(Agent("Agent"+repr(i), mpmath.rand()))
            
            for ag1 in agents:
                for ag2 in agents:
                    if ag1 != ag2 and int(mpmath.floor(mpmath.rand()*100)) < perclink:
                        ag1.addNeighbour(ag2)
            
            chosen_agent = int(mpmath.floor(mpmath.rand()*numagents))
            
            t = AberdeenExperimentBothOperatorsSameExploration(path+'/exp-'+repr(numagents)+'-'+repr(perclink)+'-'+repr(num_b)+'-'+repr(chosen_agent),
                                                                     "Agent"+repr(chosen_agent))
            
            print >> sys.stderr, 'exp-'+repr(numagents)+'-'+repr(perclink)+'-'+repr(num_b)+'-'+repr(chosen_agent) + "\n"
            
            for ag in agents:
                t.add_agent(ag)
                
            t.save()
            
            t.bootstrap(num_b)
            t.save()
            
            print "bootstrapped"
            
            for i in range(25):
            #for i in range(5):
                print "iteration num: " + repr(i)
                t.run_experiment()
                t.save()

            [r1, r2, r3, r4, r1b, r2b, r3b, r4b] = t.distance_ratio_results()
            mean1 = "" # operator AT2013 - conference
            std1 = ""
            mean2 = "" # operator AT2013 extended parallel
            std2 = ""
            mean3 = "" # operator AT2013 extended half
            std3 = ""
            mean4 = "" # operator UAI referee
            std4 = ""
            
            #distance between expected values as suggested by Lance
            mean1b = "" # operator AT2013 - conference
            std1b = ""
            mean2b = "" # operator AT2013 extended parallel
            std2b = ""
            mean3b = "" # operator AT2013 extended half
            std3b = ""
            mean4b = "" # operator UAI referee
            std4b = ""
            
            if r1.get_mean_std() != None:
                mean1 = r1.get_mean_std()[0]
                std1 = r1.get_mean_std()[1]
            if r2.get_mean_std() != None:
                mean2 = r2.get_mean_std()[0]
                std2 = r2.get_mean_std()[1]
            if r3.get_mean_std() != None:
                mean3 = r3.get_mean_std()[0]
                std3 = r3.get_mean_std()[1]
            if r4.get_mean_std() != None:
                mean4 = r4.get_mean_std()[0]
                std4 = r4.get_mean_std()[1]
                
            
            if r1b.get_mean_std() != None:
                mean1b = r1b.get_mean_std()[0]
                std1b = r1b.get_mean_std()[1]
            if r2b.get_mean_std() != None:
                mean2b = r2b.get_mean_std()[0]
                std2b = r2b.get_mean_std()[1]
            if r3b.get_mean_std() != None:
                mean3b = r3b.get_mean_std()[0]
                std3b = r3b.get_mean_std()[1]
            if r4b.get_mean_std() != None:
                mean4b = r4b.get_mean_std()[0]
                std4b = r4b.get_mean_std()[1]    
            
            csv.write('"{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}","{9}","{10}","{11}","{12}","{13}","{14}","{15}","{16}","{17}","{18}"\n'.format(perclink,num_b,chosen_agent,mean1,std1,mean2,std2,mean3,std3,mean4,std4,mean1b,std1b,mean2b,std2b,mean3b,std3b,mean4b,std4b))
            csv.flush()
            
    csv.close()


if __name__ == "__main__":
    
    for i in range(10):
    #for i in range(1):
        path = "/home/geryo/experiments/test-20131024/test-"+repr(i)
        os.mkdir(path)
        experiment(path)

