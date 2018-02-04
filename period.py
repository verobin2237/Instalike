import datetime
import time
from random import randint

class PeriodRandomizer:
	def __init__(self, configuration):
		self.configuration = configuration
		# 0 - 23 format
		self.from_hour = self.configuration.botting_start_hour
		self.to_hour = self.configuration.botting_end_hour

		self.from_time = None
		self.to_time = None

		self.work_for = 6 * 60 # means bot will be working for a total of # minutes

		# periods
		self.min_periods = 2
		self.max_periods = 4

		# in minutes
		self.min_period_length = 30
		self.max_period_length = 0
		self.actual_length = 0
		self.require_login = False # require login after longer period of work; False - we start off as logged in.

		self.periods = []

		# timing
		self.next_info_print = 0

	def randomize(self):
		# working whole time or for certain amount of time. No need to generate random periods.
		if(self.configuration.bot_work_whole_time):
			return

		self.periods = []

		now = datetime.datetime.now()
		self.from_time = datetime.datetime(now.year, now.month, now.day, self.from_hour)
		self.to_time = datetime.datetime(now.year, now.month, now.day, self.to_hour)

		minute_len = (self.to_time - self.from_time).seconds / 60
		if (self.work_for > minute_len):
			self.periods.append(Period(self.from_time, self.to_time)) # work whole time
			return

		no_of_periods = randint(self.min_periods, self.max_periods)
		while(len(self.periods) < no_of_periods):
			start_minute = randint(0, minute_len)
			period_len = randint(self.min_period_length, self.work_for / (no_of_periods - 1))
			if (len(self.periods) == no_of_periods - 1):
				period_len = self.work_for - self.actual_length

			if (period_len < self.min_period_length):
				period_len = self.min_period_length

			start_here = self.from_time + datetime.timedelta(minutes = start_minute)
			stop_here = self.from_time + datetime.timedelta(minutes = start_minute + period_len)

			# if (((self.to_time - stop_here).seconds / 60) < self.min_period_length):
			# 	continue
			# if (((start_here - self.from_time).seconds / 60) < self.min_period_length):
			# 	continue

			period_proposition = Period(start_here, stop_here)

			if (len(self.periods) == 0):
				self.periods.append(period_proposition)
				self.actual_length += period_proposition.get_length()
				continue

			valid = True
			for period in self.periods:
				if (period_proposition.during(period)):
					valid = False
					break

			if (valid):
				self.periods.append(period_proposition)
				self.actual_length += period_proposition.get_length()

		self.remove_late_periods()

	def remove_late_periods(self):
		valid_periods = []
		for period in self.periods:
			if (period.restarts_in() >= 0 or period.is_active()):
				valid_periods.append(period)

		self.periods = valid_periods

	def should_relog(self):
		return self.require_login

	def logged(self):
		self.require_login = False

	def is_workday(self):
		now = datetime.datetime.now()
		self.from_time = datetime.datetime(now.year, now.month, now.day, self.from_hour)
		self.to_time = datetime.datetime(now.year, now.month, now.day, self.to_hour)
		if(now > self.from_time and now < self.to_time):
			return True
		else:
			if (self.next_info_print < time.time()):
				print('Bot will work from {0}'.format(self.from_time))
				self.next_info_print = time.time() + 60
			return False

	def is_active_period(self):
		if (len(self.periods) == 0):
			if(self.from_time.day != datetime.datetime.now().day):
				self.randomize()
			else:
				self.require_login = True
				if (self.next_info_print < time.time()):
					print('work for day done, wait till midnight for next periods.')
					self.next_info_print = time.time() + 60
				return False

		# print info about bot restart
		for period in self.periods:
			if (period.is_active()):
				return True

		if (self.next_info_print < time.time()):
			print('bot restarts in {0:.0f} minutes'.format(self.restarts_in_s() / 60))
			self.next_info_print = time.time() + 60

		return False

	def is_active(self):
		# working whole time, active.
		if(self.configuration.bot_work_whole_time):
			if(self.configuration.bot_work_at_day):
				return self.is_workday()
			else:
				return True
		return self.is_active_period()

	def restarts_in_s(self):
		now = datetime.datetime.now()
		time_diff = (self.to_time - now).seconds
		for period in self.periods:
			start_t = period.get_start_time()
			period_diff = (start_t - now).seconds
			if (time_diff > period_diff):
				time_diff = period_diff
		return time_diff

	def info(self):
		if(self.configuration.bot_work_whole_time):
			print('working whole time.')
			return

		print('time periods, total: {0:.0f} minutes'.format(self.actual_length))

		for period in self.periods:
			period.get_times()


class Period:
	def __init__(self, from_time, to_time):
		self.start_time = from_time
		self.end_time = to_time

	def is_active(self):
		now = datetime.datetime.now()
		if (now > self.start_time and now < self.end_time):
			return True
		return False

	def during(self, period):
		if (self.start_time >= period.start_time and self.start_time <= period.end_time):
			return True
		if (self.end_time >= period.start_time and self.end_time <= period.end_time):
			return True
		if (self.start_time <= period.start_time and self.end_time >= period.end_time):
			return True
		return False

	def get_length(self):
		return (self.end_time - self.start_time).seconds / 60

	def get_start_time(self):
		return self.start_time

	def restarts_in(self):
		return self.start_time.hour - datetime.datetime.now().hour

	def get_times(self):
		print('from {0} to {1}, minutes: {2}, active: {3}, wait for {4} hours'.format(self.start_time, self.end_time, self.get_length(), self.is_active(), self.restarts_in()))
