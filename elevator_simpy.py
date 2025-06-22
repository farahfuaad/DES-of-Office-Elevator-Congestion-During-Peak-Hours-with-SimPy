import simpy
import random

# Simulation parameters
MAX_PASSENGERS = 10
FLOORS = 20
START_FLOOR = 1
SIMULATION_DURATION = 8 * 60  # 8 hours in minutes
NUM_ELEVATORS = 3

# Elevator state
elevators = [{'id': i + 1, 'current_floor': START_FLOOR, 'passengers': []} for i in range(NUM_ELEVATORS)]
waiting_passengers = []
queue_length = []

# Passenger Generator
def generate_passenger():
    destination = random.randint(1, FLOORS) # random floor between 1 and 20 floors
    patience = random.uniform(3, 10) # random patience between 3 and 10 minutes
    return destination, patience

# Passenger management functions
def add_passengers(env):
    while len(waiting_passengers) < MAX_PASSENGERS:
        destination, patience = generate_passenger() 
        waiting_passengers.append((destination, patience))
        print(f"{env.now:7.4f} Passenger added (Destination: Floor {destination}, Patience: {patience:.1f} mins). "
              f"Waiting: {len(waiting_passengers)}")

# Elevator management functions
def assign_passengers_to_elevators(env):
    for elevator in elevators:
        while len(elevator['passengers']) < MAX_PASSENGERS and waiting_passengers:
            passenger = waiting_passengers.pop(0) # get the first waiting passenger
            elevator['passengers'].append(passenger) # assign passenger to elevator
            print(f"{env.now:7.4f} Passenger assigned to Elevator {elevator['id']} (Floor: {passenger[0]})")

# Remove passengers from the elevator when they reach their destination
def remove_passengers(env, elevator):
    offboarding = [p for p in elevator['passengers'] if p[0] == elevator['current_floor']]
    for p in offboarding:
        elevator['passengers'].remove(p) 
    if offboarding:
        print(f"{env.now:7.4f} Elevator {elevator['id']} - {len(offboarding)} passenger(s) got off at floor {elevator['current_floor']}. "
              f"Remaining: {len(elevator['passengers'])}.")

# Move elevator to the target floor
def move_elevator(env, elevator, target_floor):
    if target_floor == elevator['current_floor']:
        print(f"{env.now:7.4f} Elevator {elevator['id']} already on floor {target_floor}.")
    elif target_floor > elevator['current_floor']:
        print(f"{env.now:7.4f} Elevator {elevator['id']} Going up...")
        for floor in range(elevator['current_floor'] + 1, target_floor + 1):
            yield env.timeout(1.5)
            print(f"{env.now:7.4f} Elevator {elevator['id']} arrived at floor {floor}")
    else:
        print(f"{env.now:7.4f} Elevator {elevator['id']} Going down...")
        for floor in range(elevator['current_floor'] - 1, target_floor - 1, -1):
            yield env.timeout(1.5)
            print(f"{env.now:7.4f} Elevator {elevator['id']} arrived at floor {floor}")
    elevator['current_floor'] = target_floor

# Elevator process to handle movement and passenger management
def elevator_process(env, elevator):
    while env.now < SIMULATION_DURATION:
        if elevator['passengers']:
            next_floors = sorted(set(p[0] for p in elevator['passengers']))
            for floor in next_floors:
                if env.now >= SIMULATION_DURATION:
                    break
                yield env.process(move_elevator(env, elevator, floor))
                remove_passengers(env, elevator)
        else:
            yield env.timeout(1)

# Main elevator system process
def elevator_system(env):
    print(f"Welcome to the Office Elevator System with {NUM_ELEVATORS} elevators.\n")
    while env.now < SIMULATION_DURATION:
        arrival_interval = 60 / random.randint(10, 15)
        yield env.timeout(arrival_interval)

        if len(waiting_passengers) < MAX_PASSENGERS:
            add_passengers(env)

        assign_passengers_to_elevators(env)
        queue_length.append(len(waiting_passengers))

# Run simulation
print('Elevator System Simulation with 3 Elevators')
random.seed(42)
env = simpy.Environment()

# Start elevator processes
for elevator in elevators:
    env.process(elevator_process(env, elevator))

# Start main system process
env.process(elevator_system(env))
env.run(until=SIMULATION_DURATION)