pragma solidity ^0.5.0;

import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/token/ERC721/ERC721.sol";
import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/release-v2.5.0/contracts/drafts/Counters.sol";


contract FarmersMarket is ERC721{
    using Counters for Counters.Counter;
    
    struct product {
        uint vendorID;
        string URI; 
        uint available_quantity;
        uint price;
    }
    
    struct vendor {
        string URI;
        address _address;
        
    }
    
    // we need to link the productID to the vendor ID in the URI? ???
    }
    
    Counters.Counter private productIDS;
    Counters.Counter private vendorIDS;
   
    
    // mapping token_id to asset
    mapping(uint => product) public products;
    mapping(uint => vendor) public vendors;
   
    
    event RegisterVendor(uint, string, address);
    event RegisterProduct(uint, string, uint, uint);
    event MakePurchase();
    event RemoveVendor(uint);   //just need vendorID
    event RemoveProduct(uint); //just need productID
    
    constructor("Farmers Market", "FMD") public {
        
    }
 

 function registerVedor(address vendorAddress, string memory vendorURI) public returns(uint) {
        
        vendorIDS.increment();
        uint vendorID = vendorIDS.current();
        
        vendors[vendorID] = vendor(vendorURI, vendorAddress);
        
        return vendorID;
    }

