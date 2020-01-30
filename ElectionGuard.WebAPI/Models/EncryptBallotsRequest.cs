using ElectionGuard.SDK.Models;
using ElectionGuard.Tools;
using VotingWorks.Ballot;

namespace ElectionGuard.WebAPI.Models
{
    public class EncryptBallotsRequest
    {
        public Ballot[] Ballots { get; set; }
#nullable enable
        public Election? Election { get; set; }
        public ElectionGuardConfig? ElectionGuardConfig { get; set; }
        public ElectionMap? ElectionMap { get; set; }
        public string? ExportPath { get; set; }
        public string? ExportFileName { get; set; }
#nullable disable
    }
}