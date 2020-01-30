using ElectionGuard.SDK.Models;

namespace ElectionGuard.WebAPI.Models
{
    public class RecordBallotsRequest
    {
        public EncryptedBallot[] Ballots { get; set; }

        public string[] CastBallotIds { get; set; }

        public string[] SpoildBallotIds { get; set; }

#nullable enable
        public ElectionGuardConfig? ElectionGuardConfig { get; set; }

        public string? ExportPath { get; set; }

        public string? ExportFileNamePrefix {get; set; }
#nullable disable
    }
}