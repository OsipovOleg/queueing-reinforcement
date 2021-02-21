from queueing import Action
from queueing import QueueingSystem

lambd = 1
fast_server_rate = 0.7
slow_server_rate = 0.2
queue_capacity = 10
loss_penalty = 1
simulation_time = 10 ** 6


def service_income(service_duration):
    return 1 / (1 + service_duration)


def decision_function(queue_size):
    return Action.MOVE_TO_SERVER


qs = QueueingSystem(lambd, fast_server_rate, slow_server_rate, queue_capacity, loss_penalty,
                    service_income, decision_function)
qs.run(simulation_time)

print(qs)

print(qs._total_benefit / simulation_time)
