using System.Collections.Generic;
using VotingWorks.Ballot;

namespace ElectionGuard.Tools
{
    public class ContestMap
    {
        public Contest Contest { get; set; }
        public Dictionary<string, int> SelectionMap { get; set; }
        public int NumberOfSelections { get; set; }
        public int ExpectedNumberOfSelected { get; set; }
        public int StartIndex { get; set; }
        public int EndIndex { get; set; }
        public int WriteInStartIndex { get; set; }
        public int NullVoteStartIndex { get; set; }
    }
}