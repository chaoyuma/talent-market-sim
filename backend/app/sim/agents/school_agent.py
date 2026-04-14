from mesa import Agent


class SchoolAgent(Agent):
    def __init__(self, unique_id, model, name, major_capacity, school_type, profile):
        super().__init__(model)
        self.unique_id = unique_id
        self.name = name
        self.major_capacity = major_capacity
        self.school_type = school_type
        self.profile = profile

    def adjust_capacity(self):
        for major, stats in self.model.last_round_major_stats.items():
            employment_rate = stats.get("employment_rate", 0.5)

            if employment_rate > 0.75:
                self.major_capacity[major] = int(self.major_capacity.get(major, 10) * 1.1)
            elif employment_rate < 0.4:
                self.major_capacity[major] = max(5, int(self.major_capacity.get(major, 10) * 0.9))