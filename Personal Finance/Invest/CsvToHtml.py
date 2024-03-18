import pandas as pd 
#"C:\Users\ckraft\Desktop\My Experiments\Personal Use\Portfolio\OnBalanceVolume_Ranked.csv"
csv_file = pd.read_csv(r"C:\Users\ckraft\Desktop\My Experiments\Personal Use\Portfolio\OnBalanceVolume_Ranked.csv")
csv_file.to_html(r"C:\Users\ckraft\Desktop\My Experiments\Personal Use\Portfolio\OnBalanceVolume_Ranked.html") 

html_file = csv_file.to_html()