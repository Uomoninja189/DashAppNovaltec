import funzioni
import pandas as pd

data=funzioni.leggi_excel(2025)
print(data['CATEGORIA'].unique())

