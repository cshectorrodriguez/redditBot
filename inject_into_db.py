from db import database

subreddits = set(["ActiveDeals", "ActualFrugalFashion", "DealShareUSA", "DiscountedMaleFashion", "buildapcsales", "deals", "freebies", "frugalmalefashion", "maximizing_money", "AppHookup"])

database = Database('database.db')

for x in subreddits:
	if x in database.getValues():
		print("r/{} is already in the database and was not inserted.".format(x))
		continue
	database.insertDB(x)
	print("r/{} was inserted into the database.".format(x))