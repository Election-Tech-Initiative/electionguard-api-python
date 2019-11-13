using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using ElectionGuard.SDK.KeyCeremony;

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
            return "Welcome to the ElectionGuard Web API!";
        }

        [HttpPost]
        [Route("")]
        [Route("/")]
        [Route("Create")]
        // TODO: everything..
        public string Create([FromBody] object electionCreateConfig)
        {
            var testUsingSdk = new KeyCeremonyCoordinator(3, 3);
            return electionCreateConfig.ToString();
        }
    }
}
