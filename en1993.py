def _get_elong_tangent(temp: float,
                      fyT: float,
                      E0T: float) -> tuple[float, float, float, float]:
    """
    Python translation of `Steel01Thermal::getElongTangent`.

    Parameters
    ----------
    temp : float
        Current steel temperature [°C].
    fyT  : float
        Yield stress at 20 °C.
    E0T  : float
        Young’s modulus at 20 °C.

    Returns
    -------
    ET : float
        Tangent Young’s modulus at the supplied temperature.
    elong : float
        Thermal elongation strain (dimensionless).
    fy : float
        Yield stress at the supplied temperature.
    fp : float
        Peak stress at the supplied temperature.

    Raises
    ------
    ValueError
        If *temp* is outside the valid range [0 °C, 1200 °C].
    """
    # --- Temperature‑dependent mechanical properties (EN 1992‑1‑2, Class N) ---
    if   temp <= 100:
        fy  = fyT
        E0  = E0T
        fp  = fyT
    elif temp <= 200:
        fy  = fyT
        E0  = E0T * (1 - (temp - 100) * 0.1 / 100)
        fp  = fyT * (1 - (temp - 100) * (1 - 0.807) / 100)
    elif temp <= 300:
        fy  = fyT
        E0  = E0T * (0.9 - (temp - 200) * 0.1 / 100)
        fp  = fyT * (0.807 - (temp - 200) * (0.807 - 0.613) / 100)
    elif temp <= 400:
        fy  = fyT
        E0  = E0T * (0.8 - (temp - 300) * 0.1 / 100)
        fp  = fyT * (0.613 - (temp - 300) * (0.613 - 0.42) / 100)
    elif temp <= 500:
        fy  = fyT * (1 - (temp - 400) * 0.22 / 100)
        E0  = E0T * (0.7 - (temp - 400) * 0.1 / 100)
        fp  = fyT * (0.42 - (temp - 400) * (0.42 - 0.36) / 100)
    elif temp <= 600:
        fy  = fyT * (0.78 - (temp - 500) * 0.31 / 100)
        E0  = E0T * (0.6  - (temp - 500) * 0.29 / 100)
        fp  = fyT * (0.36 - (temp - 500) * (0.36 - 0.18) / 100)
    elif temp <= 700:
        fy  = fyT * (0.47 - (temp - 600) * 0.24 / 100)
        E0  = E0T * (0.31 - (temp - 600) * 0.18 / 100)
        fp  = fyT * (0.18 - (temp - 600) * (0.18 - 0.075) / 100)
    elif temp <= 800:
        fy  = fyT * (0.23 - (temp - 700) * 0.12 / 100)
        E0  = E0T * (0.13 - (temp - 700) * 0.04 / 100)
        fp  = fyT * (0.075 - (temp - 700) * (0.075 - 0.05) / 100)
    elif temp <= 900:
        fy  = fyT * (0.11 - (temp - 800) * 0.05 / 100)
        E0  = E0T * (0.09 - (temp - 800) * 0.0225 / 100)
        fp  = fyT * (0.05  - (temp - 800) * (0.05 - 0.0375) / 100)
    elif temp <= 1000:
        fy  = fyT * (0.06 - (temp - 900) * 0.02 / 100)
        E0  = E0T * (0.0675 - (temp - 900) * (0.0675 - 0.045) / 100)
        fp  = fyT * (0.0375 - (temp - 900) * (0.0375 - 0.025) / 100)
    elif temp <= 1100:
        fy  = fyT * (0.04 - (temp - 1000) * 0.02 / 100)
        E0  = E0T * (0.045 - (temp - 1000) * (0.045 - 0.0225) / 100)
        fp  = fyT * (0.025 - (temp - 1000) * (0.025 - 0.0125) / 100)
    elif temp <= 1200:
        fy  = fyT * (0.02 - (temp - 1100) * 0.02 / 100)
        E0  = E0T * (0.0225 - (temp - 1100) * 0.0225 / 100)
        fp  = fyT * (0.0125 - (temp - 1100) * 0.0125 / 100)
    else:
        raise ValueError("Temperature must be ≤ 1200 °C")

    # --- Temperature‑dependent thermal elongation (EN 1992‑1‑2) ---
    if   temp <= 20:
        thermal_elong = 1.52466e-20          # practically zero
    elif temp <= 750:
        thermal_elong = -2.416e-4 + 1.2e-5 * temp + 0.4e-8 * temp * temp
    elif temp <= 860:
        thermal_elong = 0.01100840
    elif temp <= 1200:
        thermal_elong = -0.00619160 + 2e-5 * temp
    else:
        # This path is unreachable because of the previous range check,
        # but left intentionally for completeness.
        raise ValueError("Temperature must be ≤ 1200 °C")

    ET    = E0
    elong = thermal_elong
    return ET, elong, fy, fp


class EN1993:
    def __init__(self, model):
        """
        materials is a list of integer material tags to update
        """
        self._model = model


        self._tags = {
            "fy": 1,
            "E": 2
        }
        model.parameter(self._tags["fy"])
        model.parameter(self._tags["E"])


    def init(self, **values):
        fy_tag = self._tags["fy"]
        E_tag = self._tags["E"]

        self._model.updateParameter(fy_tag, values["fy"])
        self._model.updateParameter(E_tag, values["E"])
        for tag in self._model.getEleTags(),:
            self._model.addToParameter(fy_tag, "element", tag, "allSections", "Fy")
            self._model.addToParameter(E_tag,  "element", tag, "allSections", "E")

    def update(self, temperature):
        fy_tag = self._tags["fy"]
        E_tag = self._tags["E"]

        fy = self._model.getParamValue(fy_tag)
        E = self._model.getParamValue(E_tag)

        E, elong, fy, fp = _get_elong_tangent(temperature, fy, E)

        self._model.updateParameter(fy_tag, fy)
        self._model.updateParameter(E_tag,  E)

if __name__ == "__main__":
    import xara
    import numpy as np
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    strain = {}
    stress = {}

    with open("fire.tcl") as f:
        script = f.read()


    for T_end in np.linspace(0, 1000, 6):
        strain[T_end] = []
        stress[T_end] = []
        # for force in np.arange(0, 5000000, 250000):
        for force in np.linspace(0, 2500e3, 10):
            print(f"Running T={T_end} °C, force={force:.2f} N ...")
            model = xara.Model(ndm=3, ndf=7)

            model.eval(f"set T_end {T_end}")
            model.eval(f"set force {force}")
            model.eval(script)

            therm = EN1993(model)
            therm.init(fy=250, E=210e3)
            therm.update(T_end)

            if model.analyze(1) != 0:
                break

            strain[T_end].append(model.eleResponse(1, "section", 1, "fiber", 0, 0, "strain")[0])
            stress[T_end].append(model.eleResponse(1, "section", 1, "fiber", 0, 0, "stress")[0])

        ax.plot(strain[T_end], stress[T_end], ".-", label=f"T = {T_end} °C")
    fig.legend()
    fig.savefig("0.png")
    plt.show()
