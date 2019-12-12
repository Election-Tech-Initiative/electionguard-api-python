using System.Collections.Generic;
using ElectionGuard.SDK.Models;
using ElectionGuard.Tools;

namespace ElectionGuard.WebAPI.Models
{
    public class TallyVotesRequest
    {
        public ElectionGuardConfig ElectionGuardConfig { get; set; }

        public ElectionMap ElectionMap { get; set; }

        public IDictionary<int, string> TrusteeKeys { get; set; }

        public string EncryptedBallotsFileName { get; set; }

#nullable enable
        public string? ExportPath { get; set; }

        public string? ExportFileNamePrefix {get; set; }
#nullable disable

    }
}