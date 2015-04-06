import redis

class account_manager:
	redis_client=None
	
	@classmethod
	def get_redis_client(cls):
		#Use this as a factory to build a new client if it doesnt exist		
		if not cls.redis_client:
			cls.redis_client=redis.StrictRedis()
			return cls.redis_client
		else:
			return cls.redis_client
		
	def verify_user(self, unique_id):	
		#Check if the user exists in the db
		if not self.get_redis_client().exists("user:{}".format(unique_id)):
			print "User: {} does not exist".format(unique_id)
	
	def create_user(self):
		#Generate a unique id and print it
		id=self.get_redis_client().incr("unique_id_gen")
		self.get_redis_client().hset("user:{}".format(id),"balance",0)
	        print "Unique id created for you: {}".format(id)
		return id
			
	def get_balance(self, unique_id, print_balance=True):
		#Get the current balance for the user and print it if he exists
		#Get the balance for the unique id. Build the key to ask redis and ask redis
		balance = self.get_redis_client().hget("user:{}".format(unique_id),"balance")
		if print_balance:
			print "Current Balance: {}".format(balance)
		return balance
			
	def deposit_fund(self, unique_id, deposit):
		#Deposit funds(deposit) in that users account and print the updated balance
		self.verify_user(unique_id)
		#Update redis with the new balance
		user_hash = "user:{}".format(unique_id)
		if(deposit > 0):
			self.get_redis_client().hset(user_hash,"balance",int(self.get_balance(unique_id,print_balance=False))+deposit)
		else:
			print "deposit needs to be greater than 0";
			return
		self.get_balance(unique_id)	


	def withdraw_funds(self, unique_id, amount):
	        #Withdraw amount from that users account and print the updated balance
		#Get the balance for the unique id and substract it with the requested amount.
		user_hash = "user:{}".format(unique_id)
                if(amount > 0):
			cur_balance = int(self.get_redis_client().hget(user_hash,"balance"))
			if (amount > cur_balance):
				print "You are requesting {} more than what you have {}".format(amount,cur_balance)
				return
                        else:
				self.get_redis_client().hset(user_hash,"balance",cur_balance-amount)
                else:
                        print "withdraw amount needs to be greater than 0";
			return
		self.get_balance(unique_id)


account_manager_client=None

def build_account_manager_client():
	global account_manager_client
	if account_manager_client == None:
		account_manager_client = account_manager()
		return account_manager_client
	else:
		return account_manager_client

def options_loop(unique_id):
	while(True):
		option=raw_input("What do you want to do?(withdraw/checkBalance/deposit/signoff)")
		if option == "withdraw":
		        try:
				amount=int(raw_input("How much? Limit: 10000"))
				if (amount > 10000):
					print "Not allowed more than 10000"
					continue
			except ValueError, voe:
				print "Please give a valid input"
				continue
			build_account_manager_client().withdraw_funds(unique_id,amount)
		elif option == "checkBalance":
			build_account_manager_client().get_balance(unique_id)
		elif option == "deposit":
			try:
		        	amount=int(raw_input("How much? limit: 1000"))
				if (amount > 1000):
					print "Not allowed: less than 1000 please"
					continue
			except ValueError, voe:
				print "Please enter a valid input"
				continue
			build_account_manager_client().deposit_fund(unique_id,amount)
		elif option == "signoff":
			print "Thanks!"
			break
		else:
			print "I do not understand"		

#parse args from the command line
answer = raw_input("Are you a new user(y/n)")
if answer == "y":
	answer = raw_input("You want us to create a new PIN?(y/n)")
	if answer == "y":
		unique_id=build_account_manager_client().create_user()
		options_loop(unique_id)	
	else:
		print("Thanks for the time")
else:
	pin = raw_input("Pin please")
	build_account_manager_client().verify_user(pin)
	options_loop(pin)


