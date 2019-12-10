namespace VotingWorks.Ballot
{
    public class CandidateContest : Contest
    {
        public CandidateContest()
        {
            Type = "candidate";
        }

        public int Seats { get; set; }
        public Candidate[] Candidates { get; set; }
        public bool AllowWriteIns { get; set; }
    }
}