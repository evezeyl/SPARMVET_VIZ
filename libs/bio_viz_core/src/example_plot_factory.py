# Example: 
from plotnine import ggplot, aes, geom_bar, theme_minimal
import polars as pl

def draw_species_plot(df: pl.DataFrame, x_col: str, fill_col: str):
    """
    A generic factory function. 
    It doesn't care what the data is, as long as the columns exist.
    """
    # Plotnine logic
    plot = (
        ggplot(df.to_pandas(), aes(x=x_col, fill=fill_col)) 
        + geom_bar() 
        + theme_minimal()
    )
    return plot