using System.Linq;
using ElectionGuard.SDK;
using ElectionGuard.SDK.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using ElectionGuard.WebAPI.Models;
using System.Collections.Generic;

namespace ElectionGuard.WebAPI.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class ElectionController : ControllerBase
    {
        private readonly ILogger<ElectionController> _logger;

        public ElectionController(ILogger<ElectionController> logger)
        {
            _logger = logger;
        }

        [HttpGet]
        public string Get()
        {
            return "Welcome to ElectionGuard";
        }

        [HttpPost]
        public ActionResult<CreateElectionResult> CreateElection(ElectionRequest request)
        {
            var election = Election.CreateElection(request.Config, request.Manifest);

            return CreatedAtAction(nameof(CreateElection), election);
        }

        [HttpPost]
        [Route(nameof(EncryptBallots))]
        public ActionResult<EncryptBallotResult[]> EncryptBallots(BallotEncryptRequest request)
        {
            var currentBallotCount = 0;
            if (request.CurrentBallotCount != null) 
            {
                currentBallotCount = (int)request.CurrentBallotCount;
            } else 
            {
                //TODO: Get from lib
            }

            var result = new List<EncryptBallotResult>();

            for (var i = 0; i < request.Selections.Length; i++) 
            {
                var encryptedBallot = Election.EncryptBallot(
                    request.Selections[i], 
                    request.ExpectedNumberOfSelected, 
                    request.electionGuardConfig, 
                    currentBallotCount);

                currentBallotCount = (int)encryptedBallot.CurrentNumberOfBallots;
                result.Add(encryptedBallot);
            }

            return CreatedAtAction(nameof(EncryptBallots), result);
        }

        [HttpPost]
        [Route(nameof(RecordBallots))]
        public ActionResult<RecordBallotsResult> RecordBallots(BallotRecordRequest request)
        {
            var result = Election.RecordBallots(
                request.electionGuardConfig, 
                request.EncryptedBallots, 
                request.CastBallotIndicies, 
                request.SpoiledBallotIndicies);

            return CreatedAtAction(nameof(RecordBallots), result);
        }

        [HttpPost]
        [Route(nameof(TallyVotes))]
        public ActionResult<TallyVotesResult> TallyVotes(TallyVotesRequest request)
        {

            if (request.TrusteeKeys.Count < request.electionGuardConfig.Threshold)
            {
                return BadRequest("Trustee count is less than threshold");
            }

            var result = Election.TallyVotes(
                request.electionGuardConfig, 
                request.TrusteeKeys.Values, 
                request.TrusteeKeys.Count, 
                request.EncryptedBallotsFileName);

            return CreatedAtAction(nameof(TallyVotes), result);
        }
    }
}
