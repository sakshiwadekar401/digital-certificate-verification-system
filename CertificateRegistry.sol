// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract CertificateRegistry {
    struct Certificate {
        string studentName;
        string courseName;
        uint issueDate;
        string certificateHash;
    }

    mapping(bytes32 => Certificate) public certificates;

    event CertificateRegistered(
        string certificateHash,
        string studentName,
        string courseName,
        uint issueDate
    );

    event Debug(string message, uint value); // Debug event

    function registerCertificate(
        string memory studentName,
        string memory courseName,
        uint issueDate,
        string memory certificateHash
    ) public {
        bytes32 key = keccak256(abi.encodePacked(certificateHash));
        certificates[key] = Certificate(studentName, courseName, issueDate, certificateHash);
        emit Debug("Before CertificateRegistered", issueDate); // Add this line
        emit CertificateRegistered(certificateHash, studentName, courseName, issueDate);
        emit Debug("After CertificateRegistered", issueDate); // Add this line
    }

    function verifyCertificate(string memory certificateHash) public view returns (bool) {
        bytes32 key = keccak256(abi.encodePacked(certificateHash));
        return certificates[key].issueDate != 0;
    }

    function getCertificate(string memory certificateHash)
        public
        view
        returns (
            string memory,
            string memory,
            uint,
            string memory
        )
    {
        bytes32 key = keccak256(abi.encodePacked(certificateHash));
        Certificate memory certificate = certificates[key];
        return (
            certificate.studentName,
            certificate.courseName,
            certificate.issueDate,
            certificate.certificateHash
        );
    }
}