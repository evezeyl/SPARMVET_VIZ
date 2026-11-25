import polars as pl, warnings; warnings.filterwarnings("ignore")
from transformer.actions.modified import action_modif_filter
df=pl.DataFrame({"id":["a","b","c","d","e"],"x":[1.0,5.0,float("nan"),None,10.0],"n":[1,5,None,7,10]})
print("x =",df["x"].to_list())
for op,v in (("eq",5.0),("ne",5.0),("gt",5.0),("ge",5.0),("lt",5.0),("le",5.0),("in",[5.0]),("not_in",[5.0]),("between",[2.0,6.0])):
    r={}
    for na in ("remove","keep"):
        r[na]="".join(action_modif_filter(df.lazy(),{"column":"x","op":op,"value":v,"na":na}).collect()["id"].to_list())
    print(f"x {op:8s} {str(v):12s} remove->{r['remove']:6s} keep->{r['keep']}")
# integer thresholds on float and int columns, and ids
for spec in ({"column":"n","op":"gt","value":5.5,"na":"remove"},{"column":"x","op":"gt","value":5,"na":"remove"},{"column":"id","op":"in","value":[" a","A"],"na":"remove"},{"column":"id","op":"eq","value":1,"na":"remove"}):
    try: print(spec["column"],spec["op"],repr(spec["value"]),"->",action_modif_filter(df.lazy(),spec).collect()["id"].to_list())
    except Exception as e: print(spec["column"],spec["op"],repr(spec["value"]),"-> REFUSED:",str(e)[:110])
