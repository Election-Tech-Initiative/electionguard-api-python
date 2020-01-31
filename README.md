---
page_type: sample
languages:
- csharp
products:
- dotnet
description: "Add 150 character max description"
urlFragment: "update-this-to-unique-url-stub"
---

# Official Microsoft Sample

<!-- 
Guidelines on README format: https://review.docs.microsoft.com/help/onboard/admin/samples/concepts/readme-template?branch=master

Guidance on onboarding samples to docs.microsoft.com/samples: https://review.docs.microsoft.com/help/onboard/admin/samples/process/onboarding?branch=master

Taxonomies for products and languages: https://review.docs.microsoft.com/new-hope/information-architecture/metadata/taxonomies?branch=master
-->

Give a short description for your sample here. What does it do and why is it important?

## Contents

Outline the file contents of the repository. It helps users navigate the codebase, build configuration and any related assets.

| File/folder       | Description                                |
|-------------------|--------------------------------------------|
| `src`             | Sample source code.                        |
| `.gitignore`      | Define what to ignore at commit time.      |
| `CHANGELOG.md`    | List of changes to the sample.             |
| `CONTRIBUTING.md` | Guidelines for contributing to the sample. |
| `README.md`       | This README file.                          |
| `LICENSE`         | The license for the sample.                |

## Prerequisites

Outline the required components and tools that a user might need to have on their machine in order to run the sample. This can be anything from frameworks, SDKs, OS versions or IDE releases.

## Setup

Explain how to prepare the sample once the user clones or downloads the repository. The section should outline every step necessary to install dependencies and set up any settings (for example, API keys and output folders).

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

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
