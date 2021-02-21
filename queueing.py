import random
from enum import Enum


class Action(Enum):
    LEAVE_TO_QUEUE = "leave to the queue"
    MOVE_TO_SERVER = "move to a free fastest server"


class Demand:
    def __init__(self):
        self.arrival_time = None
        self.start_service_time = None
        self.leave_time = None


class QueueingSystem:
    _FAST_SERVER_ID = 0
    _SLOW_SERVER_ID = 1

    def __init__(self, lambd, fast_server_rate, slow_server_rate, queue_capacity, loss_penalty, service_income,
                 decision_function):
        self._lambda = lambd
        self._server_rates = [fast_server_rate, slow_server_rate]
        self._loss_penalty = loss_penalty
        self._time_benefit_function = service_income
        self._queue_capacity = queue_capacity
        self._decision_function = decision_function
        self._number_of_servers = 2
        self._current_time = 0
        self._next_arrival_time = float('inf')
        self._next_start_service_times = float('inf')
        self._next_leave_times = [float('inf')] * self._number_of_servers
        self._queue = None
        self._servers = [None, None]
        self._total_benefit = None

    def run(self, max_time):
        self._current_time = 0
        self._total_benefit = 0

        self._queue = []
        self._servers = [None, None]

        self._next_arrival_time = 0
        self._next_start_service_times = float('inf')
        self._next_leave_times = [float('inf')] * self._number_of_servers

        self._average_response_time = 0
        self._response_times_sample_size = 0
        self._loss_probability = 0
        self._n_arrivals = 0

        while self._current_time < max_time:
            next_event_time = min(self._next_arrival_time,
                                  self._next_start_service_times,
                                  self._next_leave_times[0],
                                  self._next_leave_times[1])
            self._current_time = next_event_time

            if next_event_time == self._next_arrival_time:
                self._arrival_event()
            elif next_event_time == self._next_start_service_times:
                self._start_service_event()
            elif next_event_time == self._next_leave_times[QueueingSystem._FAST_SERVER_ID]:
                self._leave_from_server(QueueingSystem._FAST_SERVER_ID)
            elif next_event_time == self._next_leave_times[QueueingSystem._SLOW_SERVER_ID]:
                self._leave_from_server(QueueingSystem._SLOW_SERVER_ID)
            else:
                raise Exception("")

        self._average_response_time /= self._response_times_sample_size
        self._loss_probability /= self._n_arrivals
        return self._average_response_time, self._loss_probability

    def _arrival_event(self):
        self._n_arrivals += 1
        if len(self._queue) > self._queue_capacity:
            self._total_benefit -= self._loss_penalty

            self._loss_probability += 1
        else:
            demand = Demand()
            demand.arrival_time = self._current_time
            self._queue.append(demand)
            self._next_start_service_times = self._current_time
        self._next_arrival_time += random.expovariate(self._lambda)

    def _start_service_event(self):
        if self._queue:
            if self._servers[QueueingSystem._FAST_SERVER_ID] is None:
                self._servers[QueueingSystem._FAST_SERVER_ID] = self._queue.pop(0)
                service_duration = random.expovariate(self._server_rates[QueueingSystem._FAST_SERVER_ID])
                self._next_leave_times[QueueingSystem._FAST_SERVER_ID] = self._current_time + service_duration
            elif self._servers[QueueingSystem._SLOW_SERVER_ID] is None:
                action = self._decision_function(len(self._queue))
                if action is Action.MOVE_TO_SERVER:
                    self._servers[QueueingSystem._SLOW_SERVER_ID] = self._queue.pop(0)
                    service_duration = random.expovariate(self._server_rates[QueueingSystem._SLOW_SERVER_ID])
                    self._next_leave_times[QueueingSystem._SLOW_SERVER_ID] = self._current_time + service_duration
        self._next_start_service_times = float('inf')

    def _leave_from_server(self, server_id: int):
        if self._servers[server_id] is not None:
            demand_in_server = self._servers[server_id]
            demand_in_server.leave_time = self._current_time
            response_time = demand_in_server.leave_time - demand_in_server.arrival_time
            self._total_benefit += self._time_benefit_function(response_time)
            self._servers[server_id] = None
            self._next_start_service_times = self._current_time
            # statistics
            self._response_times_sample_size += 1
            self._average_response_time += response_time

        self._next_leave_times[server_id] = float('inf')

    def __str__(self):
        return f"""
        total_benefit: {self._total_benefit}
        average_response_time: {self._average_response_time}
        loss_probability: {self._loss_probability}
        """
