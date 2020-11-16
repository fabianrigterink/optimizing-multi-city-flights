from pyomo import environ as pyo

import itertools
import pandas as pd
import sys

class ClientSolver():
    model = None
    instance = None

    def __init__(self):
        pass

    def generate_model(self):
        self.model = pyo.AbstractModel()

        # Sets and parameters
        self.model.N0 = pyo.Set()
        self.model.N = pyo.Set(within=self.model.N0)
        self.model.T = pyo.Set()
        
        def n_init(model):
            return len(model.N0)
        self.model.n = pyo.Param(initialize=n_init, within=pyo.NonNegativeIntegers)

        self.model.N0N0 = pyo.RangeSet(0, (2**self.model.n - 1))
        def S_init(model, k):
            return [model.N0[i] for i in range(1, len(model.N0)+1) if int(k/2**(i-1)) % 2 == 1]
        self.model.S = pyo.Set(self.model.N0N0, within=self.model.N0, initialize=S_init)

        self.model.sMin = pyo.Param(self.model.N, within=pyo.NonNegativeIntegers)
        self.model.sMax = pyo.Param(self.model.N, within=pyo.NonNegativeIntegers)

        self.model.c = pyo.Param(self.model.N0, self.model.N0, self.model.T, within=pyo.NonNegativeReals, default=sys.maxsize)

        # Variables
        self.model.x = pyo.Var(self.model.N0, self.model.N0, self.model.T, domain=pyo.Binary)

        # Objective
        def obj_rule(model):
            return sum(model.c[i, j, t] * model.x[i, j, t] for (i, j, t) in list(itertools.product(model.N0, model.N0, model.T)) if i != j)
        self.model.Obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

        # Constraint 1: every node must have an outbound flight
        def con1_rule(model, i):
            return sum(model.x[i, j, t] for (j, t) in list(itertools.product(model.N0, model.T)) if i != j) == 1
        self.model.Con1 = pyo.Constraint(self.model.N0, rule=con1_rule)

        # Constraint 2: every node must have an inbound flight
        def con2_rule(model, j):
            return sum(model.x[i, j, t] for (i, t) in list(itertools.product(model.N0, model.T)) if i != j) == 1
        self.model.Con2 = pyo.Constraint(self.model.N0, rule=con2_rule)

        # Constraint 3: subtour elimination
        def con3_rule(model, k):
            if len(model.S[k]) >= 1 and len(model.S[k]) < model.n:
                return sum(model.x[i, j, t] for (i, j, t) in list(itertools.product(model.S[k], model.N0, model.T)) if j not in model.S[k]) >= 1
            else:
                return pyo.Constraint.Feasible
        self.model.Con3 = pyo.Constraint(self.model.N0N0, rule=con3_rule)

        # Constraint 4a: minimum time of stay
        def con4a_rule(model, j):
            return sum(t * model.x[i, j, model.T[t]] for (i, t) in list(itertools.product(model.N0, range(1, len(model.T)+1))) if i != j) + model.sMin[j] \
                <= sum(t * model.x[j, k, model.T[t]] for (k, t) in list(itertools.product(model.N0, range(1, len(model.T)+1))) if j != k)
        self.model.Con4a = pyo.Constraint(self.model.N, rule=con4a_rule)

        # Constraint 4b: maximum time of stay
        def con4b_rule(model, j):
            return sum(t * model.x[i, j, model.T[t]] for (i, t) in list(itertools.product(model.N0, range(1, len(model.T)+1))) if i != j) + model.sMax[j] \
                >= sum(t * model.x[j, k, model.T[t]] for (k, t) in list(itertools.product(model.N0, range(1, len(model.T)+1))) if j != k)
        self.model.Con4b = pyo.Constraint(self.model.N, rule=con4b_rule)

    def generate_instance(self, instance_name: str, home: str, quotes: pd.DataFrame, stays_min: dict, stays_max: dict):
        assert self.model is not None, 'Model is not yet generated. You must call generate_model() before you can call generate_instance(...).'

        s = ''
        
        # Generate N0
        origins = list(quotes['origin'].unique())
        s += 'set N0 := {} ;\n'.format(' '.join(origins))

        # Generate N
        assert home in origins, 'Home \'{}\' is not in quotes\' origins. Exit.'.format(home)
        origins.remove(home)
        s += 'set N := {} ;\n'.format(' '.join(origins))

        # Generate T
        outbound_dates = list(quotes['outbound_date'].unique())
        s += 'set T := {} ;\n'.format(' '.join(outbound_dates))

        quotes.dropna(inplace=True)
        # Generate c
        s += 'param c :=\n'
        for _, row in quotes.iterrows():
            s += '{} {} {} {}\n'.format(row['origin'], row['destination'], row['outbound_date'], row['quote'])
        s += ';\n'

        # Generate sMin
        s += 'param sMin :=\n'
        for key in stays_min.keys():
            s += '{} {}\n'.format(key, stays_min.get(key))
        s += ';\n'

        # Generate sMax
        s += 'param sMax :=\n'
        for key in stays_max.keys():
            s += '{} {}\n'.format(key, stays_max.get(key))
        s += ';\n'

        instance_file = 'data/instance_{}.dat'.format(instance_name)
        f = open(instance_file, 'w')
        f.write(s)
        f.close()

        self.instance = self.model.create_instance(instance_file)

    def solve(self):
        assert self.instance is not None, 'Instance is not yet generated. You must call generate_instance(...) before you can call solve().'

        # Solve the instance using NEOS and CPLEX
        results = pyo.SolverManagerFactory('neos').solve(self.instance, opt='cplex')

        # Print the results
        results.write(num=1)

        # Print the optimal solution
        solution = pd.DataFrame()
        for i in self.instance.x:
            if self.instance.x[i].value == 1:
                d = {
                    'origin': i[0],
                    'destination': i[1],
                    'outbound_date': i[2],
                    'quote': self.instance.c[i]
                }
                solution = solution.append(d, ignore_index=True)
        
        solution = solution[['origin', 'destination', 'outbound_date', 'quote']]
        solution.sort_values(by=['outbound_date'], inplace=True, ignore_index=True)

        print(solution)