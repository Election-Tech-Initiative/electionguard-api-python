using System.Collections.Generic;

namespace VotingWorks.Ballot
{
    /// <summary>
    /// Filled out ballot for use in election
    /// Name wrapper on Completed Ballot
    /// </summary>
    public class Ballot : CompletedBallot { }

    /// <summary>
    /// Completed Ballot
    /// Exists as exact match to Voting Works implementation
    /// </summary>
    public abstract class CompletedBallot
    {
        public Election Election { get; set; }
        public BallotStyle BallotStyle { get; set; }
        public Precinct Precinct { get; set; }
        public string BallotId { get; set; }
        // Object can be Candidate[] or string of "yes" or "no"
        public Dictionary<string, object> Votes { get; set; }
        public bool IsTestBallot { get; set; }
        public BallotType BallotType { get; set; }
    }
}