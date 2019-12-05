using ElectionGuard.SDK.Models;

namespace ElectionGuard.WebAPI.Models
{
    public class BallotEncryptRequest
    {
        public ElectionGuardConfig electionGuardConfig { get; set; }

        public bool[][] Selections { get; set; }

        public int ExpectedNumberOfSelected { get; set; }

        public int? CurrentBallotCount { get; set; }
    }
}