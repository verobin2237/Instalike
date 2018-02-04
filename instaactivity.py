import time
import random

# bot that records follows & comments & likes you receive.
class InstaActivity:
	def __init__(self, operation, repository, content_manager):
		self.operation = operation
		self.repository = repository
		self.content_manager = content_manager

		# instance stats
		self.follows = 0
		self.likes = 0

		# timing
		self.next_activity_check = 0
		
	# 1 - like
	# 2 - comment
	# 3 - follow

	def parse_activities(self):
		self.follows = 0
		self.likes = 0
		
		activities = self.content_manager.get_activity()
		if(len(activities) == 0):
			return
		for activity in activities:
			if (activity.type == 3):
				self.follows += 1
			if (activity.type == 1):
				self.likes += 1

	def act(self):
		if (self.next_activity_check < time.time()):
			self.parse_activities()
			self.update_timer()


	def update_timer(self):
		self.next_activity_check = time.time() + random.randint(100,120)
		self.get_stats()

	def get_stats(self):
		print('#######################################')
		print('--------------ACTIVITIES---------------')
		print('received follows: {0}'.format(self.follows))
		print('received likes: {0}'.format(self.likes))

		