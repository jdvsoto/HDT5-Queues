import simpy
import random
import statistics
import matplotlib.pyplot as plt

# ── Configurable parameters ──────────────────────────────────────────────────
RANDOM_SEED   = 42
NEW_PROCESSES = 25          # total processes to simulate
INTERVAL      = 10          # mean inter-arrival time (exponential)
RAM_CAPACITY  = 100         # total RAM units
CPU_CAPACITY  = 1           # number of CPUs
CPU_SPEED     = 3           # instructions executed per CPU time-unit
# ─────────────────────────────────────────────────────────────────────────────


def process(env, _name, ram, cpu, times):
    """Lifecycle of a single OS process."""
    arrival = env.now

    # ── NEW: request memory ──────────────────────────────────────────────────
    memory = random.randint(1, 10)
    yield ram.get(memory)

    # ── READY → RUNNING loop ─────────────────────────────────────────────────
    instructions = random.randint(1, 10)

    while instructions > 0:
        # Wait for a free CPU
        with cpu.request() as req:
            yield req

            # RUNNING: execute up to CPU_SPEED instructions in 1 time unit
            run = min(instructions, CPU_SPEED)
            yield env.timeout(1)
            instructions -= run

        # CPU released — decide next state
        if instructions <= 0:
            break                       # → TERMINATED

        chance = random.randint(1, 21)
        if chance == 1:
            # → WAITING (I/O), then back to READY
            yield env.timeout(random.randint(1, 5))
        elif chance == 2:
            pass                        # → READY immediately (just loop again)
        # any other value also goes back to READY (loop again)

    # ── TERMINATED: release memory ───────────────────────────────────────────
    yield ram.put(memory)
    times.append(env.now - arrival)


def run_simulation(num_processes, interval, ram_capacity, cpu_capacity, cpu_speed):
    """Run one simulation and return list of per-process completion times."""
    global CPU_SPEED
    CPU_SPEED = cpu_speed

    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    ram = simpy.Container(env, init=ram_capacity, capacity=ram_capacity)
    cpu = simpy.Resource(env, capacity=cpu_capacity)
    times = []

    def generate_processes():
        for i in range(num_processes):
            yield env.timeout(random.expovariate(1.0 / interval))
            env.process(process(env, f'P{i}', ram, cpu, times))

    env.process(generate_processes())
    env.run()
    return times


def simulate_scenario(counts, interval, ram_capacity=100, cpu_capacity=1, cpu_speed=3):
    """Return (avg_times, std_times) lists for each process count."""
    avgs, stds = [], []
    for n in counts:
        t = run_simulation(n, interval, ram_capacity, cpu_capacity, cpu_speed)
        avgs.append(statistics.mean(t))
        stds.append(statistics.stdev(t) if len(t) > 1 else 0)
        print(f"  n={n:>3}  avg={avgs[-1]:.2f}  std={stds[-1]:.2f}")
    return avgs, stds


# ── Main ──────────────────────────────────────────────────────────────────────
counts = [25, 50, 100, 150, 200]

# ── Task 1 & 2: vary arrival interval ────────────────────────────────────────
print("\n=== Task 1: interval=10 ===")
avg10, std10 = simulate_scenario(counts, interval=10)

print("\n=== Task 2a: interval=5 ===")
avg5, std5 = simulate_scenario(counts, interval=5)

print("\n=== Task 2b: interval=1 ===")
avg1, std1 = simulate_scenario(counts, interval=1)

# ── Task 3 & 4: optimisation strategies (interval=10 as baseline) ─────────────
print("\n=== Task 3a: RAM=200, interval=10 ===")
avg_ram200_10, _ = simulate_scenario(counts, interval=10, ram_capacity=200)
print("\n=== Task 3a: RAM=200, interval=5 ===")
avg_ram200_5, _  = simulate_scenario(counts, interval=5,  ram_capacity=200)
print("\n=== Task 3a: RAM=200, interval=1 ===")
avg_ram200_1, _  = simulate_scenario(counts, interval=1,  ram_capacity=200)

print("\n=== Task 3b: fast CPU (6 inst/unit), interval=10 ===")
avg_fcpu_10, _ = simulate_scenario(counts, interval=10, cpu_speed=6)
print("\n=== Task 3b: fast CPU (6 inst/unit), interval=5 ===")
avg_fcpu_5, _  = simulate_scenario(counts, interval=5,  cpu_speed=6)
print("\n=== Task 3b: fast CPU (6 inst/unit), interval=1 ===")
avg_fcpu_1, _  = simulate_scenario(counts, interval=1,  cpu_speed=6)

print("\n=== Task 3c: 2 CPUs, interval=10 ===")
avg_2cpu_10, _ = simulate_scenario(counts, interval=10, cpu_capacity=2)
print("\n=== Task 3c: 2 CPUs, interval=5 ===")
avg_2cpu_5, _  = simulate_scenario(counts, interval=5,  cpu_capacity=2)
print("\n=== Task 3c: 2 CPUs, interval=1 ===")
avg_2cpu_1, _  = simulate_scenario(counts, interval=1,  cpu_capacity=2)


