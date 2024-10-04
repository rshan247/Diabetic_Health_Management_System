import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

# Constants for rapid and intermediate insulin
mu_rapid = 3  # Peak for rapid-acting insulin at 3 hours
sigma_rapid = 1  # Spread for rapid-acting insulin
mu_intermediate = 7  # Peak for intermediate-acting insulin at 7 hours
sigma_intermediate = 2  # Spread for intermediate-acting insulin
duration = 12  # Total duration of insulin action (in hours)

# Gaussian (bell curve) function for insulin utilization
def insulin_utilization(t, insulin_type, mu, sigma):
    return (insulin_type / (sigma * np.sqrt(2 * np.pi))) * np.exp(-((t - mu) ** 2) / (2 * sigma ** 2))

# Cumulative insulin utilization up to a specific time t1
def cumulative_insulin_utilization(t1, insulin_type, mu, sigma):
    result, _ = quad(insulin_utilization, 0, t1, args=(insulin_type, mu, sigma))
    return result

# Plot insulin utilization curve for each insulin type
def get_insulin_usage(total_units, input_time, chart=True):
    if input_time < 0:
        return 0
    # Generate time points
    time_points = np.linspace(0, duration, 1000)
    total_rapid = total_units * 0.3  # 30% of total insulin is rapid-acting
    total_intermediate = total_units * 0.7  # 70% of total insulin is intermediate-acting

    # Calculate insulin usage for rapid and intermediate insulin
    rapid_usage = [insulin_utilization(t, total_rapid, mu_rapid, sigma_rapid) for t in time_points]
    intermediate_usage = [insulin_utilization(t, total_intermediate, mu_intermediate, sigma_intermediate) for t in time_points]

    # Calculate cumulative insulin used at the given input time for both types
    rapid_used = cumulative_insulin_utilization(input_time, total_rapid, mu_rapid, sigma_rapid)
    intermediate_used = cumulative_insulin_utilization(input_time, total_intermediate, mu_intermediate, sigma_intermediate)

    # Total insulin used and remaining
    total_used = rapid_used + intermediate_used
    total_left = (total_rapid + total_intermediate) - total_used
    rapid_left = total_rapid - rapid_used
    intermediate_left = total_intermediate - intermediate_used


    if chart:
        # Plot for rapid-acting insulin
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.plot(time_points, rapid_usage, label='Rapid-acting Insulin Usage', color='b')
        plt.axvline(x=input_time, color='r', linestyle='--', label=f'Time = {input_time} hours')
        plt.fill_between(time_points[:int(input_time / duration * len(time_points))],
                         rapid_usage[:int(input_time / duration * len(rapid_usage))], color='orange', alpha=0.4,
                         label=f'Rapid Insulin Used ({rapid_used:.2f} units)')
        plt.title(f'Rapid-acting Insulin Utilization')
        plt.xlabel('Time (hours)')
        plt.ylabel('Insulin Usage Rate (units/hour)')
        plt.legend()
        plt.grid(True)

        # Plot for intermediate-acting insulin
        plt.subplot(1, 2, 2)
        plt.plot(time_points, intermediate_usage, label='Intermediate-acting Insulin Usage', color='g')
        plt.axvline(x=input_time, color='r', linestyle='--', label=f'Time = {input_time} hours')
        plt.fill_between(time_points[:int(input_time / duration * len(time_points))],
                         intermediate_usage[:int(input_time / duration * len(intermediate_usage))], color='orange', alpha=0.4,
                         label=f'Intermediate Insulin Used ({intermediate_used:.2f} units)')
        plt.title(f'Intermediate-acting Insulin Utilization')
        plt.xlabel('Time (hours)')
        plt.ylabel('Insulin Usage Rate (units/hour)')
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.show()

    return total_used
    # Print the results
    print(f"At {input_time} hours:")
    print(f"Rapid-acting insulin used: {rapid_used:.2f} units, remaining: {rapid_left:.2f} units")
    print(f"Intermediate-acting insulin used: {intermediate_used:.2f} units, remaining: {intermediate_left:.2f} units")
    print(f"Total insulin used: {total_used:.2f} units, total remaining: {total_left:.2f} units")

# Example: Enter the time to calculate and plot insulin utilization
if __name__ == "__main__":
    input_time = float(input("Enter the time (in hours) to check insulin utilization: "))
    get_insulin_usage(18, input_time, chart=True)



# while True:
#     input_time = float(input("Enter the time (in hours) to check insulin utilization (-1 to exit): "))
#     if input_time == -1:
#         break
#
#     # Plot the insulin usage and calculate for the input time
#     plot_insulin_curve(A, mu, sigma, duration, input_time, True)
