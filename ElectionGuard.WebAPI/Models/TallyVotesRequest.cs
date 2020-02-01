using System.Collections.Generic;
using ElectionGuard.SDK.Models;
using ElectionGuard.Tools;
using VotingWorks.Ballot;

namespace ElectionGuard.WebAPI.Models
{
    public class TallyVotesRequest
    {
    
        public IDictionary<int, string> TrusteeKeys { get; set; }

        public string RegisteredBallotsFileName { get; set; }

#nullable enable
        public Election? Election { get; set; }

        public ElectionGuardConfig? ElectionGuardConfig { get; set; }

        public ElectionMap? ElectionMap { get; set; }

        public string? ExportPath { get; set; }

        public string? ExportFileNamePrefix {get; set; }
#nullable disable

    }
}