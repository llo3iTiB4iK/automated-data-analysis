import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
from datetime import datetime

matplotlib.use('Agg')


class DataFrameReport(FPDF):

    def __init__(self):
        super().__init__()
        self.create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.add_page()

    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(text="Data Analysis Report", center=True)
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"Generated on: {self.create_time}", ln=True, align="R")
        self.cell(0, 0, "", "T")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 10)
        self.cell(w=0, text=f'Page {self.page_no()}', align='C')

    def add_text(self, text: str = "", monospaced: bool = False) -> None:
        if monospaced:
            self.set_font("Courier", size=12)
        else:
            self.set_font("Times", size=14)

        self.write(text=text+"\n")

    def add_series(self, s: pd.Series, title: str = "") -> None:
        self.add_dataframe(df=pd.DataFrame(s), title=title, col_names=False)

    def add_dataframe(self, df: pd.DataFrame, max_cols: int = 4, title: str = "", col_names: bool = True) -> None:
        if title:
            self.add_text(text='\n\n'+title)
        for start in range(0, len(df.columns), max_cols):
            chunk: pd.DataFrame = df.iloc[:, start:start + max_cols]
            self.add_text(text='\n'+chunk.to_string(header=col_names), monospaced=True)
        self.add_text()

    def add_plot(self) -> None:
        img_buf: BytesIO = BytesIO()
        plt.savefig(img_buf, dpi=200, bbox_inches='tight')
        self.image(img_buf, w=self.epw)
        img_buf.close()

    def to_bytes(self) -> BytesIO:
        return BytesIO(self.output())
