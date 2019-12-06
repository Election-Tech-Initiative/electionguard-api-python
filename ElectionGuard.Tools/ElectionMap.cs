using System;
using System.Collections.Generic;
using ElectionGuard.SDK.Models;

namespace ElectionGuard.Tools
{
    public class ElectionMap
    {
        public int NumberOfSelections { get; set; }
        public Dictionary<string, ContestMap> ContestMaps { get; set; }
        public Dictionary<string, BallotStyleMap> BallotStyleMaps { get; set; }
    }
}