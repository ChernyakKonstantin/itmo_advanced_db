import io
from typing import Dict

import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


class PngDrawer:
    @staticmethod
    def draw(sensor_data: Dict[int, pd.DataFrame]) -> io.BytesIO:
        figure = PngDrawer.create_figure(sensor_data)
        png = PngDrawer.plot_png(figure)
        return png

    @staticmethod
    def create_figure(sensor_data: Dict[int, pd.DataFrame]) -> Figure:
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        for sensor_id, (data) in sensor_data.items():
            axis.plot(data["timestamp"], data["measurement"], label=f"Sensor {sensor_id}")
        axis.legend()
        axis.grid()
        axis.set_xlabel("Time")
        axis.set_ylabel("Measurment")
        return fig

    @staticmethod
    def plot_png(fig: Figure):
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return output
