using System.Collections.Generic;

namespace ElectionGuard.Tools
{
    public class BallotStyleMap
    {
        public int ExpectedNumberOfSelected { get; set; }
        public Dictionary<string, ContestMap> ContestMaps { get; set; }
    }
}