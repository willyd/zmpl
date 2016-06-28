import types
from matplotlib import pyplot as _plt

# gather all pyplot module level functions
MODULE_LEVEL_FUNCTIONS = [a for a in dir(_plt) if type(getattr(_plt, a)) == types.FunctionType]