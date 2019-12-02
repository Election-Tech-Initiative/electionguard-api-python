using System.Linq;
using ElectionGuard.SDK;
using ElectionGuard.SDK.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using ElectionGuard.WebAPI.Models;

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
        public ActionResult<object> CreateElection(ElectionRequest electionRequest)
        {
            var election = new Election(electionRequest.NumberOfTrustees, electionRequest.Threshold, new ElectionManifest()
            {
                Contests = new Contest[]{ new YesNoContest()
                {
                    Type = "YesNo"
                } },
            });
            return CreatedAtAction(nameof(CreateElection), new
            {
                election.NumberOfTrustees,
                election.Threshold,
                election.BaseHashCode,
                election.PublicJointKey,
                TrusteeKeys = election.TrusteeKeys.Select(x =>
                    new TrusteeKey()
                    {
                        Index = x.Key,
                        PrivateKey = x.Value
                    }).ToList()
            });
        }
    }
}
