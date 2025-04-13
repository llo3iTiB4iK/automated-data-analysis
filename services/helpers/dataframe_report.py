import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
from datetime import datetime, timezone

matplotlib.use('Agg')
pd.set_option('display.precision', 4)


class DataFrameReport(FPDF):

    def __init__(self):
        super().__init__()
        self.create_time: str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        self.add_font("Monospace-Unicode", style="", fname="fonts/MonospaceRegular-6ZWg.ttf")
        self.add_font("Monospace-Unicode", style="b", fname="fonts/MonospaceBold-zmP0.ttf")
        self.add_font("Monospace-Unicode", style="i", fname="fonts/MonospaceOblique-5meB.ttf")
        self.add_page()

    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(text="Data Analysis Report", center=True)
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"Generated: {self.create_time}", ln=True, align="R")
        self.cell(0, 0, "", "T")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 10)
        self.cell(w=0, text=f'Page {self.page_no()}', align='C')

    def add_text(self, text: str = "", monospaced: bool = False, style: str = "") -> None:
        if monospaced:
            self.set_font("Monospace-Unicode", style, 14)
        else:
            self.set_font("Times", style, 14)

        self.write(text=text+"\n")

    def add_heading(self, text: str = ""):
        self.ln(5)
        self.add_text(text="        " + text, style="B")
        self.ln(3)

    def add_series(self, s: pd.Series, title: str = "") -> None:
        self.add_dataframe(df=pd.DataFrame(s), title=title, col_names=False)

    def add_dataframe(self, df: pd.DataFrame, max_cols: int = 4, title: str = "", col_names: bool = True) -> None:
        if title:
            self.add_heading(text=title)

        def truncate_column_name(name: str, max_length: int = 14) -> str:
            return name if len(name) <= max_length else f"{name[:max_length//2-1]}...{name[-(max_length//2-2):]}"

        df = df.rename(columns={col: truncate_column_name(str(col)) for col in df.columns})

        for start in range(0, len(df.columns), max_cols):
            chunk: pd.DataFrame = df.iloc[:, start:start + max_cols]
            self.add_text(text=chunk.to_string(header=col_names)+"\n", monospaced=True)
        self.add_text()

    def add_plot(self, title: str = None) -> None:
        if title:
            plt.title(title)
        img_buf: BytesIO = BytesIO()
        plt.savefig(img_buf, dpi=200, bbox_inches='tight')
        self.image(img_buf, w=self.epw)
        img_buf.close()
        plt.close()

    def _add_subplots_row(self, plot_funcs: list, cols: int = 2, suptitle: str = None) -> None:
        fig, axes = plt.subplots(1, cols, figsize=(5 * cols, 5))
        if cols == 1:
            axes = [axes]
        for i, plot_func in enumerate(plot_funcs):
            plot_func(axes[i])
        for j in range(len(plot_funcs), cols):
            axes[j].set_xticks([])
            axes[j].set_yticks([])
            axes[j].set_facecolor('white')
        plt.tight_layout(pad=1.0)
        if suptitle:
            fig.suptitle(suptitle, fontsize=cols*7, fontweight='bold', y=1.05)
        self.add_plot()

    def add_subplots(self, plot_funcs: list, cols: int = 2, suptitle: str = None) -> None:
        self._add_subplots_row(plot_funcs[:cols], cols, suptitle)
        for i in range(cols, len(plot_funcs), cols):
            self._add_subplots_row(plot_funcs[i:i + cols], cols)

    def to_bytes(self) -> BytesIO:
        return BytesIO(self.output())
