// scripts/deploy.cjs
require("dotenv").config();
const hre = require("hardhat");

async function main() {
  // 1. Get the contract factory
  const MedicalDataAccess = await hre.ethers.getContractFactory("MedicalDataAccess");

  // 2. Deploy the contract
  const medicalDataAccess = await MedicalDataAccess.deploy();

  // 3. Wait until deployment is mined
  await medicalDataAccess.deployed();

  // 4. Print the deployed contract address
  console.log("MedicalDataAccess deployed to:", medicalDataAccess.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
