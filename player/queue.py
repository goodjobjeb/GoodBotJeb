from collections import defaultdict

class QueueManager:
    def __init__(self):
        self.queues = defaultdict(list)

    def add(self, guild_id, item):
        self.queues[guild_id].append(item)

    def get_next(self, guild_id):
        return self.queues[guild_id].pop(0) if self.queues[guild_id] else None

    def has_next(self, guild_id):
        return bool(self.queues[guild_id])

    def clear(self, guild_id):
        self.queues[guild_id] = []

    def get_all(self, guild_id):
        return self.queues[guild_id]
