namespace VotingWorks.Ballot
{
    public interface ICandidateVoteTally
    {
        int[] Candidates { get; set; }
        WriteInCandidateTally[] WriteIns { get; set; }
    }
}