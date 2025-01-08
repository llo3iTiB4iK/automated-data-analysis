import matplotlib.pyplot as plt
import matplotlib
import io

matplotlib.use('Agg')


def generate_plot_to_bytesio(plot_func: callable) -> io.BytesIO:
    plot_func()
    buf: io.BytesIO = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()
    return buf
