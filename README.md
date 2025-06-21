# Discrete Event Simulation (DES) of Office Elevator Congestion During Peak Hours with SimPy

## Objectives
1.	To develop an Agent-Based Simulation (ABS) model that represents elevator usage and congestion in an office building during peak hours.
2.	To analyze and identify factors that contribute to elevator congestion during peak period such as morning arrival, lunch break and end of workday.
3.	To explore and test different elevator control strategies like optimized scheduling algorithms and grouping user by floor range to reduce congestion. 

## Simulation Design
### Scenario
#### Peak-Hour Context:
•	Simulates a high-rise office building with 20 floors during morning rush hour (8:00–9:00 AM).
•	Input Data: 
- Multiple Floor Selection: Passengers select their destination floors via input.
- Passenger arrival follows a random pattern, averaging 10–15 passengers per minute.
- Real-world traffic patterns, such as increased flow to floor 6 where the cafeteria is located.

### Agents
a.	Passenger:
  •	Attributes: 
    - Weight (in kilograms): This parameter ensures the elevator's weight capacity is not exceeded.
    - Patience Threshold (in seconds): Determines how long a passenger will wait in the queue before abandoning it and opting for stairs or another elevator.
    - Destination Floor: Assigned either randomly or based on survey data to reflect actual floor preferences.

  •	Behaviors: 
  - Autonomous Boarding Decisions: Passengers evaluate elevator capacity and current load before entering
  - Queue Management: If the wait time exceeds the passenger’s patience threshold, the agent leaves the queue.
  - Group travel: Colleagues move together, affecting elevator capacity and boarding behavior.

b.	Elevator:
  •	Attributes: 
    - Capacity (maximum weight or passenger count): Defines the elevator's operational limits
    - Current Load: Tracks the total weight or number of passengers currently inside the elevator, updating in real-time as passengers board or exit.
    - Speed (floors per second): Determines how quickly the elevator moves between floors, influencing overall system efficiency.
  •	Behaviors:
    - Weight management: The elevator rejects additional passengers if adding them would exceed its weight or capacity limits.
    - Floor stops: The elevator stops at floors where passengers request to exit or where waiting passengers meet boarding criteria.
    - Demand-Responsive Scheduling: During peak hours, the elevator may skip floors that are already at capacity or prioritize high-demand floors to optimize traffic flow.
