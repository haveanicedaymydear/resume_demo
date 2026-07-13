# Original Coursework Report - Public Summary

This note summarizes the original 12-page English report without republishing the complete document or private implementation assets.

## Research objective

The report studied access control for Internet-of-Vehicles environments, where vehicles and infrastructure exchange sensitive information under dynamic operating conditions. It identified three target problems:

1. centralized authentication and single-point-of-failure risk;
2. insufficiently fine-grained and static authorization;
3. the absence of behaviour-sensitive trust evaluation.

## Proposed design

The report proposed a two-layer solution:

- **distributed access authentication** using a Hyperledger Fabric consortium chain, digital signatures, certificates, and Raft ordering;
- **dynamic access control** using subject and environment attributes together with a behaviour-derived trust value.

The architecture separated application, access-control, authentication, blockchain, and cloud/deployment concerns.

## Implemented prototype evidence

The surviving report and screenshots document the following activities:

- provisioning and accessing an Azure Ubuntu virtual machine;
- Linux package and security setup through SSH;
- deployment of a multi-organization Fabric environment with Docker;
- chaincode lifecycle installation and approval;
- certificate-registration and verification tests;
- a trust-value update function affecting subsequent permissions;
- evaluation scripts or figures for transaction throughput, authentication latency, and CPU utilization;
- simulated malicious-node cases discussed in the report.

## Important distinction

The original report also described an extended cloud architecture involving Kubernetes, key management, and monitoring. Public CV evidence keeps this separate from the access-control prototype. The independently archived [`FabricK8s`](https://github.com/haveanicedaymydear/FabricK8s) repository represents the later infrastructure/deployment evidence and should not be treated as identical to the original IoV prototype.

## Public-claim boundary

The original coursework report includes quantitative performance and simulated attack-detection results. These figures are preserved in the private source artifact but are **not presented here as independently revalidated research findings**. The public archive supports the narrower claim that an end-to-end trust-aware access-control prototype and evaluation workflow were designed and exercised.

## Contribution summary

The project's main contribution was the integration of:

- distributed certificate-based authentication;
- immutable access and trust records;
- smart-contract policy enforcement;
- dynamic trust updates;
- cloud-hosted prototype deployment;
- system-performance and security-scenario evaluation.
