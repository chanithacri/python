import pandas as pd

# Load the text file into a DataFrame, specifying the index column as "Name"
df = pd.read_csv("hyperskill-dataset-97901992.txt.txt", index_col="Name")

# Print the first 10 rows of the DataFrame
print(df.head(10))
