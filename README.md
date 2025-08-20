
# Free Chloride Concentration Calculator

This repository contains a Python-based desktop application for the **calculation of free chloride concentration (Cf)** in concrete materials, developed as part of an academic project.  
The tool implements a **Fourier-series analytical solution** for chloride ingress in a cubic domain, derived from established chloride transport models in cementitious materials.  
The application is designed to assist researchers and students in studying **chloride diffusion, binding phenomena, and durability analysis of reinforced concrete structures**.

---

## 🔬 Scientific Background
The ingress of chloride ions into concrete is a critical durability concern in reinforced concrete exposed to marine or saline environments.  
The **free chloride concentration (Cf)** at a specific position and time governs the risk of reinforcement corrosion.  

This tool computes **Cf(x,y,z,t)** in a cubic domain by solving a **multi-dimensional Fourier series expansion** of Fick’s second law, with automated series convergence controlled by a user-defined tolerance.  
The methodology is based on derivations adapted from X. Qiu, J. Yuan, W. Chen, X. Tan, G. Wu, and H. Tian (2024) [[1]](#references).

---

## ✨ Features
- **PyQt5-based GUI** for intuitive parameter input and visualization.  
- **Analytical Fourier-series solution** of Fick’s second law for chloride ingress in cubic domains.  
- **Adaptive truncation of series terms** with user-defined tolerance for efficient convergence.  
- **Vectorized computation** using NumPy for performance optimization.  
- **Real-time convergence plotting** (terms vs. concentration) using Matplotlib, updated asynchronously via QThread.  
- Supports **manual input** or **file-based input** (`.txt` / `.csv`) for batch calculations.  
- Outputs both **final chloride concentration** `C_xyz(t)` and the **number of Fourier terms used**.  


---

## ⚙️ Installation
Clone the repository:
```bash
git clone https://github.com/epidsc/Free-Chloride-Concentration-Calculator
cd Free-Chloride-Concentration-Calculator
````

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

Run the application:

```bash
python "Free Chloride Concentration Calculator.py"
```

### Input Parameters

* **L1, L2, L3** → Domain dimensions (cm)
* **x, y, z** → Spatial position (cm)
* **Cs** → Surface chloride concentration (%)
* **Cs0** → Initial chloride concentration (%)
* **Da** → Apparent diffusion coefficient (cm²/year)
* **t** → Exposure time (years)
* **Tolerance** → Convergence criterion (optional)

### File-based Input

Inputs can also be loaded from `.txt` or `.csv` with format:

```
L1=10
L2=15
L3=20
x=5
y=7
z=10
Cs=0.8
Cs0=0.1
Da=0.05
t=25
```

---

## 👥 Authors

* **U.Sanathanan** – GUI development, implementation, coding

* **Perera B.V.N.** – Mathematical derivations
* **Perera N.A.P.V.S.** – Mathematical derivations
* **Prabodha P.A.D.** – Mathematical derivations

---

## 🙏 Acknowledgments

We acknowledge **Dr. D.A.S. Amarasinghe** for academic supervision and guidance during this project.

---

## 📖 References

\[1]X. Qiu, J. Yuan, W. Chen, X. Tan, G. Wu, and H. Tian, “Effect of chloride binding and sulfate ion attack on the chloride diffusion in calcium sulfoaluminate-based material under seawater environment,” Journal of Materials Research and Technology, vol. 30, pp. 4261–4271, Apr. 2024, doi: https://doi.org/10.1016/j.jmrt.2024.04.139.
‌

---

## 📜 Citation

If you use this software in academic or technical work, please cite:

* **This repository** (see [CITATION.cff](CITATION.cff))
* **The original derivation source**: X. Qiu, J. Yuan, W. Chen, X. Tan, G. Wu, and H. Tian(2024)

---

### Demonstration video
https://github.com/user-attachments/assets/4263ed52-06b0-4763-85ae-c1de8cef885a

```


