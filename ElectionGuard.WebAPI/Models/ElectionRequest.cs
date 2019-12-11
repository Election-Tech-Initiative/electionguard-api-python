using ElectionGuard.SDK.Models;
using VotingWorks.Ballot;

namespace ElectionGuard.WebAPI.Models
{
    public class ElectionRequest
    {
        public ElectionGuardConfig Config { get; set; }
        public Election Election { get; set; }
    }
}