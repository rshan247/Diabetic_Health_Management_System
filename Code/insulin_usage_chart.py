import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

# Constants
A = 30  # Total insulin administered in units (e.g., 30 units)
mu = 5  # Peak time in hours (e.g., 5 hours)
sigma = 2  # Spread of the insulin action (standard deviation)
duration = 10  # Total duration of insulin action (in hours)


# Gaussian (bell curve) function for insulin utilization
def insulin_utilization(t, A, mu, sigma):
    return (A / (sigma * np.sqrt(2 * np.pi))) * np.exp(-((t - mu) ** 2) / (2 * sigma ** 2))


# Cumulative insulin utilization up to a specific time t1
def cumulative_insulin_utilization(t1, A, mu, sigma):
    result, _ = quad(insulin_utilization, 0, t1, args=(A, mu, sigma))
    return result


# Plot insulin utilization curve and show insulin used at a specific time
def plot_insulin_curve(A , mu, sigma, duration, input_time, chart = False):
    # Generate time points
    time_points = np.linspace(0, duration, 1000)
    # print(time_points)

    # Calculate insulin usage for each time point
    insulin_usage = [insulin_utilization(t, A, mu, sigma) for t in time_points]

    # Calculate cumulative insulin used at the given input time
    insulin_used = cumulative_insulin_utilization(input_time, A, mu, sigma)
    insulin_left = A - insulin_used
    if chart == False:
        return insulin_used
    else:
        plt.plot(time_points, insulin_usage, label='Insulin Usage Rate (Bell Curve)', color='b')

        # Mark the input time on the curve
        plt.axvline(x=input_time, color='r', linestyle='--', label=f'Time = {input_time} hours')
        plt.fill_between(time_points[:int(input_time / 10 * len(time_points))],
                         insulin_usage[:int(input_time / 10 * len(insulin_usage))], color='orange', alpha=0.4,
                         label=f'Insulin Used ({insulin_used:.2f} units)')

        # Show details of insulin used and remaining
        plt.text(input_time + 0.1, max(insulin_usage) / 2,
                 f'Insulin Used: {insulin_used:.2f} units\nInsulin Left: {insulin_left:.2f} units', fontsize=12)

        plt.title(f'Insulin Utilization Over {duration} Hours')
        plt.xlabel('Time (hours)')
        plt.ylabel('Insulin Usage Rate (units/hour)')
        plt.legend()
        plt.grid(True)

        plt.show()


# while True:
#     input_time = float(input("Enter the time (in hours) to check insulin utilization (-1 to exit): "))
#     if input_time == -1:
#         break
#
#     # Plot the insulin usage and calculate for the input time
#     plot_insulin_curve(A, mu, sigma, duration, input_time, True)
