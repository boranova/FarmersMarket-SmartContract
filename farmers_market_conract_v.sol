pragma solidity ^0.5.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/drafts/Counters.sol";


contract FarmersMarket is ERC721{
    using Counters for Counters.Counter;
    
    struct product {
        string type;
        uint vendorID;
        string URI; 
        uint available_quantity;
        uint price;
    }
    
    struct vendor {
        string URI;
        address _address;
        
    }
    
    }
    
    Counters.Counter private productIDS;
    Counters.Counter private vendorIDS;
   
    
    // mapping token_id to asset
    mapping(uint => product) public products;
    mapping(uint => vendor) public vendors;
   
    
    event RegisterVendor(uint, string, address);
    event RegisterProduct(string ,uint, string, uint, uint);
    event MakePurchase();
    event RemoveVendor(uint);   //just need vendorID
    event RemoveProduct(uint); //just need productID
    
    constructor("Farmers Market", "FMD") public {
        
    }
 

 function registerVendor(address vendorAddress, string memory vendorURI) public returns(uint) {
        
        vendorIDS.increment();
        uint vendorID = vendorIDS.current();
        
        vendors[vendorID] = vendor(vendorURI, vendorAddress);
        
        emit registerVendor(vendorAddress, vendorURI);
        
        return vendorID;
    }


 function registerProduct (string type, uint vendorID, string memory URI, uint quantity, uint price) 
        public returns(uint)
    {
        productIDS.increment();
        uint productID = productIDS.current();
        
        products[productID] = product(type, vendorID, URI, quantity, price);
        
        emit registerProduct (type, vendorID, URI, qantity, price);
        
        return productID;
    }


  function updateProduct(uint productID, string type, uint vendorID, string memory URI, uint quantity, uint price)) public returns(uint){
        products[productID] = product(typeID, vendorID, URI, quantity, price);
        
        return productID;
    }
        

  function removeProduct(uint productID) public returns(uint) {
        _burn(productID);
        delete products[productID];
        return productID;
    }

  function MakePurchase(uint purchaseDate, uint deliveryDate, uint vendorID, uint productID, uint quantity) public returns(uint) ) {
      require(purchaseDate <= deliveryDate, "you cannot rent backwards in time");
      require(quantity < products[productID].quantity, "Out of stock");
      
      
      emit MakePurchase (purchaseDate, deliveryDate, vendorID, productID, quantity);
      
      return 
  }


