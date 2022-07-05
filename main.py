# Main python file to run to search for pattern occurrences
# %%
import patterns
import matching_tools
import data
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# %%
datah = data.Database()
# Pattern (target sequence) to search for
pattern = np.log(patterns.SYM_TRIANGLE_BEAR)
acceptable_error = 0.0105
# Number of scaled timesteps to record ahead of a pattern match
scaled_steps_record = 10
# Scalings to apply to target pattern for comparisons
scales = patterns.LONG_SCALES
# Scale number for plotting purposes
plot_scale = np.lcm.reduce(scales)
# Maximum number of values to store per pattern match
max_steps = plot_scale * scaled_steps_record

everything_after = pd.DataFrame(columns = [i for i in range(max_steps + 1)])
for i, ticker in enumerate(datah.tickers):
    # Retrieve opening prices and apply log
    prices = datah.get_ticker(ticker)["open"]
    prices = matching_tools.apply_log(prices)

    # Find timestamps where pattern occurs
    matches = matching_tools.initial_diff_match(prices, pattern, 
        step_scalings=scales, diff_range=acceptable_error)

    # Find what happens after pattern occurance
    for scale in scales:
        afterwards = matching_tools.POI_afterwards(
            prices,
            # Multiple occurances can happen in nearby timesteps so purge them
            matching_tools.purge_date_repeats(matches[matches["scale"] == scale]), 
            steps_after=scaled_steps_record*scale
        )
        # apply "initial differencing"
        afterwards = afterwards.sub(afterwards.iloc[:, 0], axis=0)

        # apply upscaling so all results sequences are same length
        # (allows results to be plotted on top of each other later)
        afterwards = pd.DataFrame(
            matching_tools.horizontal_scale(
                afterwards.to_numpy(), 
                (scale, plot_scale)
            ),
            index=afterwards.index
        )
        # append results
        everything_after = pd.concat([everything_after, afterwards])

    # Show progress
    print(f"\r{i+1}/{len(datah.tickers)} completed", end="\r")

# %%
x_space = np.linspace(0, scaled_steps_record, max_steps+1)
# plot results
res = everything_after.T.to_numpy()
plt.plot(x_space, res[:, 1], color="gray", label="Individual views")
plt.plot(x_space, res[:, 2:], color="gray")
# plot average of results
avg = everything_after.mean(axis=0).to_numpy()
plt.plot(x_space, avg, color="blue", linewidth=3, linestyle="dashed", label="Average")
# plot pattern
pattern_scaled = matching_tools.horizontal_scale(pattern, (1, plot_scale))
pattern_scaled = pattern_scaled - pattern_scaled[0]
plt.plot(x_space[:len(pattern_scaled)], pattern_scaled, color="black", linewidth=4, label="Target pattern")
# plot bounding lines
plt.plot(x_space[:len(pattern_scaled)], pattern_scaled+acceptable_error, color="red", linewidth=1, 
    label=f"Accepted error (±{acceptable_error})")
plt.plot(x_space[:len(pattern_scaled)], pattern_scaled-acceptable_error, color="red", linewidth=1)
# label axis and toggle legend
plt.xlabel("Scaled timesteps")
plt.ylabel("Log (base e) returns from step 0")
plt.legend()
plt.show()
# %%
