using System.Collections.Generic;

namespace ElectionGuard.WebAPI.Models
{
    public class RecordBallotsResponse
    {
        public string RegisteredBallotsFileName { get; set; }
        public ICollection<string> CastedBallotTrackers { get; set; }
        public ICollection<string> SpoiledBallotTrackers { get; set; }
    }
}