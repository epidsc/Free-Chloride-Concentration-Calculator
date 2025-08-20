import sys
import numpy as np
from math import sin,  pi
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,QHBoxLayout, QLineEdit,
    QPushButton, QMessageBox, QTabWidget,QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


def parse_inputs(required_fields, widgets):
    parsed = {}
    for key in required_fields:
        try:
            parsed[key] = float(widgets[key].text())
        except ValueError:
            raise ValueError(f"Invalid input for '{key}'")
    return parsed

def compute_cubic_term_single(n, m, p, x, y, z, L1, L2, L3, delta_C, Da, t):
    coeff = 64 * delta_C / (pi**3 * n * m * p)
    sine_product = sin(n * pi * x / L1) * sin(m * pi * y / L2) * sin(p * pi * z / L3)
    lambda_nmp = (n * pi / L1)**2 + (m * pi / L2)**2 + (p * pi / L3)**2
    decay = 0.0 if -Da * lambda_nmp * t < -700 else np.exp(-Da * lambda_nmp * t)
    return coeff * sine_product * decay

def parallel_sum_cubic(x, y, z, L1, L2, L3, Cs, Cs0, Da, t, max_index=15):
    delta_C = Cs0 - Cs
    n_vals = np.arange(1, max_index, 2)
    m_vals = np.arange(1, max_index, 2)
    p_vals = np.arange(1, max_index, 2)

    n, m, p = np.meshgrid(n_vals, m_vals, p_vals, indexing='ij')
    coeff = 64 * delta_C / (pi**3 * n * m * p)

    sin_nx = np.sin(n * pi * x / L1)
    sin_my = np.sin(m * pi * y / L2)
    sin_pz = np.sin(p * pi * z / L3)
    sine_product = sin_nx * sin_my * sin_pz

    lambda_nmp = (n * pi / L1)**2 + (m * pi / L2)**2 + (p * pi / L3)**2
    decay = np.exp(np.clip(-Da * lambda_nmp * t, -700, 0))

    terms = coeff * sine_product * decay
    return Cs + np.sum(terms), len(n_vals) * len(m_vals) * len(p_vals)

        
def auto_converge_cubic(x, y, z, L1, L2, L3, Cs, Cs0, Da, t, tol=1e-6, max_cap=31):
    prev = None
    curve = []
    for max_index in range(3, max_cap + 2, 2):  
        Cf, num_terms = parallel_sum_cubic(
            x, y, z, L1, L2, L3, Cs, Cs0, Da, t, max_index=max_index
        )
        curve.append((num_terms, Cf))
        if prev is not None and abs(Cf - prev) < tol:
            break
        prev = Cf
    return Cf, curve


class LiveCubicCalculationThread(QThread):
    append_point = pyqtSignal(int, float)        # For plot updates
    result_ready = pyqtSignal(float, int)        # Final Cf and term count

    def __init__(self, inputs, tol=1e-6):
        super().__init__()
        self.inputs = inputs
        self.tol = tol

    def run(self):
        x = self.inputs['x']
        y = self.inputs['y']
        z = self.inputs['z']
        L1 = self.inputs['L1']
        L2 = self.inputs['L2']
        L3 = self.inputs['L3']
        Cs = self.inputs['Cs']
        Cs0 = self.inputs['Cs0']
        Da = self.inputs['Da']
        t = self.inputs['t']

        prev = None
        for max_index in range(3, 33, 2):
            Cf, num_terms = parallel_sum_cubic(x, y, z, L1, L2, L3, Cs, Cs0, Da, t, max_index=max_index)
            self.append_point.emit(num_terms, Cf)
            if prev is not None and abs(Cf - prev) < self.tol:
                break
            prev = Cf

        self.result_ready.emit(Cf, num_terms)


# === GUI Application ===
class ChlorideApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Free Chloride Concentration Calculator")
        self.tabs = QTabWidget()

        self.tab_cubic = QWidget()
        self.tabs.addTab(self.tab_cubic, "Cubic")
        self.init_cubic_tab()

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)


    def init_cubic_tab(self):
        layout = QVBoxLayout()

        # --- Manual Form Layout with Horizontal Groups ---
        form_layout = QVBoxLayout()

        cub1_row = QHBoxLayout()
        self.cubic_inputs = {}
        for key, label in [('L1', 'Length in x (cm)'), ('L2', 'Length in y (cm)'), ('L3', 'Length in z (cm)')]:
            self.cubic_inputs[key] = QLineEdit()
            cub1_row.addWidget(QLabel(label + ":"))
            cub1_row.addWidget(self.cubic_inputs[key])
        form_layout.addLayout(cub1_row)

        cub2_row = QHBoxLayout()
        for key, label in [('x', 'Position x (cm)'), ('y', 'Position y (cm)'), ('z', 'Position z (cm)')]:
            self.cubic_inputs[key] = QLineEdit()
            cub2_row.addWidget(QLabel(label + ":"))
            cub2_row.addWidget(self.cubic_inputs[key])
        form_layout.addLayout(cub2_row)

        cub3_row = QHBoxLayout()
        for key, label in [('Cs', 'Surface Cl⁻ (%)'), ('Cs0', 'Initial Cl⁻ (%)'), ('Da', 'D₁ (cm²/year)')]:
            self.cubic_inputs[key] = QLineEdit()
            cub3_row.addWidget(QLabel(label + ":"))
            cub3_row.addWidget(self.cubic_inputs[key])
        form_layout.addLayout(cub3_row)

        cub4_row = QHBoxLayout()
        for key, label in [ ('t', 'Time (y)')]:
            self.cubic_inputs[key] = QLineEdit()
            cub4_row.addWidget(QLabel(label + ":"))
            cub4_row.addWidget(self.cubic_inputs[key])

        # Manual Tolerance
        self.cubic_tol_input = QLineEdit()
        self.cubic_tol_input.setPlaceholderText("e.g., 1e-6")
        cub4_row.addWidget(QLabel("Tolerance (optional):"))
        cub4_row.addWidget(self.cubic_tol_input)
        form_layout.addLayout(cub4_row)

        layout.addLayout(form_layout)

         # Load from File Button
        self.load_file_button = QPushButton("Load Inputs from File")
        self.load_file_button.clicked.connect(self.load_inputs_from_file)
        layout.addWidget(self.load_file_button)

        # --- Calculation Button ---
        self.cubic_button = QPushButton("Calculate Cf (Cubic)")
        self.cubic_button.clicked.connect(self.calculate_cubic)
        layout.addWidget(self.cubic_button)

        # --- Result Display ---
        self.cubic_result_label = QLabel("Result:")
        layout.addWidget(self.cubic_result_label)

        # --- Live Convergence Plot ---
        self.cubic_fig = Figure(figsize=(5, 5))
        self.cubic_ax = self.cubic_fig.add_subplot(111)
        self.cubic_ax.set_xlabel("Terms")
        self.cubic_ax.set_ylabel("Cf (%)")
        self.cubic_ax.set_title("Live Convergence Plot")
        self.cubic_ax.grid(True)

        self.cubic_canvas = FigureCanvas(self.cubic_fig)
        layout.addWidget(self.cubic_canvas)

        self.cubic_convergence_x = []
        self.cubic_convergence_y = []
        self.cubic_plot_line, = self.cubic_ax.plot([], [], marker='o')

        self.tab_cubic.setLayout(layout)

    def calculate_cubic(self):
        try:
            inputs = parse_inputs(list(self.cubic_inputs.keys()), self.cubic_inputs)
            tol_text = self.cubic_tol_input.text().strip()
            if tol_text:
                inputs['tol'] = float(tol_text)
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
            return

        self.cubic_convergence_x.clear()
        self.cubic_convergence_y.clear()
        self.cubic_plot_line.set_data([], [])
        self.cubic_ax.relim()
        self.cubic_ax.autoscale_view()
        self.cubic_canvas.draw()

        self.cubic_button.setEnabled(False)

        self.thread = LiveCubicCalculationThread(inputs, tol=inputs.get('tol', 1e-6))
        self.thread.append_point.connect(self.update_cubic_convergence_plot)
        self.thread.result_ready.connect(self.display_cubic_result)
        self.thread.result_ready.connect(lambda *_: self.cubic_button.setEnabled(True))
        self.thread.start()

    def display_cubic_result(self, value, terms):
        self.cubic_result_label.setText(f"Result: C_xyz(t) = {value:.6f}% | Terms: {terms}")
        self.cubic_button.setEnabled(True)


    def update_cubic_convergence_plot(self, term_count, cf_value):
        self.cubic_convergence_x.append(term_count)
        self.cubic_convergence_y.append(cf_value)
        self.cubic_plot_line.set_data(self.cubic_convergence_x, self.cubic_convergence_y)
        self.cubic_ax.relim()
        self.cubic_ax.autoscale_view()
        self.cubic_canvas.draw()

    def load_inputs_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Input File", "", "Text Files (*.txt *.csv);;All Files (*)")
        if not file_path:
            return

        input_fields = self.cubic_inputs

        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=')
                        key = key.strip()
                        value = value.strip()

                        if key in input_fields:
                            input_fields[key].setText(value)

            QMessageBox.information(self, "Success", "Input values loaded successfully from file.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load inputs:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ChlorideApp()
    win.show()
    sys.exit(app.exec_())
