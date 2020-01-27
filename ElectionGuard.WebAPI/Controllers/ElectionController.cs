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

namespace ElectionGuard.WebAPI.Controllers
{

    [Obsolete("This is for stubbing/mocking an API only.  To be removed in a future release")]
    public struct TestEncryptBallotResult 
    {
        public string EncryptedBallotMessage { readonly get; set; }
        public string Identifier { readonly get; set; }
        public string Tracker { readonly get; set; }
        public long CurrentNumberOfBallots { readonly get; set; }
    }

    [ApiController]
    [Route("[controller]")]
    public class ElectionController : ControllerBase
    {
        private long test_session_ballot_count = 0;

        private const string WelcomeMessage = "Welcome to ElectionGuard";
        private const string FileLoadErrorMessage = "File(s) not loaded. Check file paths.";
        private const string EncryptionSetupRequiredMessage = "Encryption is not setup. Election Map and ElectionGuard Config required.";
        private const string ThresholdExceedsTrusteesMessage = "Threshold exceeds count of available trustees.";

        private readonly ILogger<ElectionController> _logger;
        private readonly IConfigFileService _config;
        private readonly IElectionMapper<Election, Ballot, VoteTally> _electionMapper;

        private static int _currentBallotCount = 0;

        private static Election _election = null;
        private static ElectionMap _electionMap = null;
        private static ElectionGuardConfig _electionGuardConfig = null;

        private static string _exportPath = null;

        public ElectionController(ILogger<ElectionController> logger, IElectionMapper<Election, Ballot, VoteTally> electionMapper, IConfigFileService configService)
        {
            _config = configService;
            _logger = logger;
            _electionMapper = electionMapper;

            _exportPath = _config.GetDataDirectory();
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
        }

        [HttpGet]
        public string Get()
        {
            return WelcomeMessage;
        }

        [HttpPost]
        public ActionResult<CreateElectionResult> CreateElection(ElectionRequest request)
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

        [HttpPost]
        [Route(nameof(InitializeEncryption))]
        public ActionResult<InitializeEncryptionResponse> InitializeEncryption([FromQuery] string exportPath, [FromQuery] string electionFilePath, [FromQuery] string electionGuardConfigFilePath)
        {
            try
            {
                _exportPath = exportPath;

                var election = _config.GetElection(electionFilePath);
                var electionGuardConfig = _config.getElectionGuardConfig(electionGuardConfigFilePath);
                return InitializeEncryption(new InitializeEncryptionRequest
                {
                    Election = election,
                    ElectionGuardConfig = electionGuardConfig
                });
            }
            catch
            {
                return BadRequest(FileLoadErrorMessage);
            }
        }

        private static T LoadJsonFile<T>(string filePath)
        {
            using var reader = new StreamReader(filePath);
            var json = reader.ReadToEnd();
            var deserializedJson = JsonConvert.DeserializeObject<T>(json);
            return deserializedJson;
        }


        [HttpPut]
        [Route(nameof(InitializeEncryption))]
        public ActionResult<InitializeEncryptionResponse> InitializeEncryption(InitializeEncryptionRequest request)
        {
            _currentBallotCount = 0;
            _election = request.Election;
            _electionMap = _electionMapper.GetElectionMap(request.Election);
            _electionGuardConfig = request.ElectionGuardConfig;
            _exportPath = request.ExportPath;

            var response = new InitializeEncryptionResponse {
                Election = request.Election,
                ElectionGuardConfig = _electionGuardConfig,
                ElectionMap = _electionMap
            };

            return CreatedAtAction(nameof(InitializeEncryption), response);
        }

        [HttpPost]
        [Route(nameof(EncryptBallot))]
        public ActionResult<TestEncryptBallotResult> EncryptBallot(EncryptBallotRequest request)
        {
            var exportPath = request.ExportPath ?? _exportPath;
            var electionMap = request.ElectionMap ?? _electionMap;
            var electionGuardConfig = request.ElectionGuardConfig ?? _electionGuardConfig;
            if (electionMap == null || electionGuardConfig == null || exportPath == null)
            {
                return BadRequest(EncryptionSetupRequiredMessage);
            }

            // TESTING: Mock response for integration testing
             var testResult = new TestEncryptBallotResult {
                EncryptedBallotMessage = "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",
                Identifier = request.Ballot.BallotId,
                Tracker = "patent CD2CK length CKDBK hearsay FGH6M cave GBH7K cantaloupe K9H6K briefly F4244 fraction 37B99 behest 383KM",
                CurrentNumberOfBallots = ++test_session_ballot_count
            };

            return CreatedAtAction(nameof(EncryptBallot), testResult);

            // TODO: actual encryption

            // var selections = _electionMapper.ConvertToSelections(request.Ballot, electionMap);
            // var numberOfExpected = electionMap.BallotStyleMaps[request.Ballot.BallotStyle.Id].ExpectedNumberOfSelected;
            // var encryptedBallot = ElectionGuardApi.EncryptBallot(
            //     selections,
            //     numberOfExpected,
            //     electionGuardConfig,
            //     request.CurrentBallotCount ?? _currentBallotCount);
            // _currentBallotCount = (int)encryptedBallot.CurrentNumberOfBallots;
            // return CreatedAtAction(nameof(EncryptBallot), encryptedBallot);
        }

        [HttpPost]
        [Route(nameof(EncryptBallots))]
        public ActionResult<EncryptBallotResult[]> EncryptBallots(EncryptBallotsRequest request)
        {
            var electionMap = request.ElectionMap ?? _electionMap;
            var electionGuardConfig = request.ElectionGuardConfig ?? _electionGuardConfig;
            if (electionMap == null || electionGuardConfig == null)
            {
                return BadRequest(EncryptionSetupRequiredMessage);
            }

            var currentBallotCount = request.CurrentBallotCount ?? _currentBallotCount;
            
            var result = new List<EncryptBallotResult>();

            foreach (var ballot in request.Ballots)
            {
                var selections = _electionMapper.ConvertToSelections(ballot, electionMap);
                var numberOfExpected = electionMap.BallotStyleMaps[ballot.BallotStyle.Id].ExpectedNumberOfSelected;
                var encryptedBallot = ElectionGuardApi.EncryptBallot(
                    selections, 
                    numberOfExpected, 
                    electionGuardConfig, 
                    currentBallotCount);

                currentBallotCount = (int)encryptedBallot.CurrentNumberOfBallots;
                result.Add(encryptedBallot);
            }

            _currentBallotCount = currentBallotCount;

            return CreatedAtAction(nameof(EncryptBallots), result);
        }

        [HttpPost]
        [Route(nameof(RecordBallots))]
        public ActionResult<RecordBallotsResult> RecordBallots(RecordBallotsRequest ballotsRequest)
        {
            var result = ElectionGuardApi.RecordBallots(
                ballotsRequest.ElectionGuardConfig, 
                ballotsRequest.EncryptedBallots, 
                ballotsRequest.CastBallotIndicies, 
                ballotsRequest.SpoiledBallotIndicies,
                ballotsRequest.ExportPath,
                ballotsRequest.ExportFileNamePrefix);

            return CreatedAtAction(nameof(RecordBallots), result);
        }

        [HttpPost]
        [Route(nameof(TallyVotes))]
        public ActionResult<TallyVotesResult> TallyVotes(TallyVotesRequest request)
        {

            if (request.TrusteeKeys.Count < request.ElectionGuardConfig.Threshold)
            {
                return BadRequest(ThresholdExceedsTrusteesMessage);
            }

            var result = ElectionGuardApi.TallyVotes(
                request.ElectionGuardConfig, 
                request.TrusteeKeys.Values, 
                request.TrusteeKeys.Count, 
                request.EncryptedBallotsFileName,
                request.ExportPath,
                request.ExportFileNamePrefix);

            return CreatedAtAction(nameof(TallyVotes), _electionMapper.ConvertToTally(result.TallyResults.ToArray(), request.ElectionMap));
        }
    }
}
