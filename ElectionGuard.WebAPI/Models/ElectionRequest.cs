using ElectionGuard.SDK.Models;

namespace ElectionGuard.WebAPI.Models
{
    public class ElectionRequest
    {
        public ElectionGuardConfig Config { get; set; }
        public ElectionManifest Manifest { get; set; }
    }
}