# Example: 
from plotnine import ggplot, aes, geom_bar, theme_minimal, scale_fill_manual
import polars as pl


# Example integration user pref
def draw_categorical_plot(df: pl.DataFrame, mapping: dict, user_prefs=None):
    """
    mapping: The dictionary returned by ConfigLoader.
    user_prefs: Future dictionary for colors, titles, etc.
    """
    # 1. Prepare data (Polars)
    # We select only the columns defined in our config
    plot_df = df.select(mapping["columns"]).to_pandas()
    
    # 2. Basic Plot Logic
    # Let's assume we plot the first column for this example
    target_col = mapping["columns"][0]
    
    p = (
        ggplot(plot_df, aes(x=target_col))
        + geom_bar()
        + theme_minimal()
    )
    
    # 3. FUTURE PROOFING: Inject user preferences if they exist
    if user_prefs and "colors" in user_prefs:
        p += scale_fill_manual(values=user_prefs["colors"])
        
    return p

# REVIEW BELLOW old examples, need to be adapted as df: pl.DataFrame, mapping: dict, user_prefs=None
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


def plot_amr_presence(df, amr_columns):
    """
    Generic AMR plotter. 
    'amr_columns' is a list provided by the Config Loader.
    """
    # Convert wide data to long (tidy) for Plotnine
    df_long = df.select(amr_columns).melt() 
    
    plot = (
        ggplot(df_long, aes(x="variable", fill="value"))
        + geom_bar(position="fill")
        + labs(x="Resistance Gene", y="Proportion")
    )
    return plot
