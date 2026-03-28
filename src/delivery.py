class Delivery:
    def __init__(self,trajectory):
        self.trajectory = trajectory

"""
__init__(trajectory:int[]) d:Delivery
ext wr State:s
pre true
post s = s ~ union d
"""