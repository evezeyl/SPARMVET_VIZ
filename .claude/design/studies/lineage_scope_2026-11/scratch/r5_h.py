from r5_lib import *
from utils import remove_from_all as R
d=R.describe(raw0,"sample_id")
print(type(d)); print([a for a in dir(d) if not a.startswith("_")])
pl_=[p.place for p in d.places]; print(len(pl_),pl_)
print("rule of places on that list:",G.chosen_places_problem(pl_))
print("not reached:",[(n.table if hasattr(n,'table') else n) for n in d.not_reached])
