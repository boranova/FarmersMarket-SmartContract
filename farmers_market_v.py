import requests
import json
import os

from dotenv import load_dotenv
from pathlib import Path

from web3.auto import w3

load_dotenv()

headers = {
    "Content-Type": "application/json",
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY"),
}

def initContract(contract_address, abi_file):
    with open(Path(abi_file)) as json_file:
        abi = json.load(json_file)

    print("Contract Address",
          contract_address)
    return w3.eth.contract(
        address=contract_address,abi=abi)


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
    
def registerVendor(address : str, vendor_information : dict):
    data = convertDataToJSON(vendor_information)
    ipfs_link = pinJSONtoIPFS(data)

    # call contract to create new vendor
    tx_hash = FarmersMarket.functions.registerVendor(address, ipfs_link)\
        .transact({"from": w3.eth.accounts[0]})

    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
  return receipt
  
    
def registerProduct (product_type, vendorID, URI, quantity, price):

  return receipt
  
def updateProduct (product_type, vendorID, URI, quantity, price):
  return receipt
  
def removeProduct (productID):
  return
  
def removeVendor (vendorID):
  return
  
def updateProductHistory (productID ,string):
  return
  
def MakePurchase( purchaseDate, deliveryDate, vendorID, productID, quantity)
  
def sales_report (vendorID):
  sales_filter = FarmersMarket.events.MakePurchase.createFilter(fromBlock="0x0", argument_filters={"vendorID": vendorID})
  return sales_filter.get_all_entries()

def vendor_report ():
  vendor_filter = FarmersMarket.events.registerVendor.createFilter(fromBlock="0x0")
  return vendor_filter.get_all_entries()
  
def product_history_report(productID):
  history = FarmersMarket.events.updateProductHistory.createFilter(fromBlock="0x0", argument_filters={"productID": productID})
  return history.get_all_entries()
  

  
