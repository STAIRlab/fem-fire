
import sys
import xara
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
from ec import EN1993

def test_a(script):

    strain = {}
    stress = {}
    for T_end in np.linspace(20, 400, 6):
        strain[T_end] = []
        stress[T_end] = []
        # for force in np.arange(0, 5000000, 250000):
        for force in np.linspace(10, 2500e3, 10):
            print(f"Running T={T_end} °C, force={force:.2f} N ...")
            model = xara.Model()

            model.eval(f"set T_end {T_end}")
            model.eval(f"set force {force}")
            model.eval(script)

            therm = EN1993(model, "EC3")
            therm.init(Fy=250, E=210e3)
            therm.update(T_end)

            if model.analyze(1) != 0:
                print("Analysis failed at ", model.getTime())
                break

            strain[T_end].append(model.eleResponse(1, "section", 1, "fiber", (0, 0), "strain")[0])
            stress[T_end].append(model.eleResponse(1, "section", 1, "fiber", (0, 0), "stress")[0])

    return stress, strain

def test_b(script):

    strain = defaultdict(list)
    stress = defaultdict(list)
        # for force in np.arange(0, 5000000, 250000):
    for force in np.linspace(10, 2500e3, 20):
        model = xara.Model()
        model.eval(f"set force {force}")
        model.eval(script)

        therm = EN1993(model, "EC3")
        therm.init(Fy=250, E=210e3)

        for T in np.linspace(20, 800, 50):
            # print(f"Running T={T_end} °C, force={force:.2f} N ...")

            therm.update(T)

            if model.analyze(1) != 0:
                print("Analysis failed at ", model.getTime())
                break

            strain[T].append(model.eleResponse(1, "section", 1, "fiber", (0, 0), "strain")[0])
            stress[T].append(model.eleResponse(1, "section", 1, "fiber", (0, 0), "stress")[0])
            # assert strain[T_end][-1] > 0

    return stress, strain

if __name__ == "__main__":
    fig, ax = plt.subplots()

    with open(sys.argv[1]) as f:
        script = f.read()


    stress, strain = test_b(script)

    for T_end in strain:
        ax.plot(strain[T_end], stress[T_end], ".-", label=f"T = {T_end} °C")
    fig.legend()
    plt.show()

