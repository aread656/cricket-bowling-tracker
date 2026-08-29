class Delivery:
    def __init__(self,trajectory,distance=None,run_up=None):
        self.trajectory = trajectory
        if distance:
            self.distance=distance
        if run_up:
            self.runup=run_up;

"""
__init__(trajectory:int[]) d:Delivery
ext wr State:s
pre true
post s = s ~ union d
"""