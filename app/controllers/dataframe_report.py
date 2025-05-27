from datetime import datetime, timezone
from io import BytesIO

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF  # noqa

from app.models.request.analysis_params import DocumentTheme

matplotlib.use('Agg')
pd.set_option('display.precision', 4)


class DataFrameReport(FPDF):

    def __init__(self, dpi: int = 200, theme: DocumentTheme = DocumentTheme.LIGHT, show_time: bool = True) -> None:
        super().__init__()
        self._dpi = dpi
        self._show_time = show_time
        self.create_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        if theme == DocumentTheme.DARK:
            self.set_page_background((0, 0, 0))
            self.set_text_color(255, 255, 255)
            self.set_draw_color(255, 255, 255)

        self.add_font("Monospace-Unicode", style="", fname="fonts/MonospaceRegular-6ZWg.ttf")
        self.add_font("Monospace-Unicode", style="b", fname="fonts/MonospaceBold-zmP0.ttf")
        self.add_font("Monospace-Unicode", style="i", fname="fonts/MonospaceOblique-5meB.ttf")

        self.add_page()

    def header(self) -> None:
        self.set_font('Arial', 'B', 15)
        self.cell(text="Data Analysis Report", center=True)
        if self._show_time:
            self.set_font('Arial', 'I', 10)
            self.cell(0, 10, f"Generated: {self.create_time}", align="R", ln=True)
        else:
            self.ln()
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(5)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font('Arial', 'I', 10)
        self.cell(w=0, text=f'Page {self.page_no()}', align='C')

    def add_text(self, text: str = "", monospaced: bool = False, style: str = "") -> None:
        if monospaced:
            self.set_font("Monospace-Unicode", style, 14)
        else:
            self.set_font("Times", style, 14)

        self.write(text=text+"\n")

    def add_heading(self, text: str = "") -> None:
        self.ln(5)
        self.add_text(text="        " + text, style="B")
        self.ln(3)

    def add_series(self, s: pd.Series, title: str = "") -> None:
        self.add_dataframe(df=pd.DataFrame(s), title=title, col_names=False)

    def add_dataframe(self, df: pd.DataFrame, title: str = "", col_names: bool = True, max_cols: int = 4,
                      max_col_width: int = 14) -> None:
        if title:
            self.add_heading(text=title)

        def truncate_column_name(name: str, max_length: int) -> str:
            return name if len(name) <= max_length else f"{name[:max_length//2-1]}...{name[-(max_length//2-2):]}"

        df = df.rename(columns={col: truncate_column_name(str(col), max_col_width) for col in df.columns})

        for start in range(0, len(df.columns), max_cols):
            chunk = df.iloc[:, start:start + max_cols]
            self.add_text(text=chunk.to_string(header=col_names)+"\n", monospaced=True)
        self.add_text()

    def add_plot(self, title: str = None) -> None:
        if title:
            plt.title(title)
        img_buf = BytesIO()
        plt.savefig(img_buf, dpi=self._dpi, bbox_inches='tight')
        self.image(img_buf, w=self.epw)
        img_buf.close()
        plt.close()

    def _add_subplots_row(self, plot_funcs: list[callable], cols: int = 2, suptitle: str = None) -> None:
        fig, axes = plt.subplots(1, cols, figsize=(5 * cols, 5))
        axes = axes if cols > 1 else [axes]

        for ax, func in zip(axes, plot_funcs):
            func(ax)

        for ax in axes[len(plot_funcs):]:
            ax.axis('off')

        if suptitle:
            fig.suptitle(suptitle, fontsize=cols*7, fontweight='bold', y=1.05)

        plt.tight_layout(pad=1.0)
        self.add_plot()

    def add_subplots(self, plot_funcs: list[callable], cols: int = 2, suptitle: str = None) -> None:
        self._add_subplots_row(plot_funcs[:cols], cols, suptitle)
        for i in range(cols, len(plot_funcs), cols):
            self._add_subplots_row(plot_funcs[i:i + cols], cols)

    def to_bytes(self) -> BytesIO:
        return BytesIO(self.output())
