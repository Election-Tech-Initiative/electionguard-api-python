using ElectionGuard.SDK.Models;
using ElectionGuard.Tools;
using VotingWorks.Ballot;

namespace ElectionGuard.WebAPI.Models
{
    public class EncryptBallotsRequest
    {
        public Ballot[] Ballots { get; set; }
        public int? CurrentBallotCount { get; set; }
#nullable enable
        public ElectionGuardConfig? ElectionGuardConfig { get; set; }
        public ElectionMap? ElectionMap { get; set; }
#nullable disable
    }
}