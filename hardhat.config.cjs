require("@nomiclabs/hardhat-ethers");
require("dotenv").config();

const ALCHEMY_RPC = process.env.ALCHEMY_RPC || "your alchemy RPC address here "; #this is priavate info hence not included 
const PRIVATE_KEY = process.env.PRIVATE_KEY || "your wallet private key here (the one from the sender address";#this is private info hence not included 

/**
 * @type import('hardhat/config').HardhatUserConfig
 */
module.exports = {
  solidity: "0.8.20",
  networks: {
    sepolia: {
      url: ALCHEMY_RPC,
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
    },
  },
};
