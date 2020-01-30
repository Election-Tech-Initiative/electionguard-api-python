using ElectionGuard.SDK.Models;

namespace ElectionGuard.WebAPI.Models
{
    public class LoadBallotsRequest
    {
        public long StartIndex { get ;set; }
        public long Count { get; set; }

        public string ImportFileName { get; set; }

        #nullable enable
        public ElectionGuardConfig? ElectionGuardConfig { get; set; }

        public string? ImportPath { get; set; }
#nullable disable
    }
}