require("@nomiclabs/hardhat-ethers");
require("dotenv").config();

const ALCHEMY_RPC = process.env.ALCHEMY_RPC || "https://eth-sepolia.g.alchemy.com/v2/veSD0nysW7_16h_8Kb14l";
const PRIVATE_KEY = process.env.PRIVATE_KEY || "0x511423562bdf8e6fe95cc5760fe78def1bb443e4a19a74711f0c9ac5e7c507cb";

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
