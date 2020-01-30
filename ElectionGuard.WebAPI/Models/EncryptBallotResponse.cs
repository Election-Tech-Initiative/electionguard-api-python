

namespace ElectionGuard.WebAPI.Models
{
    public class EncryptBallotResponse: EncryptedBallot
    {
        public string Tracker { get; set; }
        public long CurrentNumberOfBallots { get; set; }

#nullable enable
        public string? OutputFileName { get; set; }
#nullable disable
    }
}
