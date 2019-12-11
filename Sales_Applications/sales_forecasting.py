#!/usr/local/bin/python
import os,string,signal

__authon__ = 'Sayed'
# TODO :
# product class to have definations of the products and there pricing.
# Sales class to provide the functionality for selling the items and 
# calculating the total on sold items.


"""
doc : module helps to store the product information in conf file so that 
on change of the pricing and offers on the product should not require code changes

Based on the saved info calucate the total cost of sold items .
"""

class Products :

	""" 
		A class that contains all the informations about products and the available offers on the quantity of products.

		Marking the products to private and restricting the direct editing 
		Provides the Abstractions .
		If application is thread base it will save from deadlock in such editing cases by making the locks on functions.
	"""

	__products_dict = {}
	__offer_based_products= {}

	def __init__(self , conf_file ='') :
		""" Constructor to initialize the default values by calling the basic functions """	
		if not conf_file :
			conf_file = ('conf'+os.sep+'product_conf.conf')
		self.conf_file = conf_file
		self.populate_products()
		self.populate_offer_on_products()

	def get_product_values(self) :
		""" On runtime checks that products values are poplulated 
			if in case found empty calls the populate_products() 
		"""
		try:
			self.populate_products()
		except Exception as msg:
			print ("Exception in get_product_values ",msg)
		return self.__products_dict # helps the value to be retrieved outside the class and restrict direct access and modifications


	def get_product_offers(self) :
		""" On runtime checks that products offers values are poplulated 
			if in case found empty calls the populate_offer_on_products() 
		"""
		try:
			self.populate_offer_on_products()
		except Exception as msg:
			print ("Exception in get_product_offers ",msg)
		return self.__offer_based_products # helps the value to be retrieved outside the class and restrict direct access and modifications

	def populate_offer_on_products(self) :
		""" helps to populate the offers on the product 
			having data structures using tuples to achieve immutability 
			if new offers are updated again tuples should be replaced.
		"""
		try:
			try:
				available_offers = read_conf_file(self.conf_file , 'OFFERS_ON_PRODUCTS')
				if not available_offers :
					raise Exception('Products conf file not found') 
				self.set_product_offers(eval(available_offers))
			except Exception as e:
				self.set_product_offers({'A' : ( 3 , 130 ) , 'B' : (2 , 45 ) })
		except Exception as msg :
			print ("Exception in populate_offer_on_products",msg)		


	def populate_products(self) :
		""" helps to get the values from conf files else populate the basic requiremets based values"""
		try :
			try :
				available_products = read_conf_file(self.conf_file , 'AVAILABLE_PRODUCTS')
				if not available_products :
					raise Exception('No product found in conf')
				self.set_product_values(eval(available_products))
			except :
				self.set_product_values({'A' : 50 , 'B' : 30 , 'C' : 20 , 'D' : 15 })			
		except Exception as msg:
			print ("Exception in populating the products",msg)

	def set_product_values(self,updated_product_dict={}) :
		""" Setter to set values in private variables 
			helps to update the values of product if any new values is required to be updated.
		"""
		try :
			if isinstance(updated_product_dict , dict ) :
				self.__products_dict.update(updated_product_dict)
			# print ("self.products_dict >> ",self.__products_dict)
		except Exception as msg :
			print ("Exception in setting the products values",msg)

	def set_product_offers(self,updated_product_offers={}) :
		""" Setter to set values in private variables 
			helps to update the values of product if any new values is required to be updated.
		"""
		try :
			if isinstance(updated_product_offers , dict ) : 
				self.__offer_based_products.update(updated_product_offers)
		except Exception as msg :
			print ("Exception in setting the products values",msg)

	def show_products_and_offers(self):
		"""Helps to show the list of products with the available offers """
		try :
			if not self.__products_dict or not self.__offer_based_products :
				# Just to be on the safer side data should be populated if its empty :)
				self.populate_products()
				self.populate_offer_on_products()

			print("Items       Unit Price     Special Price")
			print("-"*45 , '\n')
			for pro in sorted(self.__products_dict.keys()) :
				is_offer_on_pro , offer_descr = tuple() ,''
				if self.__offer_based_products.get(pro) :
					is_offer_on_pro = self.__offer_based_products.get(pro)
					offer_descr = '{} for {} '.format(is_offer_on_pro[0] , is_offer_on_pro[1] )
				product_summary = '  {}          {}           {}'.format(pro,self.__products_dict.get(pro) , offer_descr )
				print(product_summary)
			print('')
		except Exception as msg :
			print ("Exception in setting the products values",msg)


class ProductSales(Products) :
	"""
	Product Sales class tells about the sales of the products which is inherited from the product class
	Jobs is to get all the sales and oredering and based on the sold product do_calculation function
	will calculate the total price of sold products.

	If any of the products  having the offers applicable then based on offers further calculations will
	be performed.
	"""
	def __init__(self , conf_file = '') :
		Products.__init__(self , conf_file )
		# self.sold_products = sold_products

	def do_calculation(self , sold_products ) :
		""" 
		performs the actual calculations on the sold products calls is_offer_applicable on each products as its 
		quantity based offers so counts of product solds is to be taken care.
		"""
		try:
			grouped_sold_products = {}
			product_pricing = self.get_product_values()
			total_cost = 0
			if sold_products :
				for sold_product in sold_products :
					if not grouped_sold_products.get(sold_product , '') :
						grouped_sold_products[sold_product] = []
					grouped_sold_products[sold_product].append(sold_product)

				for product_name,tot_pro_sold in grouped_sold_products.items() :
					product_actual_cost = product_pricing.get(product_name , 0) # assigning default 0 to avoid errors if product not available.
					if product_actual_cost :
						offer_applicable,offer_info = self.is_offer_applicable(product_name)
						if offer_applicable :
							offer_quantity ,offered_price = offer_info[0],offer_info[1]
							if len(tot_pro_sold) >= offer_quantity :
								in_offer = int(len(tot_pro_sold)/offer_quantity)
								tot_offered_price = in_offer*offered_price
								total_cost = total_cost + tot_offered_price
								if float(len(tot_pro_sold)) > float(in_offer*offer_quantity) :
									tot_left =len(tot_pro_sold[in_offer*offer_quantity:])*product_actual_cost
									total_cost =total_cost+tot_left
							else :
								total_cost =total_cost+len(tot_pro_sold)*product_actual_cost
						else :
							# no offer do simple multiplications.
							total_cost = total_cost+ int(len(tot_pro_sold)*product_actual_cost)
			print ("-"*45,"\n Total                        ",total_cost ,'\n', '-'*45 , '\n' )
		except Exception as msg:
			print ("Exception in calculting the products values",msg)

	def is_offer_applicable(self , product_name ) :
		"""checks the offers is applicable if so on how much quantity """
		try:
			offer_condition = ()
			offer_valid = False
			offer_dict = self.get_product_offers() # get the updated value on each sellings.
			if offer_dict.get(product_name,()) :
				offer_condition = offer_dict.get(product_name,())
				offer_valid = True
		except Exception as e:
			print ("Exception in checking  the products offers ",msg)
		return offer_valid , offer_condition


def read_conf_file(file_name , key_to_read) :
	""" a utility kind of function to anytime read the value from conf file
		file_name give the complete file path
		key_to_read which exactly key has to be read if empty give all the readed configuartions.
	"""
	try:
		with open(file_name) as product_conf :
			lines = product_conf.readlines()
		ret = {}

		def splitLeft(s, delimiter = ',') :
			i = s.find(delimiter)
			if i < 0 :
				return (s, "")
			return (s[:i], s[i + len(delimiter):])

		for line in lines :
			if line != "" and line[0] != '#':
				a, v = splitLeft(line, "=")
				ret[a.strip()] = v.strip()

		return ret.get(key_to_read)
	except Exception as msg :
		print ("Exception in reading the conf file ",msg)
		return

def main():
	try:
		conf_file = 'conf'+os.sep+'product_conf.conf'
		# initializing the class.
		product_sales = ProductSales(conf_file)
		while True :
			product_sales.show_products_and_offers()			
			inputs = input("Enter the products :  ")
			sold_products = inputs.strip()
			product_sales.do_calculation(sold_products)
			if not inputs :
				ans = input(" Do you want to exit Enter y for [yes] or press enter continue")
				if ans == 'y' : break
	except Exception as msg:
		pass
		# print ("Exception in executing main block msg : {} ".format(msg))

if __name__ == '__main__' :
	try:
		main()		
	except Exception as e:
		print ("Stopped the apps..",e)


