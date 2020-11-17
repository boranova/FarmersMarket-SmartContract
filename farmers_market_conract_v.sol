pragma solidity ^0.5.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/drafts/Counters.sol";


contract FarmersMarket is ERC721{
    using Counters for Counters.Counter;
    
    address payable public MarketOwner = msg.sender;
    
    struct product {
        string product_type;
        uint vendorID;
        string URI; 
        uint quantity;
        uint price;
    }
    
    struct vendor {
        string URI;
        address payable _address;
        
    }
    
    Counters.Counter private productIDS;
    Counters.Counter private vendorIDS;
   
    
    // mapping token_id to asset
    mapping(uint => product) public products;
    mapping(uint => vendor) public vendors;
   
    
    event RegisterVendor(address, string);
    event RegisterProduct(string ,uint, string, uint, uint);
    event MakePurchase(uint, uint, uint, uint, uint);
    event RemoveVendor(uint);   //just need vendorID
    event RemoveProduct(uint); //just need productID
    event UpdateProductHistory(uint, string);
    
    constructor(string memory name, string memory symbol) public {
    
    }
 

 function registerVendor(address payable vendorAddress, string memory vendorURI) public returns(uint) {
        
        vendorIDS.increment();
        uint vendorID = vendorIDS.current();
        
        vendors[vendorID] = vendor(vendorURI, vendorAddress);
        
        emit RegisterVendor(vendorAddress, vendorURI);
        
        return vendorID;
    }


 function registerProduct (string memory product_type, uint vendorID, string memory URI, uint quantity, uint price) 
        public returns(uint)
    {
        productIDS.increment();
        uint productID = productIDS.current();
        
        products[productID] = product(product_type, vendorID, URI, quantity, price);
        
        emit RegisterProduct (product_type, vendorID, URI, quantity, price);
        
        return productID;
    }


  function updateProduct(uint productID, string memory product_type, uint vendorID, string memory URI, uint quantity, uint price) public returns(uint) {
        products[productID] = product(product_type, vendorID, URI, quantity, price);
        
        return productID;
    }
        

  function removeProduct(uint productID) public returns(uint) {
        _burn(productID);
        delete products[productID];
        return productID;
    }

  function makePurchase(uint purchaseDate, uint deliveryDate, uint vendorID, uint productID, uint quantity) public payable returns(uint)  {
      require(purchaseDate <= deliveryDate, "Date must be in the future");
      require(quantity < products[productID].quantity, "Out of stock");
      require(quantity * products[productID].price == msg.value, "Price and Quantity Error");
      
      
      vendors[vendorID]._address.transfer(msg.value);
      
      emit MakePurchase (purchaseDate, deliveryDate, vendorID, productID, quantity);
      
      return vendorID;
  }
  
  function updateProductHistory(uint productID, string memory URI) public {
      
      emit UpdateProductHistory(productID, URI);
      
  }
}
