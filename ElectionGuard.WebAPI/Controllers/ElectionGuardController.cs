using ElectionGuard.SDK;
using ElectionGuard.SDK.Models;
using ElectionGuard.Utilities;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using ElectionGuard.WebAPI.Models;
using System.Collections.Generic;
using System;
using System.IO;
using System.Linq;
using ElectionGuard.Tools;
using Newtonsoft.Json;
using VotingWorks.Ballot;
using System.Threading.Tasks;

namespace ElectionGuard.WebAPI.Controllers
{

    [ApiController]
    [Route("[controller]")]
    [DisableRequestSizeLimit]
    public class ElectionGuardController : ControllerBase
    {
        private const string WelcomeMessage = "Welcome to ElectionGuard";
        private const string FileLoadErrorMessage = "File(s) not loaded. Check file paths.";
        private const string EncryptionSetupRequiredMessage = "Encryption is not setup. Election Map and ElectionGuard Config required.";
        private const string EncryptMissingIdentifierMessage = "Encrypt Ballot requires a 'ballotId'";
        private const string ThresholdExceedsTrusteesMessage = "Threshold exceeds count of available trustees.";

        private readonly ILogger<ElectionGuardController> _logger;
        private readonly IConfigFileService _config;
        private readonly IElectionMapper<Election, Ballot, VoteTally> _electionMapper;

        private static int _currentBallotCount = 0;

        private static Election _election = null;
        private static ElectionMap _electionMap = null;
        private static ElectionGuardConfig _electionGuardConfig = null;

        private static string _exportPath = null;
        private static string _encryptedBallotsExportFileName = null;
        private static string _registeredBallotsExportFileNamePrefix = null;
        private static string _tallyExportFileNamePrefix = null;

        public ElectionGuardController(ILogger<ElectionGuardController> logger, IElectionMapper<Election, Ballot, VoteTally> electionMapper, IConfigFileService configService)
        {
            _config = configService;
            _logger = logger;
            _electionMapper = electionMapper;

            _exportPath = Path.Combine(_config.GetDataDirectory(), "election_results");
            logger.LogInformation($"DATA: resolved at: {_exportPath}");

            // try to load the election config files from the file system
            var election = _config.GetElection();
            if (election != null)
            {
                logger.LogInformation("ElectionController: Found Election");
                _election = election;
                _electionMap = _electionMapper.GetElectionMap(_election);
                
            }

            var electionguardConfig = _config.getElectionGuardConfig();
            if (electionguardConfig != null)
            {
                logger.LogInformation("ElectionController: Found ElectionGuard Config");
                _electionGuardConfig = electionguardConfig;
            }

            var now = DateTime.Now;

            _encryptedBallotsExportFileName = $"encrypted-ballots_{now.Year}_{now.Month}_{now.Day}";
            _registeredBallotsExportFileNamePrefix = $"registered-ballots";
            _tallyExportFileNamePrefix = "tally-results";
        }

        [HttpGet]
        public string Get()
        {
            return WelcomeMessage;
        }

        [HttpPost]
        public ActionResult<CreateElectionResult> CreateElection(ElectionRequest request)
        {
            try
            {
                var electionMap = _electionMapper.GetElectionMap(request.Election);
                request.Config.NumberOfSelections = electionMap.NumberOfSelections;

                var election = ElectionGuardApi.CreateElection(request.Config);
                return CreatedAtAction(nameof(CreateElection), new ElectionResponse {
                    ElectionGuardConfig = election.ElectionGuardConfig,
                    TrusteeKeys = election.TrusteeKeys,
                    ElectionMap = electionMap,
                });
            }
            catch (Exception ex)
            {
                _logger.LogError("CreateElection: ", ex);
                return StatusCode(500);
            }
        }

        [HttpPost]
        [Route(nameof(InitializeEncryption))]
        public async Task<ActionResult<InitializeEncryptionResponse>> InitializeEncryption(
            [FromQuery] string exportPath, [FromQuery] string exportFileName, [FromQuery] string electionFilePath, [FromQuery] string electionGuardConfigFilePath)
        {
            try
            {
                _exportPath = exportPath;
                _encryptedBallotsExportFileName = exportFileName;

                var election = _config.GetElection(electionFilePath);
                var electionGuardConfig = _config.getElectionGuardConfig(electionGuardConfigFilePath);
                return await InitializeEncryption(new InitializeEncryptionRequest
                {
                    Election = election,
                    ElectionGuardConfig = electionGuardConfig
                });
            }
            catch (Exception ex)
            {
                _logger.LogError("InitializeEncryption: ", ex);
                return BadRequest(FileLoadErrorMessage);
            }
        }

        [HttpPut]
        [Route(nameof(InitializeEncryption))]
        public async Task<ActionResult<InitializeEncryptionResponse>> InitializeEncryption(InitializeEncryptionRequest request)
        {
            try 
            {
                _currentBallotCount = 0;
                _election = request.Election;
                _electionMap = _electionMapper.GetElectionMap(request.Election);
                _electionGuardConfig = request.ElectionGuardConfig;
                _exportPath = request.ExportPath;
                _encryptedBallotsExportFileName = request.ExportFileName;

                await _config.SetElectionAsync(_election);
                await _config.setElectionGuardConfigAsync(_electionGuardConfig);

                var response = new InitializeEncryptionResponse {
                    Election = request.Election,
                    ElectionGuardConfig = _electionGuardConfig,
                    ElectionMap = _electionMap
                };

                return AcceptedAtAction(nameof(InitializeEncryption), response);
            } 
            catch (Exception ex)
            {
                _logger.LogError("InitializeEncryption: ", ex);
                return StatusCode(500);
            }
        }

        [HttpPost]
        [Route(nameof(EncryptBallot))]
        public ActionResult<EncryptBallotResponse> EncryptBallot(EncryptBallotRequest request)
        {
            // TODO: cache encrypted ballot id's in memory and disallow encrypting an existing ballot id
            try
            {
                var exportPath = request.ExportPath ?? _exportPath;
                var exportFileName = request.ExportFileName ?? _encryptedBallotsExportFileName;
                var electionMap = request.ElectionMap ?? GetElectionMap(request.Election);
                var electionGuardConfig = request.ElectionGuardConfig ?? _electionGuardConfig;
                if (electionMap == null || electionGuardConfig == null)
                {
                    return BadRequest(EncryptionSetupRequiredMessage);
                }

                if (String.IsNullOrWhiteSpace(request.Ballot.BallotId))
                {
                    return BadRequest(EncryptMissingIdentifierMessage);
                }

                var selections = _electionMapper.ConvertToSelections(request.Ballot, electionMap);
                var numberOfExpected = electionMap.BallotStyleMaps[request.Ballot.BallotStyle.Id].ExpectedNumberOfSelected;
                var encryptedBallot = ElectionGuardApi.EncryptBallot(
                    selections,
                    numberOfExpected,
                    electionGuardConfig,
                    request.Ballot.BallotId,
                    exportPath,
                    exportFileName);

                _currentBallotCount++;

                var response = new EncryptBallotResponse()
                {
                    Id = encryptedBallot.ExternalIdentifier,
                    EncryptedBallotMessage = encryptedBallot.EncryptedBallotMessage,
                    Tracker = encryptedBallot.Tracker,
                    OutputFileName = encryptedBallot.OutputFileName,
                    CurrentNumberOfBallots = _currentBallotCount
                };

                return CreatedAtAction(nameof(EncryptBallot), response);
            }
            catch (Exception ex)
            {
                _logger.LogError("EncryptBallot: ", ex);
                return StatusCode(500);
            }
        }

        [HttpPost]
        [Route(nameof(EncryptBallots))]
        public ActionResult<EncryptBallotResponse[]> EncryptBallots(EncryptBallotsRequest request)
        {
            // TODO: cache encrypted ballot id's in memory and disallow encrypting an existing ballot id

            try
            {
                var exportPath = request.ExportPath ?? _exportPath;
                var exportFileName = request.ExportFileName ?? _encryptedBallotsExportFileName;
                var electionMap = request.ElectionMap ?? GetElectionMap(request.Election);
                var electionGuardConfig = request.ElectionGuardConfig ?? _electionGuardConfig;
                if (electionMap == null || electionGuardConfig == null)
                {
                    return BadRequest(EncryptionSetupRequiredMessage);
                }

                if (request.Ballots.Any(i => String.IsNullOrWhiteSpace(i.BallotId)))
                {
                    return BadRequest(EncryptMissingIdentifierMessage);
                }
                
                var response = new List<EncryptBallotResponse>();

                foreach (var ballot in request.Ballots)
                {
                    var selections = _electionMapper.ConvertToSelections(ballot, electionMap);
                    var numberOfExpected = electionMap.BallotStyleMaps[ballot.BallotStyle.Id].ExpectedNumberOfSelected;
                    var encryptedBallot = ElectionGuardApi.EncryptBallot(
                        selections, 
                        numberOfExpected, 
                        electionGuardConfig, 
                        ballot.BallotId,
                        exportPath,
                        exportFileName);

                    _currentBallotCount++;

                    var ballotResponse = new EncryptBallotResponse()
                    {
                        Id = encryptedBallot.ExternalIdentifier,
                        EncryptedBallotMessage = encryptedBallot.EncryptedBallotMessage,
                        Tracker = encryptedBallot.Tracker,
                        OutputFileName = encryptedBallot.OutputFileName,
                        CurrentNumberOfBallots = _currentBallotCount
                    };

                    response.Add(ballotResponse);
                }

                return CreatedAtAction(nameof(EncryptBallots), response);
            }
            catch (Exception ex)
            {
                _logger.LogError("EncryptBallots: ", ex);
                return StatusCode(500);
            }
        }

#nullable enable

        [HttpDelete]
        [Route(nameof(BallotFile))]
        public ActionResult BallotFile([FromQuery] string? path, [FromQuery] string fileName)
        {
            try
            {
                var exportPath = path ?? _exportPath;

                if (String.IsNullOrWhiteSpace(exportPath))
                {
                    return BadRequest(FileLoadErrorMessage);
                }

                var success = ElectionGuardApi.SoftDeleteEncryptedBallotsFile(
                    exportPath,
                    fileName
                );

                return success? Ok() : StatusCode(500);
            }
            catch (Exception ex)
            {
                _logger.LogError("BallotFile: ", ex);
                return StatusCode(500);
            }
        }

#nullable disable

        [HttpPost]
        [Route(nameof(LoadBallots))]
        public ActionResult<LoadBallotsResponse[]> LoadBallots(LoadBallotsRequest request)
        {
            try
            {
                var importPath = request.ImportPath ?? _exportPath;

                if (String.IsNullOrWhiteSpace(importPath))
                {
                    return BadRequest(FileLoadErrorMessage);
                }

                var electionGuardConfig = request.ElectionGuardConfig ?? _electionGuardConfig;
                if (electionGuardConfig == null)
                {
                    return BadRequest(EncryptionSetupRequiredMessage);
                }

                var result = ElectionGuardApi.LoadBallotsFile(
                    request.StartIndex,
                    request.Count,
                    electionGuardConfig.NumberOfSelections,
                    Path.Combine(
                        importPath,
                    request.ImportFileName
                    )
                );

                if (result.EncryptedBallotMessages.Count != result.ExternalIdentifiers.Count)
                {
                    return StatusCode(500);
                }

                var response = new List<LoadBallotsResponse>();

                for (int i = 0; i < result.EncryptedBallotMessages.Count; i++)
                {
                    var ballot = new LoadBallotsResponse()
                    {
                        Id = result.ExternalIdentifiers.ElementAt(i),
                        EncryptedBallotMessage = result.EncryptedBallotMessages.ElementAt(i)
                    };
                    response.Add(ballot);
                }

                return AcceptedAtAction(nameof(LoadBallots), response);
            }
            catch (Exception ex)
            {
                _logger.LogError("LoadBallots: ", ex);
                return StatusCode(500);
            }
        }

        [HttpPost]
        [Route(nameof(RecordBallots))]
        public ActionResult<RecordBallotsResponse> RecordBallots(RecordBallotsRequest request)
        {
            try
            {
                // if the exportPath resolves to null, the default will be used
                var exportPath = request.ExportPath ?? _exportPath;
                var exportFileNamePrefix = request.ExportFileNamePrefix ?? _registeredBallotsExportFileNamePrefix;

                var electionGuardConfig = request.ElectionGuardConfig ?? _electionGuardConfig;
                if (electionGuardConfig == null)
                {
                    return BadRequest(EncryptionSetupRequiredMessage);
                }

                if (request.Ballots == null)
                {
                    return BadRequest("Ballots cannot be null");
                }

                // HACK: If we receive a list containing more than one ballot for a given Id
                // just take the last one

                var ballots = request.Ballots.GroupBy(e => new {
                    Id = e.Id
                })
                .Select(g => g.Last());

                var identifiers = ballots.Select(i => i.Id).ToList();
                var ballotMessages = ballots.Select(i => i.EncryptedBallotMessage).ToList();

                if ((request.CastBallotIds.Count() + request.SpoildBallotIds.Count()) != ballots.Count())
                {
                    return BadRequest("All ballots must be cast or spoiled");
                }

                var result = ElectionGuardApi.RecordBallots(
                    electionGuardConfig,
                    request.CastBallotIds, 
                    request.SpoildBallotIds, 
                    identifiers,
                    ballotMessages,
                    exportPath,
                    exportFileNamePrefix
                );

                var response = new RecordBallotsResponse()
                {
                    RegisteredBallotsFileName = result.EncryptedBallotsFilename,
                    CastedBallotTrackers = result.CastedBallotTrackers,
                    SpoiledBallotTrackers = result.SpoiledBallotTrackers
                };

                return AcceptedAtAction(nameof(RecordBallots), response);
            }
            catch (Exception ex)
            {
                _logger.LogError("RecordBallots: ", ex);
                return StatusCode(500);
            }
        }

        [HttpPost]
        [Route(nameof(TallyVotes))]
        public ActionResult<TallyVotesResponse> TallyVotes(TallyVotesRequest request)
        {
            try
            {
                // if the exportPath resolves to null, the default will be used
                var exportPath = request.ExportPath ?? _exportPath;
                var exportFileNamePrefix = request.ExportFileNamePrefix ?? _tallyExportFileNamePrefix;

                var electionMap = request.ElectionMap ?? GetElectionMap(request.Election);
                var electionGuardConfig = request.ElectionGuardConfig ?? _electionGuardConfig;
                if (electionGuardConfig == null || electionMap == null)
                {
                    return BadRequest(EncryptionSetupRequiredMessage);
                }

                if (request.TrusteeKeys.Count < request.ElectionGuardConfig.Threshold)
                {
                    return BadRequest(ThresholdExceedsTrusteesMessage);
                }

                var result = ElectionGuardApi.TallyVotes(
                    request.ElectionGuardConfig, 
                    request.TrusteeKeys.Values, 
                    request.TrusteeKeys.Count, 
                    request.RegisteredBallotsFileName,
                    exportPath,
                    exportFileNamePrefix);

                var response = new TallyVotesResponse()
                {
                    EncryptedTallyFilename = result.EncryptedTallyFilename,
                    TallyResults = _electionMapper.ConvertToTally(result.TallyResults.ToArray(), electionMap)
                };

                return CreatedAtAction(nameof(TallyVotes), response);
            }
            catch (Exception ex)
            {
                _logger.LogError("InitializeEncryption: ", ex);
                return StatusCode(500);
            }
        }

#nullable enable
        private ElectionMap? GetElectionMap(Election? election)
        {
            var electionMap = election != null 
                ? _electionMapper.GetElectionMap(election) 
                : _electionMap;
            return electionMap;
        }
#nullable disable
    }
}
