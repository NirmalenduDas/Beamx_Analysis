import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Beam Shear Force and Bending Moment Calculator")

# Beam properties
beam_type = st.selectbox("Select Beam Type", ["simply_supported", "cantilever"])
beam_length = st.number_input("Enter Beam Length (m)", min_value=1.0, value=10.0)
num_loads = st.number_input("Number of Loads", min_value=1, step=1, value=1)

loads = []

st.subheader("Load Details")
for i in range(num_loads):
    st.markdown(f"### Load {i+1}")
    load_type = st.selectbox(f"Type of Load {i+1}", ["point", "udl", "triangular"], key=f"type{i}")
    
    if load_type == "point":
        pos = st.number_input(f"Position of Point Load {i+1} (m)", min_value=0.0, max_value=beam_length, key=f"pos{i}")
        mag = st.number_input(f"Magnitude (kN)", key=f"mag{i}")
        loads.append({"type": "point", "position": pos, "magnitude": mag})
    
    elif load_type == "udl":
        start = st.number_input(f"Start of UDL {i+1} (m)", min_value=0.0, max_value=beam_length, key=f"start_udl{i}")
        end = st.number_input(f"End of UDL {i+1} (m)", min_value=start, max_value=beam_length, key=f"end_udl{i}")
        intensity = st.number_input("Intensity (kN/m)", key=f"intensity{i}")
        loads.append({"type": "udl", "start": start, "end": end, "intensity": intensity})
    
    elif load_type == "triangular":
        start = st.number_input(f"Start of Triangular Load {i+1} (m)", min_value=0.0, max_value=beam_length, key=f"start_tri{i}")
        end = st.number_input(f"End of Triangular Load {i+1} (m)", min_value=start, max_value=beam_length, key=f"end_tri{i}")
        peak = st.number_input("Peak Intensity (kN/m)", key=f"peak{i}")
        loads.append({"type": "triangular", "start": start, "end": end, "peak": peak})

# Calculate reactions
RA, RB = 0, 0
if beam_type == "simply_supported":
    total_force, total_moment = 0, 0
    for load in loads:
        if load["type"] == "point":
            total_force += load["magnitude"]
            total_moment += load["magnitude"] * (beam_length - load["position"])
        elif load["type"] == "udl":
            L = load["end"] - load["start"]
            F = load["intensity"] * L
            centroid = (load["start"] + load["end"]) / 2
            total_force += F
            total_moment += F * (beam_length - centroid)
        elif load["type"] == "triangular":
            L = load["end"] - load["start"]
            F = 0.5 * load["peak"] * L
            centroid = load["start"] + 2/3 * L
            total_force += F
            total_moment += F * (beam_length - centroid)
    RB = total_moment / beam_length
    RA = total_force - RB

elif beam_type == "cantilever":
    total_moment = 0
    for load in loads:
        if load["type"] == "point":
            RA += load["magnitude"]
            total_moment += load["magnitude"] * load["position"]
        elif load["type"] == "udl":
            L = load["end"] - load["start"]
            F = load["intensity"] * L
            centroid = (load["start"] + load["end"]) / 2
            RA += F
            total_moment += F * centroid
        elif load["type"] == "triangular":
            L = load["end"] - load["start"]
            F = 0.5 * load["peak"] * L
            centroid = load["start"] + 1/3 * L
            RA += F
            total_moment += F * centroid

# Calculate SFD and BMD
x_vals = np.linspace(0, beam_length, 1000)
shear_force = []
bending_moment = []

for x in x_vals:
    V, M = 0, 0

    if beam_type == "simply_supported":
        V += RA
        M += RA * x
    elif beam_type == "cantilever":
        V += RA
        M += RA * x

    for load in loads:
        if load["type"] == "point" and x >= load["position"]:
            V -= load["magnitude"]
            M -= load["magnitude"] * (x - load["position"])
        elif load["type"] == "udl":
            a, b, w = load["start"], load["end"], load["intensity"]
            if x >= a:
                x_eff = min(x, b)
                L = x_eff - a
                V -= w * L
                M -= w * L * (x - (a + L / 2))
        elif load["type"] == "triangular":
            a, b, w = load["start"], load["end"], load["peak"]
            if x >= a:
                x_eff = min(x, b)
                L = x_eff - a
                F = 0.5 * w * L
                centroid = a + (1/3) * L
                V -= F
                M -= F * (x - centroid)

    shear_force.append(V)
    bending_moment.append(M)

# Display Results
st.subheader("Reaction Forces")
st.write(f"RA = {RA:.2f} kN")
if beam_type == "simply_supported":
    st.write(f"RB = {RB:.2f} kN")

st.subheader("Shear Force Diagram (SFD) and Bending Moment Diagram (BMD)")
fig, ax = plt.subplots(2, 1, figsize=(12, 6))

# SFD Plot
ax[0].plot(x_vals, shear_force, color="blue")
ax[0].set_title("Shear Force Diagram")
ax[0].set_ylabel("Shear Force (kN)")
ax[0].grid(True)
ax[0].axhline(0, color='black', linewidth=0.5)

# BMD Plot
ax[1].plot(x_vals, bending_moment, color="red")
ax[1].set_title("Bending Moment Diagram")
ax[1].set_xlabel("Beam Length (m)")
ax[1].set_ylabel("Bending Moment (kN·m)")
ax[1].grid(True)
ax[1].axhline(0, color='black', linewidth=0.5)

st.pyplot(fig)
