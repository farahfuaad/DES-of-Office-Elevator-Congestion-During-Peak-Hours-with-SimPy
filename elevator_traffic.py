import simpy
import random
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

# Simulation parameters
MAX_PASSENGERS = 10
FLOORS = 20
START_FLOOR = 1
SIMULATION_DURATION = 8 * 60  # 8 hours in minutes
NUM_ELEVATORS = 3

# Elevator state
elevators = [{'id': i + 1, 'current_floor': START_FLOOR, 'passengers': [], 'active_time': 0, 'distance_travelled': 0} for i in range(NUM_ELEVATORS)]
waiting_passengers = []
queue_length = []

# Logs for analysis
passenger_log = []
waiting_times = []
elevator_assignment_log = defaultdict(list)

# Passenger Generator
def generate_passenger():
    destination = random.randint(1, FLOORS)
    patience = random.uniform(3, 10)
    return destination, patience

# Passenger management functions
def add_passengers(env):
    while len(waiting_passengers) < MAX_PASSENGERS:
        destination, patience = generate_passenger()
        waiting_passengers.append((destination, patience, env.now))
        passenger_log.append((env.now, destination))
        print(f"{env.now:7.4f} Passenger added (Destination: Floor {destination}, Patience: {patience:.1f} mins). Waiting: {len(waiting_passengers)}")

# Elevator management functions
def assign_passengers_to_elevators(env):
    for elevator in elevators:
        while len(elevator['passengers']) < MAX_PASSENGERS and waiting_passengers:
            passenger = waiting_passengers.pop(0)
            elevator['passengers'].append(passenger)
            wait_time = env.now - passenger[2]
            waiting_times.append(wait_time)
            elevator_assignment_log[elevator['id']].append(passenger)
            print(f"{env.now:7.4f} Passenger assigned to Elevator {elevator['id']} (Floor: {passenger[0]})")

# Remove passengers from the elevator when they reach their destination
def remove_passengers(env, elevator):
    offboarding = [p for p in elevator['passengers'] if p[0] == elevator['current_floor']]
    for p in offboarding:
        elevator['passengers'].remove(p)
    if offboarding:
        print(f"{env.now:7.4f} Elevator {elevator['id']} - {len(offboarding)} passenger(s) got off at floor {elevator['current_floor']}. Remaining: {len(elevator['passengers'])}.")

# Move elevator to the target floor
def move_elevator(env, elevator, target_floor):
    if target_floor == elevator['current_floor']:
        print(f"{env.now:7.4f} Elevator {elevator['id']} already on floor {target_floor}.")
    elif target_floor > elevator['current_floor']:
        print(f"{env.now:7.4f} Elevator {elevator['id']} Going up...")
        for floor in range(elevator['current_floor'] + 1, target_floor + 1):
            yield env.timeout(1.5)
            elevator['active_time'] += 1.5
            elevator['distance_travelled'] += 1
            print(f"{env.now:7.4f} Elevator {elevator['id']} arrived at floor {floor}")
    else:
        print(f"{env.now:7.4f} Elevator {elevator['id']} Going down...")
        for floor in range(elevator['current_floor'] - 1, target_floor - 1, -1):
            yield env.timeout(1.5)
            elevator['active_time'] += 1.5
            elevator['distance_travelled'] += 1
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

#random.seed(42) uncomment if you want reproducible results

env = simpy.Environment()
for elevator in elevators:
    env.process(elevator_process(env, elevator))
env.process(elevator_system(env))
env.run(until=SIMULATION_DURATION)

# Analysis and Visualization
times = [log[0] for log in passenger_log]
destinations = [log[1] for log in passenger_log]

# Peak hour analysis
time_bins = [int(t // 60) for t in times]
time_counter = Counter(time_bins)

# Most visited floors
floor_counter = Counter(destinations)

# Total passengers
total_passengers = len(passenger_log)

# Plot peak hour chart
plt.figure(figsize=(10, 5))
plt.bar(list(time_counter.keys()), list(time_counter.values()), color='skyblue')
plt.xlabel('Hour of Day')
plt.ylabel('Number of Passengers')
plt.title('Passenger Arrival per Hour')
plt.xticks(range(0, 9))
plt.grid(True)
plt.savefig('peak_hour_chart.png')
plt.close()

# Plot most visited floors
plt.figure(figsize=(10, 5))
plt.bar(list(floor_counter.keys()), list(floor_counter.values()), color='lightgreen')
plt.xlabel('Floor Number')
plt.ylabel('Number of Visits')
plt.title('Most Visited Floors')
plt.xticks(range(1, FLOORS + 1))
plt.grid(True)
plt.savefig('visited_floors_chart.png')
plt.close()

# Additional Analysis
avg_waiting_time = sum(waiting_times) / len(waiting_times) if waiting_times else 0
elevator_utilization = [(e['id'], e['active_time'] / SIMULATION_DURATION * 100) for e in elevators]
avg_travel_distance = sum(e['distance_travelled'] for e in elevators) / total_passengers if total_passengers else 0
passenger_distribution = {eid: len(p_list) for eid, p_list in elevator_assignment_log.items()}

# Save analysis summary
summary_lines = [
    "\n--- Simulation Summary ---",
    f"Total number of passengers during simulation: {total_passengers}",
    f"Average waiting time: {avg_waiting_time:.2f} minutes",
    f"Average travel distance per passenger: {avg_travel_distance:.2f} floors",
    "Elevator Utilization Rates:"
]
for eid, util in elevator_utilization:
    summary_lines.append(f"  Elevator {eid}: {util:.2f}%")
summary_lines.append("Passenger Distribution per Elevator:")
for eid, count in passenger_distribution.items():
    summary_lines.append(f"  Elevator {eid}: {count} passengers")

# Print to terminal
for line in summary_lines:
    print(line)

print("Analysis complete. Charts and summary can be found in saved file.")