import sqlite3

class Database:
	def __init__(self, file):
		self.file = file
		conn = sqlite3.connect(self.file)
		c = conn.cursor()
		with conn:
			c.execute("CREATE TABLE IF NOT EXISTS subreddits (subreddit text, value integer)")
		c.execute("SELECT * FROM subreddits")
		self.database = set([k for k,v in c.fetchall()])
		self.count = len(self.database)

	def getValues(self):
		return self.database

	def getCount(self):
		return self.count

	def insertDB(self, key):
		x = ('{}'.format(key), 1)
		temp = sqlite3.connect(self.file)
		with temp:
			temp.cursor().execute("INSERT INTO subreddits VALUES (?, ?)", x)
		self.database.add(key)
		self.count += 1

	def removeDB(self, key):
		x = (key, 1)
		to_execute = "DELETE FROM subreddits WHERE subreddit = ('{}')".format(key)
		temp = sqlite3.connect(self.file)
		with temp:
			temp.cursor().execute(to_execute)
		self.database.remove(key)
		self.count -= 1