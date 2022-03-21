# ll = list of lists
def flatten(ll) :
  if ll :
    return [i for l in ll for i in l]
  else :
    return None

