pragma solidity ^0.5.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/drafts/Counters.sol";


contract FarmersMarket is ERC721{
    using Counters for Counters.Counter;
    
    struct product {
        uint typeID;
        uint vendorID;
        string URI; 
        bool isReady;
        uint quantity;
    }
    
    struct vendor {
        string URI;
        address _address;
    }
    
    Counters.Counter private productIDS;
    Counters.Counter private vendorIDS;
   
    
    // mapping token_id to asset
    mapping(uint => product) public products;
    mapping(uint => vendor) public vendors;
   
    event RegisterVendor(uint, string);
    event RegisterProduct(uint ,uint, string, bool);
    event MakePurchase(uint, uint, uint, uint, uint);
    event RemoveVendor(uint);   //just need vendorID
    event RemoveProduct(uint); //just need productID
    
    constructor(string memory name, string memory symbol) public {}
    
    function registerVendor(address vendorAddress, string memory vendorURI) public returns(uint) {
        
        vendorIDS.increment();
        uint vendorID = vendorIDS.current();
        
        vendors[vendorID] = vendor(vendorURI, vendorAddress);
        
        emit RegisterVendor(vendorID, vendorURI);
        
        return vendorID;
    }
    
    function getLatestVendor() public view returns(string memory) {
        uint vendor_id = vendorIDS.current();

        return vendors[vendor_id].URI;
    }
    
    function registerProduct (uint typeID, uint vendorID, string memory productURI, bool isReady) 
    public returns(uint) {
            
        productIDS.increment();
        uint productID = productIDS.current();
        
        products[productID] = product(typeID, vendorID, productURI, isReady, 1);
        
        emit RegisterProduct (typeID, vendorID, productURI, isReady);
        
        return productID;
    }


  function updateProduct(uint productID, uint typeID, uint vendorID, string memory URI, bool isReady) 
  public returns(uint) {
      
        products[productID] = product(typeID, vendorID, URI, isReady, 1);
        
        return productID;
    }
        

  function removeProduct(uint productID) public returns(uint) {
        _burn(productID);
        delete products[productID];
        return productID;
    }

  function makePurchase(uint purchaseDate, uint deliveryDate, uint vendorID, uint productID, uint quantity) 
  public returns(uint) {
      
      require(purchaseDate <= deliveryDate, "you cannot rent backwards in time");
      require(quantity < products[productID].quantity, "Out of stock");
      
      
      emit MakePurchase (purchaseDate, deliveryDate, vendorID, productID, quantity);
      
      return productID;
  }

}
