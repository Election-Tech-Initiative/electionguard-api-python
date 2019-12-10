using System.Collections.Generic;
using VotingWorks.Ballot;

namespace ElectionGuard.Tools
{
    public class ContestTally
    {
        public ContestTally(Contest contest)
        {
            Contest = contest;
            Results = new Dictionary<string, int>();
        }

        public Contest Contest { get; set; }
        public Dictionary<string, int> Results { get; set; }
    }
}