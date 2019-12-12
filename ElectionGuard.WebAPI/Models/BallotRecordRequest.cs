using ElectionGuard.SDK.Models;

namespace ElectionGuard.WebAPI.Models
{
    public class BallotRecordRequest
    {
        public ElectionGuardConfig ElectionGuardConfig { get; set; }

        public string[] EncryptedBallots { get; set; }

        public long[] CastBallotIndicies { get; set; }

        public long[] SpoiledBallotIndicies { get; set; }

#nullable enable
        public string? ExportPath { get; set; }

        public string? ExportFileNamePrefix {get; set; }
#nullable disable
    }
}