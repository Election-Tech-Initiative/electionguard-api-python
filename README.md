![Microsoft Defending Democracy Program: ElectionGuard](images/electionguard-banner.svg)

#  🗳️ ElectionGuard Web API

![package](https://github.com/microsoft/electionguard-web-api/workflows/Package/badge.svg)
[![license](https://img.shields.io/github/license/microsoft/electionguard-web-api)](LICENSE)

This is an API that interacts with admin encrypter devices to perform ballot encryption, casting, spoiling, and tallying. This makes use of the C# Nuget package.

## Runnning the sample

## Debugging from Visual Studio Code

Open the Debug Window and execute: `.NET Core Launch (web)`

## Debugging from Visual studio Code (in Docker)

1. Open the Command Palette and execute: `Tasks: Run Task > run docker (debug)`
2. Open the Debug Window and execute: `.NET Core Attach (docker)`

### Running as a Windows Service

On a Windows Machine, from an elevated powershell prompt

```powershell
pwsh .\scripts\Create-Windows-Service.ps1
```

### Interacting with the API

There is a [Postman]() collection and environment included.  Ensure the API is running on your desired port, and import the files in `.postman` into your postman environment.  

The API loads `election` and `ElectionGuardConfig` values in diffferent ways.  On startup, the `ElectionGuardController` searches for these files on the file system.  They can also be overwritten bby calling `InitializeEncryption`.  Lastly, these configuration values can be provided with specific request bodies where relevant to override the cached values for that request only.

#### Test the Complete workflow

You can test the entire workflow, which overwrites the sample data with new encryption keys.

To test the primary workflow, which interacts wiht the file system, execute the postman requests in the following order:

- `1. Create Election`
- `2.a Initialize Encryption via Body` (to override the default election.json and election.cojnfig.json files)
- `3.a Encrypt Ballot (Individual)`
- `3.b Encrypt Ballots (Set)`
- `4.a Load Ballots` (optional, if you wish to test loading the ballots)
- `5. Record Ballots`
- `6. Tally Votes`

#### Test Encrypting Ballots

This test simulates encrypting ballots on a Ballot Marking Device.

Encrypting Ballots can be done using the provided sample files in the `data/` folder.

Reset your postman environment variables to the default ones included in the repo, if you ran the previous test.

- `3.a Encrypt Ballot (Individual)`
- `3.b Encrypt Ballots (Set)`
- `4.a Load Ballots`

Verify that the loaded ballots match the encrypted ballots.

#### Test Loading and Decrypting Ballots

This test simulates loading ballots from a Ballot Marking Device and decrypting the results.

Reset your postman environment variables to the default ones included in the repo, if you ran the previous test.

- `4.a Load Ballots`
- `5. Record Ballots`
- `6. Tally Votes`

Verify that a tally result is returned and matches the data in `data/tallies.sample.response.json`

## Key concepts

This API is a werapper around the C-Sharp SDK.  All of the interesting code is in `ElectionController.cs`.

### Providing Configuration

In order to encrypt an election, the API must know about the election (`election.json`) and the ElectionGuard configuration (`election.config.json`).  Samples are provided in the `data` folder.  This dataq is also pre-loaded into the postman environment.

Configuration can be provided in multiple ways

1. At Runtime - On the first call to `ElectionController` we search for the configuration files in the `./data` relative path at runtime.
2. via `InitializeEncryption` - by making the Initialize Encryption request, a json body or a file path can be specified to cache the configuration.
3. Via `EncryptBallot` - by providing the election configuration with each encrypt ballot request, the provided values will be used to encrypt a specific ballot.

## Contributing
Help defend democracy and [contribute to the project](CONTRIBUTING).

<!-- 
Guidelines on README format: https://review.docs.microsoft.com/help/onboard/admin/samples/concepts/readme-template?branch=master

Guidance on onboarding samples to docs.microsoft.com/samples: https://review.docs.microsoft.com/help/onboard/admin/samples/process/onboarding?branch=master

Taxonomies for products and languages: https://review.docs.microsoft.com/new-hope/information-architecture/metadata/taxonomies?branch=master
-->

