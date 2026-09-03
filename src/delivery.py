class Delivery:
    def __init__(self,trajectory,fps: float,run_up: int = 0,distance: int = 0):
        self.trajectory = trajectory
        self.fps = fps
        self.run_up = run_up
        self.distance = distance
        self.speed = self.calculate_speed()
    def calculate_speed(self):
        frame_duration: float = 1.0/self.fps
        velocities: list[float] = []
        euclidean_distance = lambda x1,x2,y1,y2: ((x1-x2)**2 + (y1-y2)**2)**0.5
        #iterate through all detections, find velocity for each
        for i in range(1,len(self.trajectory)):
            delta_dist = euclidean_distance(self.trajectory[i][0][0],self.trajectory[i-1][0][0],
                                            self.trajectory[i][0][1],self.trajectory[i-1][0][1])
            delta_time = (self.trajectory[i][1] - self.trajectory[i-1][1])*frame_duration
            #velocity = distance over time
            velocities.append(delta_dist/delta_time)
        return sum(velocities)/len(velocities)
    def __str__(self):
        return f"Delivery at {self.distance} from a {self.run_up} run-up: {self.speed} m/s"