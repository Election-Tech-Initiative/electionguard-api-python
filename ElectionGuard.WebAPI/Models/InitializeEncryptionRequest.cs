using ElectionGuard.SDK.Models;
using ElectionGuard.Tools;

namespace ElectionGuard.WebAPI.Models
{
    public class InitializeEncryptionRequest
    {
        public ElectionGuardConfig ElectionGuardConfig { get; set; }
        public ElectionMap ElectionMap { get; set; }
    }
}