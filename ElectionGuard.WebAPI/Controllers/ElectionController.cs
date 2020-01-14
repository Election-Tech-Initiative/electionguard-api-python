using ElectionGuard.SDK;
using ElectionGuard.SDK.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using ElectionGuard.WebAPI.Models;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using ElectionGuard.Tools;
using Newtonsoft.Json;
using VotingWorks.Ballot;

namespace ElectionGuard.WebAPI.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class ElectionController : ControllerBase
    {
        private const string WelcomeMessage = "Welcome to ElectionGuard";
        private const string FileLoadErrorMessage = "File(s) not loaded. Check file paths.";
        private const string EncryptionSetupRequiredMessage = "Encryption is not setup. Election Map and ElectionGuard Config required.";
        private const string ThresholdExceedsTrusteesMessage = "Threshold exceeds count of available trustees.";

        private readonly ILogger<ElectionController> _logger;
        private readonly IElectionMapper<Election, Ballot, VoteTally> _electionMapper;

        private static int _currentBallotCount = 0;
        private static ElectionMap _electionMap = null;
        private static ElectionGuardConfig _electionGuardConfig = null;

        public ElectionController(ILogger<ElectionController> logger, IElectionMapper<Election, Ballot, VoteTally> electionMapper)
        {
            _logger = logger;
            _electionMapper = electionMapper;
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
        public ActionResult InitializeEncryption([FromQuery] string electionMapFilePath, [FromQuery] string electionGuardConfigFilePath)
        {
            try
            {
                var electionMap = LoadJsonFile<ElectionMap>(electionMapFilePath);
                var electionGuardConfig = LoadJsonFile<ElectionGuardConfig>(electionGuardConfigFilePath);
                return InitializeEncryption(new InitializeEncryptionRequest
                {
                    ElectionMap = electionMap,
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
        public ActionResult InitializeEncryption(InitializeEncryptionRequest request)
        {
            _currentBallotCount = 0;
            _electionMap = request.ElectionMap;
            _electionGuardConfig = request.ElectionGuardConfig;
            return Ok();
        }

        [HttpPost]
        [Route(nameof(EncryptBallot))]
        public ActionResult<EncryptBallotResult> EncryptBallot(EncryptBallotRequest request)
        {
            var electionMap = request.ElectionMap ?? _electionMap;
            var electionGuardConfig = request.ElectionGuardConfig ?? _electionGuardConfig;
            if (electionMap == null || electionGuardConfig == null)
            {
                return BadRequest(EncryptionSetupRequiredMessage);
            }

            var selections = _electionMapper.ConvertToSelections(request.Ballot, electionMap);
            var numberOfExpected = electionMap.BallotStyleMaps[request.Ballot.BallotStyle.Id].ExpectedNumberOfSelected;
            var encryptedBallot = ElectionGuardApi.EncryptBallot(
                selections,
                numberOfExpected,
                electionGuardConfig,
                request.CurrentBallotCount ?? _currentBallotCount);
            _currentBallotCount = (int)encryptedBallot.CurrentNumberOfBallots;
            return CreatedAtAction(nameof(EncryptBallot), encryptedBallot);
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
