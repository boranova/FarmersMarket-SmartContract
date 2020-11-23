import json
import os
import requests
from dotenv import load_dotenv
from pathlib import Path
#from web3.auto import w3
from web3 import Web3, HTTPProvider
from datetime import datetime as dt

load_dotenv()

# create a web3.py instance w3 by connecting to the local Ethereum node
w3 = Web3(HTTPProvider("http://localhost:8545"))

print(w3.isConnected())

# Initialize a local account object from the private key of a valid Ethereum node address
local_acct = w3.eth.account.from_key(os.getenv("ACCT_PRIVATE_KEY"))

# compile your smart contract first, then copy the whole 'FarmsMarket.json' file
abi = json.load(open('abi.json', 'r'))
bytecode = json.load(open("bytecode.json", 'r'))['object']

#truffleFile = json.load(open('artifacts/FarmersMarket.json'))
#abi = truffleFile['abi']
#bytecode = truffleFile['data']['bytecode']['object']

# Initialize a contract object with the smart contract compiled artifacts
contract = w3.eth.contract(bytecode=bytecode, abi=abi)

# build a transaction by invoking the buildTransaction() method from the smart contract constructor function
construct_txn = contract.constructor('FarmsMarket', 'FMD').buildTransaction({
    'from': local_acct.address,
    'nonce': w3.eth.getTransactionCount(local_acct.address),
    'gas': 5000000,
    'gasPrice': w3.toWei('21', 'gwei')})

# sign the deployment transaction with the private key
signed = w3.eth.account.sign_transaction(construct_txn, local_acct.key)

# broadcast the signed transaction to your local network using sendRawTransaction() method and get the transaction hash
tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
print(tx_hash.hex())

# collect the Transaction Receipt with contract address when the transaction is mined on the network
tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
print("Contract Deployed At:", tx_receipt['contractAddress'])
contract_address = tx_receipt['contractAddress']

# Initialize a contract instance object using the contract address which can be used to invoke contract functions
fm_contract = w3.eth.contract(abi=abi, address=contract_address)

# env variables

headers = {
    "Content-Type": "application/json",
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY"),
}

def convertDataToJSON(content):
    data = {"pinataOptions": {"cidVersion": 1}, "pinataContent": content}
    return json.dumps(data)

def pinJSONtoIPFS(json):
    r = requests.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        data=json,headers=headers
    )
    ipfs_hash = r.json()["IpfsHash"]
    return ipfs_hash


# 1. registerVendor
#
#    struct vendor {
#        string URI;
#        address _address;
#    }
def vendor_info():
    name = input("Enter the Name: ")
    phone = input("Enter a Contact Phone: ")
    
    vendor_object = {
            "name": name,
            "phone": phone,
    }

    return vendor_object

# registerVendor(address vendorAddress, string memory vendorURI) 
# public returns(uint)

def register_vendor(vendor_address:str):

    # use contact_info to create URI using pinata API
    vendor_object = vendor_info()
    data = convertDataToJSON(vendor_object)
    ipfs_link = pinJSONtoIPFS(data)

    vendor_id = fm_contract.functions.registerVendor(vendor_address, ipfs_link).call()

    # call contract to create new owner
    tx_hash = fm_contract.functions.registerVendor(
        vendor_address, ipfs_link)\
        .transact({"from": w3.eth.accounts[0]})
    
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    desc = fm_contract.functions.vendors(vendor_id).call()
     
    return desc, receipt

# 2. registerProduct
#
# registerProduct (string memory _type, uint vendorID, 
#                 string memory URI, uint quantity, uint price) 
#    public returns(uint)

def register_product(product_type:str, 
                     vendorID:int,  
                     quantity:int, 
                     price:int,
                     description:str):

    # use product_info to create URI using pinata API
    product_object = {
            "vendorID": vendorID,
            "description":description,
    }
    data = convertDataToJSON(product_object)
    ipfs_link = pinJSONtoIPFS(data)

    product_id = fm_contract.functions.registerProduct(
        product_type,
        vendorID,
        ipfs_link,
        quantity,
        price).call()

    # call contract to create new product
    tx_hash = fm_contract.functions.registerProduct(
        product_type,
        vendorID,
        ipfs_link,
        quantity,
        price)\
        .transact({"from": w3.eth.accounts[0]})

    receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    desc = fm_contract.functions.products(product_id).call()

    return desc, receipt

# 3. updateProduct
#    function updateProduct(uint productID, string memory product_type, uint vendorID, string memory URI, uint quantity, uint price) 
#    public returns(uint) 
def update_product(productID:int,
                   product_type:str,
                   vendorID:int,  
                   quantity:int, 
                   price:int,
                   description:str):
    
    # use product_info to create URI using pinata API
    product_object = {
            "vendorID": vendorID,
            "description":description,
    }
    data = convertDataToJSON(product_object)
    ipfs_link = pinJSONtoIPFS(data)

    # call contract to update vendor
    tx_hash = fm_contract.functions.updateProduct(
        productID,
        product_type,
        vendorID,
        ipfs_link,
        quantity,
        price)\
        .transact({"from": w3.eth.accounts[0]})

    receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    desc = fm_contract.functions.products(productID).call()

    return desc, receipt

# 4. removeProduct
#    function removeProduct(uint productID) public returns(uint)
def remove_product(productID:int):
    
    #call contract to remove product
    tx_hash = fm_contract.functions.removeProduct(
        productID)\
    .transact({"from": w3.eth.accounts[0]})
        
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    desc = fm_contract.functions.products(productID).call()

    return desc, receipt

# 5. removeVendor
#     function removeVendor(uint vendorID) public returns(uint)
def remove_vendor(vendorID:int):


    #call contract to remove product
    tx_hash = fm_contract.functions.removeVendor(
        vendorID)\
    .transact({"from": w3.eth.accounts[0]})
        
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    desc = fm_contract.functions.vendors(vendorID).call()    

    return desc, receipt

# 6. makePurchase
# function makePurchase(uint purchaseDate, uint deliveryDate, uint vendorID, uint productID, uint quantity) public payable returns(uint) 
def make_purchase(purchaseDate:str,
                   deliveryDate:str,
                   vendorID:int,  
                   productID:int, 
                   quantity:int,
                   purchase_price:int):

    # Convert start_date and end_date to datetime objects
    if not isinstance(purchaseDate, dt):
        purchaseDate = dt.strptime(purchaseDate, "%Y/%m/%d") # 1996/08/30
    if not isinstance(deliveryDate, dt):
        deliveryDate = dt.strptime(deliveryDate, "%Y/%m/%d")
    # Convert dates to unix timestamps
    purchaseDate = int(purchaseDate.timestamp())
    deliveryDate = int(deliveryDate.timestamp())

#    vendor_id = fm_contract.functions.makePurchase(
#        purchaseDate,
#        deliveryDate,
#        vendorID,  
#        productID, 
#        quantity).call({"value":purchase_price})

    #call contract and get the msg.value
    tx_hash = fm_contract.functions.makePurchase(
        purchaseDate,
        deliveryDate,
        vendorID,  
        productID, 
        quantity)\
    .transact({"from": w3.eth.accounts[0],"value":purchase_price})
        
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)

    desc = fm_contract.functions.products(productID).call()   

    return desc, receipt    

# 7. updateProductHistory
#   function updateProductHistory(uint productID, string memory URI) public
def update_producthistory(
    productID:int,
    historyURI:str):
    
    #write description input
    
    
    #convert historyURIstring to URI
    data = convertDataToJSON(historyURI)
    ipfs_link = pinJSONtoIPFS(data)
    
    #call contract to remove product
    tx_hash = fm_contract.functions.updateProductHistory(
        productID,
        ipfs_link)\
    .transact({"from": w3.eth.accounts[0]})
        
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    
    desc = fm_contract.functions.products(productID).call()

    return desc, receipt

# 8. returnPurchase
#   function returnPurchase(uint purchaseDate, uint deliveryDate, uint vendorID, uint productID, uint quantity, address payable customer_address) 
# public payable returns(uint)
def return_purchase(purchaseDate:str,
                   deliveryDate:str,
                   vendorID:int,  
                   productID:int, 
                   quantity:int,
                   purchase_price:int,
                   customer_address:str):

    # Convert start_date and end_date to datetime objects
    if not isinstance(purchaseDate, dt):
        purchaseDate = dt.strptime(purchaseDate, "%Y/%m/%d") # 1996/08/30
    if not isinstance(deliveryDate, dt):
        deliveryDate = dt.strptime(deliveryDate, "%Y/%m/%d")
    # Convert dates to unix timestamps
    purchaseDate = int(purchaseDate.timestamp())
    deliveryDate = int(deliveryDate.timestamp())


    #call contract and get the msg.value
    tx_hash = fm_contract.functions.returnPurchase(
        purchaseDate,
        deliveryDate,
        vendorID,  
        productID, 
        quantity,
        customer_address)\
    .transact({"from": w3.eth.accounts[0],"value":purchase_price})
        
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    
    desc = fm_contract.functions.products(productID).call()

    return desc, receipt 


# view funtions for testing
def getVendors(vendorId):
    
    desc = fm_contract.functions.vendors(vendorID).call()
    return desc

def getLatestVendor():
    ipfs_hash = fm_contract.functions.getLatestVendor().call()
    message = requests.get(f"https://cloudflare-ipfs.com/ipfs/{ipfs_hash}")
    return message.json()

def getVendorByID(vendor_id):
    ipfs_hash = fm_contract.functions.vendors(vendor_id).call()[0]
    message = requests.get(f"https://cloudflare-ipfs.com/ipfs/{ipfs_hash}")
    return message.json()

# get reports of market
def sales_report (vendorID):
    sales_filter = fm_contract.events.MakePurchase.createFilter(fromBlock="0x0", argument_filters={"vendorID": vendorID})
    return sales_filter.get_all_entries()

def vendor_report ():
    vendor_filter = fm_contract.events.RegisterVendor.createFilter(fromBlock="0x0")
    return vendor_filter.get_all_entries()

def product_report ():

    product_reg = fm_contract.events.RegisterProduct.createFilter(fromBlock="0x0")
    product_update = fm_contract.events.UpdateProduct.createFilter(fromBlock="0x0")
    #return product_filter.get_all_entries()
    return product_reg.get_all_entries()+product_update.get_all_entries()

def product_history_report(productID):
    history = fm_contract.events.UpdateProductHistory.createFilter(fromBlock="0x0", argument_filters={"productID": productID})
    return history.get_all_entries()

## testing

if __name__ == "__main__":


    print('''
    Would you like to: 

    1. Register a vendor 
    2. Remove a vendor
    3. Register a product 
    4. Update a product 
    5. Remove a product
    6. Update a product's history
    7. Make a purchase
    8. Make a return

    a. Get a sales report
    b. Get a record list of Registered vendors
    c. Get a record list of Registered products
    d. Get a product's history

    q. Quit
    ''')

    while True:
        print()
        option = input("Please enter your option: ")

        if option == 'q':

            break

        #1. register vendor
        if option == "1":
    #        vendor_address = "0xBF8AdA742BEB32e29Ee9a0d41Da23C3Ef4C6E2Cb"
            vendor_address = "0x8ae3f5d6d85cEE8E7F6e41Bad033fDF0e6239322"
            vendor_id, receipt = register_vendor(vendor_address)
            #vendor_count += 1
            print(vendor_id)

        #2. Remove Vendor
        if option == "2":
            vendor_id = input("Enter a vendor ID to remove vendor:")

            vendor, receipt = remove_vendor(int(vendor_id))
            #ipfs_hash = vendor[0]
            #message = requests.get(f"https://cloudflare-ipfs.com/ipfs/{ipfs_hash}")

            #print(message.json())
            print(vendor)
            
        #3. Register Product
        if option == "3":
            product_type = input("Enter the product type: ")
            vendorID = input("Enter the vendor ID: ")
            quantity = input("Enter the product quantity: ")
            price = input("Enter the product price: ")
            description = input("Enter the product description: ")

            product_id, receipt = register_product(product_type, 
                                       int(vendorID), 
                                       int(quantity), 
                                       int(price),
                                       description)
            print(product_id)

        # 4. Update a product 
        if option == "4":
            productID = input("Enter the productID: ")
            product_type = input("Enter the product type: ")
            vendorID = input("Enter the vendor ID: ")
            quantity = input("Enter the product quantity: ")
            price = input("Enter the product price: ")
            description = input("Enter the product description: ")

            desc, receipt = update_product(int(productID),
                                       product_type, 
                                       int(vendorID), 
                                       int(quantity), 
                                       int(price),
                                       description)
            print(desc)

        # 5. Remove a product
        if option == "5":
            productID = input("Enter the productID that you would like to remove: ")

            productID, receipt = remove_product(int(productID))

            print(productID)

        # 6. Update a product's history
        if option == "6":
            productID = input("Enter the productID: ")
            description = input("Enter the product event description: ")

            desc, receipt = update_producthistory(int(productID),
                                            description)

            print(desc)

        # 7. Make a purchase
        if option == "7":
            purchaseDate = input("Enter the date you would like to purchase: ")
            deliveryDate = input("Enter the date you would like it delivered: ")
            vendorID = input("Enter the vendorID you would like to buy from: ") 
            productID = input("Enter the productID you would like to purchase: ") 
            quantity = input("Enter the quantity you would like to purchase: ")
            purchase_price = input("Enter the product's price: ")

            vendorID, receipt = make_purchase(purchaseDate,
                                    deliveryDate,
                                    int(vendorID),
                                    int(productID),
                                    int(quantity),
                                    int(purchase_price))

            print(vendorID)

        # 8. Make a return
        if option == "8":
            purchaseDate = input("Enter the date you bought the product: ")
            deliveryDate = input("Enter the date the product was delivered on: ")
            vendorID = input("Enter the vendorID you want to return to: ") 
            productID = input("Enter the productID you want to return: ") 
            quantity = input("Enter the quantity you want to return: ")
            purchase_price = input("Enter the purchase price: ")
            customer_address = "0xcA9c9632aD0f42f43769586B744CE3aD18289979"

            desc, receipt = return_purchase(purchaseDate,
                                    deliveryDate,
                                    int(vendorID),
                                    int(productID),
                                    int(quantity),
                                    int(purchase_price),
                                    customer_address)

            print(desc)

        # a. Get a sales report
        if option == "a":
            vendorID = input("Enter the vendorID you would like to pull the report for: ")

            report = sales_report(int(vendorID))

            for i in range(len(report)):
                #ipfs_hash = report[i]['args']['URI']
                #message = requests.get(f"https://cloudflare-ipfs.com/ipfs/{ipfs_hash}")
                print(dict(report[i]['args']))


        # b. Get a list of vendors
        if option == "b":
            report = vendor_report()
            for i in range(len(report)):
                ipfs_hash = report[i]['args']['vendorURI']
                message = requests.get(f"https://cloudflare-ipfs.com/ipfs/{ipfs_hash}")
                print(message.json())

        # c. Get a list of products
        if option == "c":
            report = product_report()
            for i in range(len(report)):
                #ipfs_hash = report[i]['args']
                #message = requests.get(f"https://cloudflare-ipfs.com/ipfs/{ipfs_hash}")
                print(dict(report[i]['args']))


        # d. Get a product's history 
        if option == "d":
            productID = input("Enter the productID you would like to see the history for: ")

            report = product_history_report(int(productID))

            for i in range(len(report)):
                #print(report[i])
                ipfs_hash = report[i]['args']['URI']
                message = requests.get(f"https://cloudflare-ipfs.com/ipfs/{ipfs_hash}")
                print(message.json())