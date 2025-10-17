
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MedicalDataAccess {
    
    enum Section { PersonalInfo, BloodResults, Imaging, Medications }

    struct BloodTest {
        string pdfHash;
        string description;
        uint256 date;
    }

    struct ImagingRecord {
        string imageType;
        string description;
        string imageHash;
        uint256 date;
    }

    struct Medication {
        string drugName;
        string dosage;
        string frequency;
        uint256 startDate;
        uint256 endDate;
    }

    struct Patient {
        string mrn;
        string name;
        uint256 age;
        string gender;
        string physicaladdress;
        string phone;
        string email;
    }

    struct Access {
        bool isActive;
        uint256 expiresAt;
    }

    address public admin;
    mapping(address => Patient) private patients;
    mapping(address => BloodTest[]) private bloodTests;
    mapping(address => ImagingRecord[]) private imagingRecords;
    mapping(address => Medication[]) private medications;
    mapping(address => mapping(Section => Access)) public accessPermissions;

    constructor() {
        admin = msg.sender;
    }

    // -------------------------
    // Patient registration
    // -------------------------
    function registerPatient(
        string memory _mrn,
        string memory _name,
        uint256 _age,
        string memory _gender,
        string memory _physicaladdress,
        string memory _phone,
        string memory _email
    ) external {
        patients[msg.sender] = Patient(_mrn, _name, _age, _gender, _physicaladdress, _phone, _email);
    }

    // -------------------------
    // Add medical data
    // -------------------------
    function addBloodTest(string memory _pdfHash, string memory _description, uint256 _date) external {
        bloodTests[msg.sender].push(BloodTest(_pdfHash, _description, _date));
    }

    function addImaging(string memory _type, string memory _description, string memory _imageHash, uint256 _date) external {
        imagingRecords[msg.sender].push(ImagingRecord(_type, _description, _imageHash, _date));
    }

    function addMedication(string memory _drug, string memory _dosage, string memory _frequency, uint256 _start, uint256 _end) external {
        medications[msg.sender].push(Medication(_drug, _dosage, _frequency, _start, _end));
    }

    // -------------------------
    // Access control
    // -------------------------
    function grantTimedAccess(address user, Section section, uint256 durationSeconds) external {
        require(msg.sender == admin || msg.sender == user, "Not authorized");
        accessPermissions[user][section] = Access(true, block.timestamp + durationSeconds);
    }

    function revokeAccess(address user, Section section) external {
        require(msg.sender == admin || msg.sender == user, "Not authorized");
        accessPermissions[user][section] = Access(false, 0);
    }



    // -------------------------
    // View functions
    // -------------------------
    function viewBloodTests(address _patient) external view returns (BloodTest[] memory) {
        return bloodTests[_patient];
    }

    function viewImaging(address _patient) external view returns (ImagingRecord[] memory) {
        return imagingRecords[_patient];
    }

    function viewMedications(address _patient) external view returns (Medication[] memory) {
        return medications[_patient];
    }

    function viewPatientInfo(address _patient) external view returns (Patient memory) {
        return patients[_patient];
    }
}
