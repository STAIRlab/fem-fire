import opensees.openseespy as ops
import os
import json
import numpy as np
import re
import matplotlib.pyplot as plt

# Set working directory
path = os.path.dirname(os.path.realpath(__file__))
os.chdir(path)

# File paths
model_path = os.path.join(path, "E_fy_pull.tcl")
results_json_path = os.path.join(path, "results_pull.json")
recorder_output_path = os.path.join(path, "E_fy_output/FiberStressStrain.out")
output_txt_path = os.path.join(path, "results_summary.txt")

# Read TCL file
with open(model_path, 'r') as f:
    tcl_content = f.read()

# Load existing results if available
if os.path.exists(results_json_path):
    results = json.load(open(results_json_path, 'r'))
else:
    results = {}

# Define temperature and pull force ranges
T_list = np.arange(100, 1100, 100)
pull_list = np.arange(0, 5000000, 250000)  # Reduce step size for denser data points

# Prepare output summary file
with open(output_txt_path, 'w') as f:
    f.write("Temperature,Stress,Strain,Stress/250\n")

# Main loop for simulation
for T in T_list:
    if f"T_{T:d}" in results and results[f"T_{T:d}"]["pull"] == pull_list.tolist():
        print(f"Skip T={T} ...")
        continue
    strain_list = []
    stress_list = []

    for pull in pull_list:
        print(f"Running T={T}, pull={pull:.2f} ...")
        # Update TCL content with current T and pull
        updated_tcl_content = re.sub(r"set T_end .*", f"set T_end {T:.2f};", tcl_content)
        updated_tcl_content = re.sub(r"set pull_force .*", f"set pull_force {pull:.2f};", updated_tcl_content)

        # Run OpenSees model
        model = ops.Model()
        model.eval(updated_tcl_content)
        model.wipe()

        # Read recorder output and extract stress/strain
        with open(recorder_output_path, 'r') as f:
            output = f.read()
        output_data = np.abs(np.loadtxt(recorder_output_path))

        # Append stress and strain data
        stress_list.append(output_data[1])  # Adjust index if needed
        strain_list.append(output_data[2])  # Adjust index if needed

    # Print the final stress and strain values for the current temperature
    final_stress = stress_list[-1]
    final_strain = strain_list[-1]
    stress_div_250 = final_stress / 250
    print(f"T={T}: Final Stress={final_stress:.2f}, Final Strain={final_strain:.6f}")

    # Write to summary file
    with open(output_txt_path, 'a') as f:
        f.write(f"{T},{final_stress:.2f},{final_strain:.6f},{stress_div_250:.6f}\n")

    # Update results
    results.update({
        f"T_{T:d}": {
            "pull": pull_list.tolist(),
            "stress": stress_list,
            "strain": strain_list
        }
    })

print("Simulation Done!")

# Save results to JSON
with open(results_json_path, 'w') as f:
    json.dump(results, f, indent=4)


# # Plot results
# fig, ax = plt.subplots()
# marker_list = ['o', 's', 'D', '^', 'v', 'p', 'P', '*', 'X', 'h']
# for T in T_list:
#     # Sort stress-strain data based on strain
#     sorted_indices = np.argsort(results[f"T_{T:d}"]["strain"])
#     sorted_data = {
#         "strain": np.array(results[f"T_{T:d}"]["strain"])[sorted_indices],
#         "stress": np.array(results[f"T_{T:d}"]["stress"])[sorted_indices]
#     }

#     sorted_strain = np.insert(sorted_strain, 0, 0.0)
#     sorted_stress = np.insert(sorted_stress, 0, 0.0) 

#     # Plot with markers
#     ax.plot(sorted_data["strain"], sorted_data["stress"],
#             label=f"T={T}", marker=marker_list.pop(0), markersize=4)

# # Configure plot appearance
# ax.grid()
# ax.set_xlim([0.0, 0.005])
# ax.set_ylim([0, 150])
# ax.legend()
# ax.set_xlabel("Strain")
# ax.set_ylabel("Stress")
# ax.set_title("Stress-Strain Curve")
# fig.savefig("stress-strain.png", dpi=300)
# plt.show()





fig, ax = plt.subplots(figsize=(8, 6))
marker_list = ['o', 's', 'D', '^', 'v', 'p', 'P', '*', 'X', 'h']

for T in T_list:
    sorted_indices = np.argsort(results[f"T_{T:d}"]["strain"])
    sorted_strain = np.array(results[f"T_{T:d}"]["strain"])[sorted_indices]
    sorted_stress = np.array(results[f"T_{T:d}"]["stress"])[sorted_indices]

    sorted_strain = np.insert(sorted_strain, 0, 0.0)  
    sorted_stress = np.insert(sorted_stress, 0, 0.0)  

    ax.plot(sorted_strain, sorted_stress, label=f"T={T}",
            marker=marker_list.pop(0), markersize=4)

# Configure plot appearance
ax.grid()
ax.set_xlim([0.0, 0.005])
ax.set_ylim([0.0, 500])
ax.legend(loc="center left", bbox_to_anchor=(1.05, 0.5), borderaxespad=0,fontsize=10, frameon=True, edgecolor='black')
plt.subplots_adjust(right=0.75)
ax.set_xlabel("Strain")
ax.set_ylabel("Stress")
ax.set_title("Stress-Strain Curve_Opensees")
fig.savefig("stress-strain.png", dpi=300)
plt.show()
