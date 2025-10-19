// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract MedicalDataAccess {
    address public admin;

    constructor() {
        admin = msg.sender;
    }

    enum Section { PatientInfo, BloodTests, Imaging, Medications }

    struct Patient {
        string mrn;                 // Medical Record Number
        string name;                // Full Name
        uint256 age;                // Age in years
        string gender;              // Gender
        string physicaladdress;     // Physical address)
        string phone;               // Contact phone number
        string email;               // Contact email
        
    }

    struct BloodTest {
        string pdfHash;             // IPFS hash or external reference
        string description;         // Test Label or Description
        uint256 date;               // Timnestamp of the test
    }

    struct ImagingRecord {
        string imageType;           // Type of imaging (e.g., X-ray, MRI)
        string description;         // Description of the imaging
        string imageHash;           // IPFS or off-chain reference
        uint256 date;               // Timestamp of the imaging
    }

    struct Medication {
        string drugName;            // Name of the medication
        string dosage;              // Dosage information
        string frequency;           // Frequency of intake
        uint256 startDate;          // Start date of the medication
        uint256 endDate;            // End date of the medication
    }

    struct AccessGrant {
        bool isActive;
        uint256 expiresAt;
    }

    mapping(address => Patient) private patientInfo;
    mapping(address => BloodTest[]) private bloodTests;
    mapping(address => ImagingRecord[]) private imagingRecords;
    mapping(address => Medication[]) private medications;

    mapping(address => mapping(Section => AccessGrant)) public accessPermissions;

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    modifier hasAccess(address patient, Section section) {
        AccessGrant memory grant = accessPermissions[msg.sender][section];
        require(grant.isActive && block.timestamp <= grant.expiresAt, "Access denied or expired");
        _;
    }

    // Grant access for a limited time (in seconds)
    function grantTimedAccess(address user, Section section, uint256 durationSeconds) public onlyAdmin {
        accessPermissions[user][section] = AccessGrant(true, block.timestamp + durationSeconds);
    }

    // Revoke access manually
    function revokeAccess(address user, Section section) public onlyAdmin {
        accessPermissions[user][section] = AccessGrant(false, 0);
    }

    // Patient registration
    function registerPatient(
        string memory _mrn,
        string memory _name,
        uint256 _age,
        string memory _gender,
        string memory _physicaladdress,
        string memory _phone,
        string memory _email

    ) public {
        patientInfo[msg.sender] = Patient(_mrn, _name, _age, _gender, _physicaladdress, _phone, _email);
    }

    // Add blood test
    function addBloodTest(string memory _pdfHash, string memory _description, uint256 _date) public {
        bloodTests[msg.sender].push(BloodTest(_pdfHash, _description, _date));
    }

    // Add imaging record
    function addImaging(string memory _type, string memory _description, string memory _imageHash, uint256 _date) public {
        imagingRecords[msg.sender].push(ImagingRecord(_type, _description, _imageHash, _date));
    }

    // Add medication
    function addMedication(string memory _drug, string memory _dosage, string memory _frequency, uint256 _start, uint256 _end) public {
        medications[msg.sender].push(Medication(_drug, _dosage, _frequency, _start, _end));
    }

    // View functions with time-aware access control
    function viewPatientInfo(address _patient) public view hasAccess(_patient, Section.PatientInfo) returns (Patient memory) {
        return patientInfo[_patient];
    }

    function viewBloodTests(address _patient) public view hasAccess(_patient, Section.BloodTests) returns (BloodTest[] memory) {
        return bloodTests[_patient];
    }

    function viewImaging(address _patient) public view hasAccess(_patient, Section.Imaging) returns (ImagingRecord[] memory) {
        return imagingRecords[_patient];
    }

    function viewMedications(address _patient) public view hasAccess(_patient, Section.Medications) returns (Medication[] memory) {
        return medications[_patient];
    }
}
