using ElectionGuard.SDK.Models;
using ElectionGuard.Tools;
using VotingWorks.Ballot;

namespace ElectionGuard.WebAPI.Models
{
    public class InitializeEncryptionRequest
    {
        public Election Election { get; set; }
        public ElectionGuardConfig ElectionGuardConfig { get; set; }
        
        public string ExportPath { get; set; }
    }
}