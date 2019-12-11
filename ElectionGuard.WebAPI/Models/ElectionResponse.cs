using ElectionGuard.SDK.Models;
using ElectionGuard.Tools;

namespace ElectionGuard.WebAPI.Models {
    public class ElectionResponse : CreateElectionResult {
        public ElectionMap ElectionMap { get; set; }
    }
}