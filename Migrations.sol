// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract Migrations {
    address public owner = msg.sender;

    modifier restricted() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    function setCompleted(uint completed) public restricted {}
}
