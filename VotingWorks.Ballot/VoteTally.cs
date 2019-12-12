namespace VotingWorks.Ballot
{
    public class VoteTally : IYesNoVoteTally, ICandidateVoteTally
    {
        public int Yes { get; set; }
        public int No { get; set; }
        public int[] Candidates { get; set; }
        public WriteInCandidateTally[] WriteIns { get; set; }
    }
}