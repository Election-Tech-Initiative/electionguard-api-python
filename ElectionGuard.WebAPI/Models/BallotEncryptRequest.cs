using ElectionGuard.SDK.Models;
using ElectionGuard.Tools;
using VotingWorks.Ballot;

namespace ElectionGuard.WebAPI.Models
{
    public class BallotEncryptRequest
    {
        public ElectionGuardConfig ElectionGuardConfig { get; set; }

        public ElectionMap ElectionMap { get; set; }

        public Ballot[] Ballots { get; set; }

        public int? CurrentBallotCount { get; set; }
    }
}